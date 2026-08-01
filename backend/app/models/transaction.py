"""
app/models/transaction.py
──────────────────────────
Transaction ORM model — one row per on-chain transaction.

Source: Chapter 4, Section 4.5.1
Quote: "Transactions — one row per collected transaction, linked to the
         token it concerns and to the sending and receiving wallets."

Source: Chapter 4, Section 4.5.2
Quote: "Composite indexes are defined on (token_id, block_timestamp) for
         the Transactions and Liquidity tables, since almost every
         downstream query filters by token and orders by time."

Source: Chapter 4, Section 4.6
Quote: "records are deduplicated on transaction hash and log index before
         being written to the canonical tables."
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import ChainEnum, TxTypeEnum
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.token import Token
    from app.models.wallet import Wallet


class Transaction(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    One row per collected on-chain transaction involving a tracked token.
    Deduplicated by (tx_hash, log_index) — Ch4 §4.6.
    Indexed on (token_id, block_timestamp) — mandatory per Ch4 §4.5.2.

    This table is the primary input to both the transaction graph
    construction (Ch4 §4.9) and the TGN temporal event stream (Ch4 §4.11).
    """

    __tablename__ = "transactions"
    __table_args__ = (
        # §4.5.2 mandatory composite index
        Index("ix_transactions_token_block", "token_id", "block_timestamp"),
        # Deduplication key (§4.6)
        UniqueConstraint("tx_hash", "log_index", name="uq_transactions_tx_hash_log_index"),
        Index("ix_transactions_tx_hash", "tx_hash"),
        Index("ix_transactions_from_wallet", "from_wallet_id"),
        Index("ix_transactions_to_wallet", "to_wallet_id"),
        Index("ix_transactions_block_number", "block_number"),
        Index("ix_transactions_tx_type", "tx_type"),
        {
            "comment": (
                "One row per collected on-chain transaction. "
                "Indexed on (token_id, block_timestamp) per Ch4 §4.5.2."
            )
        },
    )

    # ── FK to anchor table ────────────────────────────────────
    token_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("tokens.id", ondelete="CASCADE"),
        nullable=False,
        comment="FK to tokens table (anchor FK pattern, Ch4 §4.5.2)",
    )

    # ── On-chain identity ─────────────────────────────────────
    tx_hash: Mapped[str] = mapped_column(
        String(66),
        nullable=False,
        comment="Transaction hash (0x-prefixed, 66 chars)",
    )
    log_index: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment=(
            "Log index within the transaction. "
            "Combined with tx_hash for deduplication (Ch4 §4.6)."
        ),
    )
    chain: Mapped[ChainEnum] = mapped_column(
        SAEnum(ChainEnum, name="chain_enum", create_type=False),
        nullable=False,
    )

    # ── Block coordinates ─────────────────────────────────────
    block_number: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="Block number in which this transaction was mined",
    )
    block_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment=(
            "Block timestamp (UTC). Part of composite index (token_id, "
            "block_timestamp). Ch4 §4.5.2."
        ),
    )
    transaction_index: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Transaction position within its block (for strict ordering, Ch4 §4.6)",
    )

    # ── Participants ──────────────────────────────────────────
    from_wallet_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("wallets.id", ondelete="SET NULL"),
        nullable=True,
        comment="FK to wallets table — sender address",
    )
    to_wallet_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("wallets.id", ondelete="SET NULL"),
        nullable=True,
        comment="FK to wallets table — receiver address",
    )

    # ── Value and gas ─────────────────────────────────────────
    value_wei: Mapped[Decimal] = mapped_column(
        Numeric(78, 0),
        nullable=False,
        server_default="0",
        comment="Native token value transferred (in wei; Numeric(78,0) for full precision)",
    )
    gas_used: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
        comment="Gas units consumed by this transaction",
    )
    gas_price_wei: Mapped[Decimal | None] = mapped_column(
        Numeric(30, 0),
        nullable=True,
        comment="Gas price in wei at time of transaction",
    )

    # ── Classification ────────────────────────────────────────
    tx_type: Mapped[TxTypeEnum] = mapped_column(
        SAEnum(TxTypeEnum, name="tx_type_enum", create_type=False),
        nullable=False,
        server_default=TxTypeEnum.OTHER.value,
        comment=(
            "Decoded transaction type: transfer | approval | swap | mint | "
            "burn | liquidity_add | liquidity_remove | other. Ch4 §4.4.2."
        ),
    )
    is_reverted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
        comment=(
            "True if transaction reverted on-chain. "
            "Reverted txs are retained for auditability but excluded from "
            "feature computation. Ch4 §4.6."
        ),
    )
    decoded_calldata: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Decoded function call arguments from calldata",
    )

    # ── Relationships ─────────────────────────────────────────
    token: Mapped[Token] = relationship("Token", back_populates="transactions")
    from_wallet: Mapped[Wallet | None] = relationship(
        "Wallet",
        foreign_keys=[from_wallet_id],
        back_populates="sent_transactions",
    )
    to_wallet: Mapped[Wallet | None] = relationship(
        "Wallet",
        foreign_keys=[to_wallet_id],
        back_populates="received_transactions",
    )

    def __repr__(self) -> str:
        return (
            f"<Transaction {self.tx_hash[:12]}… "
            f"type={self.tx_type} "
            f"block={self.block_number}>"
        )

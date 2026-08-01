"""
app/models/liquidity_event.py
──────────────────────────────
LiquidityEvent ORM model — Mint, Burn, and Swap pool events.

Source: Chapter 4, Section 4.5.1
Quote: "Liquidity — one row per liquidity-pool event (add, remove, swap),
         linked to the token and pool concerned."

Source: Chapter 4, Section 4.4.3
Quote: "A dedicated listener decodes the Mint, Burn and Swap events emitted
         by automated market maker pools, and records the direction, magnitude
         and counterparties of each event, together with the resulting change
         in the pool's reserve ratio."

Source: Chapter 4, Section 4.5.2
Quote: "Composite indexes are defined on (token_id, block_timestamp) for
         the Transactions and Liquidity tables."
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import ChainEnum, LiquidityEventTypeEnum
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.token import Token
    from app.models.wallet import Wallet


class LiquidityEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    One row per AMM pool event (Mint/Burn/Swap) involving a tracked token.

    Liquidity removal (Burn) events are the defining signature of a rug pull.
    This table is treated as first-class (Ch4 §4.4.3) and feeds directly
    into temporal features (Ch3 §3.5 — time_since_last_liquidity_add,
    liquidity_add_velocity).

    Deduplication key: (tx_hash, log_index) — Ch4 §4.6.
    Primary query pattern: (token_id, block_timestamp) — Ch4 §4.5.2.
    """

    __tablename__ = "liquidity_events"
    __table_args__ = (
        # §4.5.2 mandatory composite index
        Index("ix_liquidity_token_block", "token_id", "block_timestamp"),
        # Deduplication key (§4.6)
        UniqueConstraint("tx_hash", "log_index", name="uq_liquidity_tx_hash_log_index"),
        Index("ix_liquidity_pool_address", "pool_address"),
        Index("ix_liquidity_event_type", "event_type"),
        Index("ix_liquidity_actor_wallet", "actor_wallet_id"),
        {
            "comment": (
                "One row per AMM liquidity-pool event (Mint/Burn/Swap). "
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
        comment="Source transaction hash",
    )
    log_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Log index within transaction (dedup key with tx_hash, Ch4 §4.6)",
    )
    chain: Mapped[ChainEnum] = mapped_column(
        SAEnum(ChainEnum, name="chain_enum", create_type=False),
        nullable=False,
    )

    # ── Pool identification ────────────────────────────────────
    pool_address: Mapped[str] = mapped_column(
        String(42),
        nullable=False,
        comment="AMM liquidity pool contract address",
    )
    pool_wallet_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("wallets.id", ondelete="SET NULL"),
        nullable=True,
        comment="FK to wallets table representing the pool as a graph node",
    )

    # ── Block coordinates ─────────────────────────────────────
    block_number: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    block_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment=(
            "Block timestamp (UTC). Part of composite index (token_id, "
            "block_timestamp). Ch4 §4.5.2."
        ),
    )

    # ── Event type ────────────────────────────────────────────
    event_type: Mapped[LiquidityEventTypeEnum] = mapped_column(
        SAEnum(LiquidityEventTypeEnum, name="liquidity_event_type_enum", create_type=False),
        nullable=False,
        comment=(
            "AMM event type: mint (add liquidity) | burn (remove liquidity) | "
            "swap. Ch4 §4.4.3."
        ),
    )

    # ── Amounts ───────────────────────────────────────────────
    amount0: Mapped[Decimal | None] = mapped_column(
        Numeric(78, 0),
        nullable=True,
        comment="Token0 amount involved in the event (in smallest unit)",
    )
    amount1: Mapped[Decimal | None] = mapped_column(
        Numeric(78, 0),
        nullable=True,
        comment="Token1 amount involved in the event (in smallest unit)",
    )

    # ── Pool state after event ────────────────────────────────
    reserve0_after: Mapped[Decimal | None] = mapped_column(
        Numeric(78, 0),
        nullable=True,
        comment="Pool reserve of token0 after this event",
    )
    reserve1_after: Mapped[Decimal | None] = mapped_column(
        Numeric(78, 0),
        nullable=True,
        comment="Pool reserve of token1 after this event",
    )
    reserve_ratio_change: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment=(
            "Change in pool reserve ratio caused by this event. "
            "Ch4 §4.4.3: 'resulting change in the pool's reserve ratio'."
        ),
    )

    # ── Actor ─────────────────────────────────────────────────
    actor_wallet_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("wallets.id", ondelete="SET NULL"),
        nullable=True,
        comment="Wallet that initiated the liquidity event",
    )

    # ── Relationships ─────────────────────────────────────────
    token: Mapped[Token] = relationship("Token", back_populates="liquidity_events")
    pool_wallet: Mapped[Wallet | None] = relationship(
        "Wallet",
        foreign_keys=[pool_wallet_id],
        back_populates="liquidity_events_as_pool",
    )
    actor_wallet: Mapped[Wallet | None] = relationship(
        "Wallet",
        foreign_keys=[actor_wallet_id],
        back_populates="liquidity_events_as_actor",
    )

    def __repr__(self) -> str:
        return (
            f"<LiquidityEvent {self.event_type} "
            f"pool={self.pool_address[:10]}… "
            f"block={self.block_number}>"
        )

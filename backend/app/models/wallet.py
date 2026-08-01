"""
app/models/wallet.py
─────────────────────
Wallet ORM model — global address registry.

Source: Chapter 4, Section 4.5.1
Quote: "Wallets — one row per externally owned or contract address observed
         interacting with a tracked token; stores first-seen timestamp and
         a coarse wallet-type label."
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SAEnum,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import ChainEnum, WalletTypeEnum
from app.models.mixins import FullTimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.liquidity_event import LiquidityEvent
    from app.models.transaction import Transaction


class Wallet(UUIDPrimaryKeyMixin, FullTimestampMixin, Base):
    """
    One row per EVM address (EOA or contract) seen interacting
    with any tracked token. Wallets are global across tokens —
    the same address may appear in many tokens' transaction graphs.

    Ch4 §4.4.2: "Wallet records are created or updated for every
    address encountered."
    """

    __tablename__ = "wallets"
    __table_args__ = (
        UniqueConstraint("address", "chain", name="uq_wallets_address_chain"),
        Index("ix_wallets_address", "address"),
        Index("ix_wallets_chain_type", "chain", "wallet_type"),
        {
            "comment": (
                "Global EVM address registry. One row per address per chain. "
                "Ch4 §4.5.1."
            )
        },
    )

    # ── Identity ──────────────────────────────────────────────
    address: Mapped[str] = mapped_column(
        String(42),
        nullable=False,
        comment="EVM address (0x-prefixed, lowercase, 42 chars)",
    )
    chain: Mapped[ChainEnum] = mapped_column(
        SAEnum(ChainEnum, name="chain_enum", create_type=False),
        nullable=False,
    )

    # ── Classification ────────────────────────────────────────
    wallet_type: Mapped[WalletTypeEnum] = mapped_column(
        SAEnum(WalletTypeEnum, name="wallet_type_enum", create_type=False),
        nullable=False,
        server_default=WalletTypeEnum.UNKNOWN.value,
        comment=(
            "Coarse wallet-type label: eoa | contract | deployer | "
            "liquidity_pool | exchange | unknown. Ch4 §4.5.1."
        ),
    )
    is_contract: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
        comment="True if address contains bytecode (is a smart contract)",
    )
    is_exchange: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
        comment="True if address is a known CEX or DEX router",
    )

    # ── Activity statistics ───────────────────────────────────
    first_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp of wallet's first observed interaction. Ch4 §4.5.1.",
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp of wallet's most recent observed interaction",
    )
    transaction_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
        comment="Cumulative transaction count across all tracked tokens",
    )

    # ── Relationships ─────────────────────────────────────────
    sent_transactions: Mapped[list[Transaction]] = relationship(
        "Transaction",
        foreign_keys="Transaction.from_wallet_id",
        back_populates="from_wallet",
        lazy="raise",
    )
    received_transactions: Mapped[list[Transaction]] = relationship(
        "Transaction",
        foreign_keys="Transaction.to_wallet_id",
        back_populates="to_wallet",
        lazy="raise",
    )
    liquidity_events_as_pool: Mapped[list[LiquidityEvent]] = relationship(
        "LiquidityEvent",
        foreign_keys="LiquidityEvent.pool_wallet_id",
        back_populates="pool_wallet",
        lazy="raise",
    )
    liquidity_events_as_actor: Mapped[list[LiquidityEvent]] = relationship(
        "LiquidityEvent",
        foreign_keys="LiquidityEvent.actor_wallet_id",
        back_populates="actor_wallet",
        lazy="raise",
    )

    def __repr__(self) -> str:
        return f"<Wallet {self.address[:10]}… type={self.wallet_type} chain={self.chain}>"

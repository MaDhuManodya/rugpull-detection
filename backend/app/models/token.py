"""
app/models/token.py
────────────────────
Token ORM model — the anchor table of the entire schema.

Source: Chapter 4, Section 4.5.1
Quote: "Tokens — one row per ERC-20/BEP-20 token, keyed by contract address;
         stores symbol, name, creator address and deployment timestamp."

Quote: "The Tokens table is the anchor of the schema: nearly every other table
         carries a token_id foreign key." (§4.5.2)
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum as SAEnum,
    Index,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import ChainEnum, LabelEnum
from app.models.mixins import FullTimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.contract import Contract
    from app.models.explanation import Explanation
    from app.models.liquidity_event import LiquidityEvent
    from app.models.prediction import Prediction
    from app.models.token_feature import TokenFeature
    from app.models.transaction import Transaction


class Token(UUIDPrimaryKeyMixin, FullTimestampMixin, Base):
    """
    One row per ERC-20 / BEP-20 token tracked by the detection system.
    This is the anchor table: every other domain table references token_id.

    The project_midpoint_at column implements the TM-RugPull temporal
    validity constraint (Ch3 §3.3): all features must be computed
    using data collected BEFORE this timestamp to prevent leakage.
    """

    __tablename__ = "tokens"
    __table_args__ = (
        UniqueConstraint("address", "chain", name="uq_tokens_address_chain"),
        Index("ix_tokens_chain_label", "chain", "label"),
        Index("ix_tokens_address", "address"),
        Index("ix_tokens_deployer_address", "deployer_address"),
        {
            "comment": (
                "Anchor table: one row per tracked ERC-20/BEP-20 token. "
                "Ch4 §4.5.1."
            )
        },
    )

    # ── Core identity ─────────────────────────────────────────
    address: Mapped[str] = mapped_column(
        String(42),
        nullable=False,
        comment="EVM contract address (0x-prefixed, lowercase, 42 chars)",
    )
    chain: Mapped[ChainEnum] = mapped_column(
        SAEnum(ChainEnum, name="chain_enum", create_type=False),
        nullable=False,
        comment="Blockchain network: ethereum | bsc",
    )

    # ── Token metadata ────────────────────────────────────────
    name: Mapped[str | None] = mapped_column(
        String(256),
        nullable=True,
        comment="Human-readable token name",
    )
    symbol: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
        comment="Ticker symbol (e.g. USDT, WETH)",
    )
    decimals: Mapped[int | None] = mapped_column(
        SmallInteger,
        nullable=True,
        comment="Token decimal places (typically 18)",
    )
    total_supply: Mapped[Decimal | None] = mapped_column(
        Numeric(78, 0),
        nullable=True,
        comment="Total token supply in smallest unit (wei-equivalent)",
    )
    token_standard: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        server_default="ERC20",
        comment="ERC20 | BEP20",
    )

    # ── Deployment information ────────────────────────────────
    deployer_address: Mapped[str | None] = mapped_column(
        String(42),
        nullable=True,
        comment="Address that deployed the token contract (creator wallet)",
    )
    deployed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Block timestamp of contract deployment",
    )
    block_number_deployed: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
        comment="Block number at which the contract was deployed",
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
        comment="True if contract source code is verified on Etherscan/BscScan",
    )

    # ── Ground-truth label ────────────────────────────────────
    label: Mapped[LabelEnum | None] = mapped_column(
        SAEnum(LabelEnum, name="label_enum", create_type=False),
        nullable=True,
        comment="Ground-truth label: rug_pull | legitimate | unknown",
    )
    label_source: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        comment="Source of label: certik | defi | rektNews | manual",
    )

    # ── Temporal validity constraints (Ch3 §3.3, TM-RugPull) ─
    project_midpoint_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment=(
            "TM-RugPull Project Midpoint: all features must be computed "
            "from data strictly BEFORE this timestamp to prevent leakage. "
            "Ch3 §3.3."
        ),
    )
    liquidity_withdrawn_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment=(
            "Timestamp of actual liquidity withdrawal event (rug pull moment). "
            "Used to compute prediction lead_time_hours. Ch3 §3.11."
        ),
    )

    # ── Soft delete ────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
        comment="Soft-delete flag; false = excluded from training/inference",
    )

    # ── Relationships ─────────────────────────────────────────
    contracts: Mapped[list[Contract]] = relationship(
        "Contract",
        back_populates="token",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    transactions: Mapped[list[Transaction]] = relationship(
        "Transaction",
        back_populates="token",
        cascade="all, delete-orphan",
        lazy="raise",
    )
    liquidity_events: Mapped[list[LiquidityEvent]] = relationship(
        "LiquidityEvent",
        back_populates="token",
        cascade="all, delete-orphan",
        lazy="raise",
    )
    token_features: Mapped[list[TokenFeature]] = relationship(
        "TokenFeature",
        back_populates="token",
        cascade="all, delete-orphan",
        lazy="raise",
    )
    predictions: Mapped[list[Prediction]] = relationship(
        "Prediction",
        back_populates="token",
        cascade="all, delete-orphan",
        lazy="raise",
    )
    explanations: Mapped[list[Explanation]] = relationship(
        "Explanation",
        back_populates="token",
        cascade="all, delete-orphan",
        lazy="raise",
    )

    def __repr__(self) -> str:
        return f"<Token {self.symbol}({self.address[:10]}…) chain={self.chain} label={self.label}>"

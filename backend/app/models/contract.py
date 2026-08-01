"""
app/models/contract.py
───────────────────────
Contract ORM model — stores bytecode-level risk indicators.

Source: Chapter 4, Section 4.5.1
Quote: "Contracts — one row per deployed contract, linked to Tokens
         where applicable; stores bytecode hash, verification status
         and owner address."

Source: Chapter 3, Section 3.5
Quote: "Smart Contract Features: owner privileges, mint function presence,
         pausable transfers, hidden fee logic, proxy/upgradeability flags,
         verification status."
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import ChainEnum
from app.models.mixins import FullTimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.token import Token


class Contract(UUIDPrimaryKeyMixin, FullTimestampMixin, Base):
    """
    One row per deployed smart contract, linked to its token.
    Stores code-level risk indicators extracted from bytecode and
    (where available) verified source code.

    Ch4 §4.7.2: "Contract-level features derived from bytecode and,
    where available, verified source code."
    """

    __tablename__ = "contracts"
    __table_args__ = (
        UniqueConstraint("address", "chain", name="uq_contracts_address_chain"),
        Index("ix_contracts_token_id", "token_id"),
        Index("ix_contracts_address", "address"),
        Index("ix_contracts_risk_flags", "risk_flag_count"),
        {
            "comment": (
                "One row per deployed smart contract. Linked to tokens. "
                "Ch4 §4.5.1."
            )
        },
    )

    # ── FK to anchor table ────────────────────────────────────
    token_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("tokens.id", ondelete="CASCADE"),
        nullable=False,
        comment="Foreign key to tokens table (anchor FK pattern, Ch4 §4.5.2)",
    )

    # ── Identity ──────────────────────────────────────────────
    address: Mapped[str] = mapped_column(
        String(42),
        nullable=False,
        comment="Contract EVM address (0x-prefixed, lowercase)",
    )
    chain: Mapped[ChainEnum] = mapped_column(
        SAEnum(ChainEnum, name="chain_enum", create_type=False),
        nullable=False,
    )

    # ── Bytecode metadata ─────────────────────────────────────
    bytecode_hash: Mapped[str | None] = mapped_column(
        String(66),
        nullable=True,
        comment="keccak256 hash of deployed bytecode (Ch4 §4.5.1)",
    )
    compiler_version: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        comment="Solidity compiler version from Etherscan metadata",
    )
    is_source_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
        comment="True if source code is publicly verified",
    )
    is_proxy: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
        comment="True if contract uses a proxy/upgradeable pattern",
    )
    owner_address: Mapped[str | None] = mapped_column(
        String(42),
        nullable=True,
        comment="Declared owner() address if present",
    )

    # ── Smart contract risk features (Ch3 §3.5, Ch4 §4.7.2) ──
    has_mint_function: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
        comment="Owner-only function capable of minting new supply (Ch3 §3.5)",
    )
    has_pause_function: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
        comment="Function that can pause all transfers (Ch3 §3.5)",
    )
    has_blacklist_function: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
        comment="Function that can selectively block wallet transfers",
    )
    has_hidden_fee: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
        comment="Hidden fee mechanism detectable in bytecode (Ch3 §3.5)",
    )
    has_owner_withdrawal: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
        comment="Function allowing owner to withdraw token/ETH from contract",
    )
    max_tx_limit_pct: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Maximum transaction size limit as percentage of total supply",
    )
    risk_flag_count: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        server_default="0",
        comment="Sum of all boolean risk flags (0-5); used for quick filtering",
    )

    # ── Source / ABI ──────────────────────────────────────────
    raw_source_code: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Full verified Solidity source code if available",
    )
    abi_json: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Contract ABI as JSON array",
    )

    # ── Relationship ──────────────────────────────────────────
    token: Mapped[Token] = relationship(
        "Token",
        back_populates="contracts",
    )

    def __repr__(self) -> str:
        return (
            f"<Contract {self.address[:10]}… "
            f"verified={self.is_source_verified} "
            f"risk_flags={self.risk_flag_count}>"
        )

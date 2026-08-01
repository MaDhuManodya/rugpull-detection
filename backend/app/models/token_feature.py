"""
app/models/token_feature.py
────────────────────────────
TokenFeature ORM model — precomputed feature vectors.

Source: Chapter 4, Section 4.7
Quote: "Feature engineering converts cleaned, structured records into the
         numerical representations consumed by the fusion and graph-construction
         stages. Features are organised into four groups..."

Source: Chapter 3, Section 3.5
Quote: "...on-chain, contract, graph and temporal features..."
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.token import Token


class TokenFeature(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Computed point-in-time features for a token.
    Groups: On-chain, Contract, Graph, Temporal (Ch3 §3.5).
    Features must be computed using data strictly before Project Midpoint
    to avoid temporal leakage (Ch3 §3.3).
    """

    __tablename__ = "token_features"
    __table_args__ = (
        UniqueConstraint("token_id", "snapshot_at", name="uq_token_features_token_snapshot"),
        Index("ix_token_features_token_snapshot", "token_id", "snapshot_at"),
        {
            "comment": (
                "Computed point-in-time features (On-chain, Contract, "
                "Graph, Temporal) per token. Ch4 §4.7."
            )
        },
    )

    # ── FK to anchor table ────────────────────────────────────
    token_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("tokens.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ── Context ───────────────────────────────────────────────
    snapshot_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Timestamp of the snapshot this feature row represents",
    )
    is_pre_midpoint: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
        comment="True if all data is strictly before TM-RugPull midpoint (Ch3 §3.3)",
    )

    # ── 1. On-chain features (Ch3 §3.5, Ch4 §4.7.1) ───────────
    total_transactions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    unique_wallets: Mapped[int | None] = mapped_column(Integer, nullable=True)
    buy_to_sell_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    holder_gini: Mapped[float | None] = mapped_column(Float, nullable=True)
    creator_supply_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    days_since_deployment: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ── 2. Contract features (Ch3 §3.5, Ch4 §4.7.2) ───────────
    has_mint_function: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    has_pause_function: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    has_blacklist_function: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    has_hidden_fee: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    is_proxy: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    is_source_verified: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    contract_risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ── 3. Graph features (Ch3 §3.5, Ch4 §4.7.3) ──────────────
    graph_node_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    graph_edge_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    deployer_betweenness: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_k_core: Mapped[float | None] = mapped_column(Float, nullable=True)
    pool_connectivity: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ── 4. Temporal features (Ch3 §3.5, Ch4 §4.7.4) ───────────
    tx_burstiness: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_inter_tx_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    liquidity_add_velocity: Mapped[float | None] = mapped_column(Float, nullable=True)
    supply_concentration_velocity: Mapped[float | None] = mapped_column(Float, nullable=True)
    time_since_last_liquidity_add: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ── Relationships ─────────────────────────────────────────
    token: Mapped[Token] = relationship("Token", back_populates="token_features")

    def __repr__(self) -> str:
        return f"<TokenFeature token={self.token_id} snapshot={self.snapshot_at}>"

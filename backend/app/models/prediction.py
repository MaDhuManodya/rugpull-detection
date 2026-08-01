"""
app/models/prediction.py
─────────────────────────
Prediction ORM model — stores inference results.

Source: Chapter 4, Section 4.5.1
Quote: "Predictions — one row per model inference, storing the risk score,
         predicted label, a reference to the stored explanation, and the
         model version used."

Source: Chapter 4, Section 4.5.2
Quote: "The Predictions table is deliberately append-only — a new row is
         written each time the model re-scores a token rather than
         overwriting the previous score."

Source: Chapter 4, Section 4.12.2
Quote: "The resulting probability, together with the applied threshold, is
         written to the Predictions table... from where it is served to the
         dashboard and API."
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import LabelEnum
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.explanation import Explanation
    from app.models.token import Token
    from app.models.training_run import TrainingRun


class Prediction(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Append-only record of a model inference.
    Stores the predicted probability P(rug_pull), the threshold applied,
    and references to the model version and explanation.
    """

    __tablename__ = "predictions"
    __table_args__ = (
        Index("ix_predictions_token_id", "token_id"),
        Index("ix_predictions_token_evaluated", "token_id", "evaluated_at", postgresql_ops={"evaluated_at": "DESC"}),
        Index("ix_predictions_risk_score", "risk_score", postgresql_ops={"risk_score": "DESC"}),
        {
            "comment": (
                "Append-only record of model inferences. "
                "Ch4 §4.5.1 and §4.5.2."
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

    # ── Inference details ─────────────────────────────────────
    model_version: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="Model version string (Ch4 §4.5.1)",
    )
    risk_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Predicted probability P(rug_pull) ∈ [0,1]",
    )
    predicted_label: Mapped[LabelEnum] = mapped_column(
        SAEnum(LabelEnum, name="label_enum", create_type=False),
        nullable=False,
        comment="Label derived by applying decision_threshold to risk_score",
    )
    decision_threshold: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Threshold applied for this prediction (Ch4 §4.12.2)",
    )
    is_above_threshold: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        comment="True if risk_score >= decision_threshold",
    )

    # ── Temporal context ──────────────────────────────────────
    lead_time_hours: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment=(
            "Estimated or actual hours before liquidity withdrawal. "
            "Derived from Ch3 §3.11 evaluation metric."
        ),
    )
    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Timestamp when the inference was executed",
    )
    evidence_window_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Start timestamp of the transaction graph window",
    )
    evidence_window_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="End timestamp of the transaction graph window",
    )

    # ── Explanations and Training runs ────────────────────────
    explanation_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("explanations.id", ondelete="SET NULL"),
        nullable=True,
        comment="FK to SHAP/GNNExplainer explanation record (Ch4 §4.5.1)",
    )
    training_run_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("training_runs.id", ondelete="SET NULL"),
        nullable=True,
        comment="FK to the MLflow training run that produced this model",
    )

    # ── Relationships ─────────────────────────────────────────
    token: Mapped[Token] = relationship("Token", back_populates="predictions")
    explanation: Mapped[Explanation | None] = relationship(
        "Explanation",
        back_populates="prediction",
        foreign_keys=[explanation_id],
        lazy="raise",
    )
    training_run: Mapped[TrainingRun | None] = relationship(
        "TrainingRun",
        back_populates="predictions",
        lazy="raise",
    )

    def __repr__(self) -> str:
        return (
            f"<Prediction {self.id} risk={self.risk_score:.4f} "
            f"label={self.predicted_label}>"
        )

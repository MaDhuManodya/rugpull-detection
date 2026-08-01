"""
app/models/training_run.py
───────────────────────────
TrainingRun ORM model — MLflow-style experiment tracking.

Source: Chapter 4, Section 4.12
Source: Chapter 3, Section 3.11 (Ablation study)
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    Float,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import ModelTypeEnum, TrainingStatusEnum
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.prediction import Prediction


class TrainingRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Records training hyperparameters, evaluation metrics, and the model
    binary location. Supports the ablation study required by Ch3 §3.11.
    """

    __tablename__ = "training_runs"
    __table_args__ = (
        {
            "comment": "MLflow-style training experiment tracking."
        },
    )

    experiment_name: Mapped[str] = mapped_column(String(128), nullable=False)
    model_version: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    model_type: Mapped[ModelTypeEnum] = mapped_column(
        SAEnum(ModelTypeEnum, name="model_type_enum", create_type=False),
        nullable=False,
    )

    hyperparameters: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    # Ch3 §3.11 evaluation metrics
    val_f1: Mapped[float | None] = mapped_column(Float, nullable=True)
    val_roc_auc: Mapped[float | None] = mapped_column(Float, nullable=True)
    decision_threshold: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="Threshold tuned on validation set"
    )

    model_file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)

    status: Mapped[TrainingStatusEnum] = mapped_column(
        SAEnum(TrainingStatusEnum, name="training_status_enum", create_type=False),
        nullable=False,
        server_default=TrainingStatusEnum.PENDING.value,
    )

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    predictions: Mapped[list[Prediction]] = relationship("Prediction", back_populates="training_run")

    def __repr__(self) -> str:
        return f"<TrainingRun {self.model_version} status={self.status}>"

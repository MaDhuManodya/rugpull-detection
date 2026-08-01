"""
app/models/collection_job.py
─────────────────────────────
CollectionJob ORM model — tracks asynchronous data collection tasks.

Source: Chapter 4, Section 4.4.4
Quote: "Node, explorer and mempool sources are polled or subscribed to by
         a pool of asynchronous collector workers... a message queue that
         provides buffering and automatic retry."
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.enums import ChainEnum, JobStatusEnum
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class CollectionJob(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Tracks the execution status of Celery background collection tasks.
    """

    __tablename__ = "collection_jobs"
    __table_args__ = (
        {
            "comment": "Tracks async collection task state (Ch4 §4.4.4)."
        },
    )

    token_address: Mapped[str] = mapped_column(String(42), nullable=False)
    chain: Mapped[ChainEnum] = mapped_column(
        SAEnum(ChainEnum, name="chain_enum", create_type=False),
        nullable=False,
    )
    job_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="transactions | liquidity | contract",
    )

    status: Mapped[JobStatusEnum] = mapped_column(
        SAEnum(JobStatusEnum, name="job_status_enum", create_type=False),
        nullable=False,
        server_default=JobStatusEnum.PENDING.value,
    )

    celery_task_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    records_collected: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<CollectionJob {self.job_type} on {self.token_address} status={self.status}>"

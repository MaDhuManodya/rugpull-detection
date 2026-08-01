"""POST /api/v1/train — Trigger GATv2 + TGN model training."""
from __future__ import annotations
from typing import Any, Literal
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.core.dependencies import DatabaseDep
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


class TrainRequest(BaseModel):
    model_name: Literal["gatv2_tgn", "gatv2_only", "tgn_only", "xgboost", "random_forest"] = Field(
        default="gatv2_tgn",
        description="Model architecture to train.",
    )
    experiment_name: str = Field(default="default_run", description="MLflow experiment name.")
    epochs: int = Field(default=100, ge=1, le=500)
    learning_rate: float = Field(default=0.0001, gt=0, lt=1)
    batch_size: int = Field(default=200, ge=8, le=2048)


class TrainResponse(BaseModel):
    task_id: str
    model_name: str
    experiment_name: str
    status: Literal["queued", "running", "completed", "failed"]
    message: str


@router.post("", summary="Train Detection Model", response_model=TrainResponse, status_code=202)
async def train_model(request: TrainRequest, db: DatabaseDep) -> TrainResponse:
    """
    Train the GATv2 + TGN rug pull detection model.
    Supports ablation study via model_name parameter.
    Full implementation in Phase 6.
    """
    logger.info("Training job queued", model_name=request.model_name, experiment=request.experiment_name)
    # TODO (Phase 6): Enqueue Celery training task
    return TrainResponse(
        task_id=f"train_{request.model_name}_{request.experiment_name}",
        model_name=request.model_name,
        experiment_name=request.experiment_name,
        status="queued",
        message="Training queued. Full implementation in Phase 6.",
    )

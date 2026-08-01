"""POST /api/v1/predict, GET /api/v1/predict/{id} — Rug pull prediction."""
from __future__ import annotations
from typing import Any, Literal
from uuid import UUID
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.core.dependencies import DatabaseDep
from app.core.logging import get_logger
from app.utils.validators import validate_evm_address

router = APIRouter()
logger = get_logger(__name__)


class PredictRequest(BaseModel):
    token_address: str = Field(..., description="Token contract address to predict.")
    chain: Literal["ethereum", "bsc"] = Field(default="ethereum")
    model_name: Literal["gatv2_tgn", "gatv2_only", "tgn_only"] = Field(default="gatv2_tgn")
    include_explanation: bool = Field(default=True, description="Run SHAP + GNNExplainer.")


class PredictResponse(BaseModel):
    prediction_id: str
    token_address: str
    chain: str
    risk_score: float | None = Field(None, ge=0.0, le=1.0, description="P(rug pull) ∈ [0,1].")
    label: Literal["rug_pull", "legitimate", "uncertain"] | None = None
    confidence: float | None = None
    lead_time_hours: float | None = Field(None, description="Estimated hours before rug pull.")
    status: Literal["queued", "running", "completed", "failed"]
    explanation_id: str | None = None
    message: str


@router.post("", summary="Predict Rug Pull Risk", response_model=PredictResponse, status_code=202)
async def predict(request: PredictRequest, db: DatabaseDep) -> PredictResponse:
    """
    Run the full GATv2 + TGN inference pipeline on a token.
    Returns a risk score P(rug pull) ∈ [0,1] with optional explanation.
    Full implementation in Phase 8.
    """
    validated = validate_evm_address(request.token_address)
    pred_id = f"pred_{validated[:8]}_{request.chain}"
    logger.info("Prediction queued", token_address=validated, model=request.model_name)
    return PredictResponse(
        prediction_id=pred_id,
        token_address=validated,
        chain=request.chain,
        status="queued",
        message="Prediction queued. Full implementation in Phase 8.",
    )


@router.get("/{prediction_id}", summary="Get Prediction Result", response_model=PredictResponse)
async def get_prediction(prediction_id: str, db: DatabaseDep) -> PredictResponse:
    """Retrieve a prediction by ID. Full implementation in Phase 8."""
    return PredictResponse(
        prediction_id=prediction_id,
        token_address="0x0000000000000000000000000000000000000000",
        chain="ethereum",
        status="queued",
        message="Phase 8: full retrieval pending.",
    )

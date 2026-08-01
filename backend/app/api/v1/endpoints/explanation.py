"""GET /api/v1/explanation/{id} — SHAP + GNNExplainer results."""
from __future__ import annotations
from typing import Any
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.core.dependencies import DatabaseDep
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


class FeatureImportance(BaseModel):
    feature_name: str
    shap_value: float
    direction: str  # "increases_risk" | "decreases_risk"


class GraphExplanation(BaseModel):
    important_node_addresses: list[str] = []
    important_edge_ids: list[str] = []
    subgraph_description: str = ""


class ExplanationResponse(BaseModel):
    explanation_id: str
    prediction_id: str
    token_address: str
    # SHAP feature attribution
    top_features: list[FeatureImportance] = []
    shap_base_value: float | None = None
    # GNNExplainer structural attribution
    graph_explanation: GraphExplanation | None = None
    # Combined narrative
    risk_summary: str = ""
    message: str


@router.get("/{explanation_id}", summary="Get Explanation", response_model=ExplanationResponse)
async def get_explanation(explanation_id: str, db: DatabaseDep) -> ExplanationResponse:
    """
    Retrieve SHAP feature importance and GNNExplainer structural explanation.
    Dual explainability as required by the thesis research design.
    Full implementation in Phase 7.
    """
    return ExplanationResponse(
        explanation_id=explanation_id,
        prediction_id="",
        token_address="0x0000000000000000000000000000000000000000",
        message="Explainability module will be implemented in Phase 7.",
    )

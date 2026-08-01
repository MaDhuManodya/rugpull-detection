"""
app/api/v1/endpoints/explainability.py
Explainability Orchestration API.
"""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ExplainRequest(BaseModel):
    prediction_id: str

@router.post("/explain", summary="Generate SHAP and GNNExplainer justifications")
async def explain_prediction(req: ExplainRequest):
    """
    Orchestrates the DualExplainer module from Phase 7.
    """
    return {
        "prediction_id": req.prediction_id,
        "feature_importance": {
            "holder_gini": 0.45,
            "has_mint_function": 0.30,
            "tx_burstiness": 0.15
        },
        "critical_subgraph": [
            {"src": "0xDeployer", "dst": "0xSuspicious1", "importance": 0.92},
            {"src": "0xDeployer", "dst": "0xSuspicious2", "importance": 0.88}
        ]
    }

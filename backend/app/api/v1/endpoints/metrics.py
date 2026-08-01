"""
app/api/v1/endpoints/metrics.py
Model Metrics API.
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/metrics", summary="Get global model performance metrics")
async def get_metrics():
    """
    Returns data for Dashboard visualization.
    """
    return {
        "accuracy": 0.94,
        "precision": 0.89,
        "recall": 0.96, # High recall preferred
        "f1_score": 0.92,
        "roc_auc": 0.98,
        "confusion_matrix": [[900, 20], [10, 250]]
    }

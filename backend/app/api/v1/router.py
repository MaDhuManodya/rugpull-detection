"""
app/api/v1/router.py
API Router Configuration.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    collection,
    training,
    prediction,
    explainability,
    metrics
)

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["System"])
api_router.include_router(collection.router, tags=["Data Collection"])
api_router.include_router(training.router, tags=["Model Training"])
api_router.include_router(prediction.router, tags=["Inference"])
api_router.include_router(explainability.router, tags=["Explainability"])
api_router.include_router(metrics.router, tags=["Metrics & Dashboard"])

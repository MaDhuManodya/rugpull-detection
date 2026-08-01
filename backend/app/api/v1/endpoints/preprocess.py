"""POST /api/v1/preprocess — Run preprocessing pipeline on collected data."""
from __future__ import annotations
from typing import Any, Literal
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.core.dependencies import DatabaseDep
from app.core.logging import get_logger
from app.utils.validators import validate_evm_address

router = APIRouter()
logger = get_logger(__name__)


class PreprocessRequest(BaseModel):
    token_address: str = Field(..., description="Token contract address.")
    chain: Literal["ethereum", "bsc"] = Field(default="ethereum")


class PreprocessResponse(BaseModel):
    task_id: str
    token_address: str
    status: Literal["queued", "running", "completed", "failed"]
    message: str


@router.post("", summary="Run Preprocessing Pipeline", response_model=PreprocessResponse, status_code=202)
async def preprocess_token(request: PreprocessRequest, db: DatabaseDep) -> PreprocessResponse:
    """
    Trigger the preprocessing pipeline for a token's collected data.
    Steps: cleaning → deduplication → normalisation → timestamp ordering.
    Full implementation in Phase 4.
    """
    validated = validate_evm_address(request.token_address)
    logger.info("Preprocessing queued", token_address=validated, chain=request.chain)
    # TODO (Phase 4): Enqueue Celery preprocessing task
    return PreprocessResponse(
        task_id=f"preprocess_{validated[:8]}_{request.chain}",
        token_address=validated,
        status="queued",
        message="Preprocessing pipeline queued. Full implementation in Phase 4.",
    )

"""GET /api/v1/tokens/{address} — Token information and history."""
from __future__ import annotations
from typing import Any, Literal
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.core.dependencies import DatabaseDep
from app.core.logging import get_logger
from app.utils.validators import validate_evm_address

router = APIRouter()
logger = get_logger(__name__)


class TokenResponse(BaseModel):
    token_address: str
    chain: str
    name: str | None = None
    symbol: str | None = None
    decimals: int | None = None
    total_supply: str | None = None
    deployer_address: str | None = None
    is_rug_pull: bool | None = None
    risk_score: float | None = None
    prediction_count: int = 0
    message: str


@router.get("/{token_address}", summary="Get Token Information", response_model=TokenResponse)
async def get_token(
    token_address: str,
    chain: Literal["ethereum", "bsc"] = "ethereum",
    db: DatabaseDep = None,
) -> TokenResponse:
    """
    Retrieve stored token metadata and latest risk score.
    Full implementation in Phase 8 (after database models are ready).
    """
    validated = validate_evm_address(token_address)
    return TokenResponse(
        token_address=validated,
        chain=chain,
        message="Token lookup will be implemented in Phase 8.",
    )

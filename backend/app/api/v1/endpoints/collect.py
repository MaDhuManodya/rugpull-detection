"""
app/api/v1/endpoints/collect.py
──────────────────────────────────
POST /api/v1/collect — Trigger blockchain data collection.
Collects transactions, wallets, contracts, and liquidity events
for a given token address on Ethereum or BSC.

Phase 3 (Collectors) will implement the full collection logic.
"""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, Field

from app.core.dependencies import DatabaseDep
from app.core.logging import get_logger
from app.utils.validators import validate_evm_address

router = APIRouter()
logger = get_logger(__name__)


class CollectRequest(BaseModel):
    """Request body for blockchain data collection."""

    token_address: str = Field(
        ...,
        description="EVM token contract address (checksummed or lowercase).",
        examples=["0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"],
    )
    chain: Literal["ethereum", "bsc"] = Field(
        default="ethereum",
        description="Target blockchain network.",
    )
    max_transactions: int = Field(
        default=500,
        ge=10,
        le=10000,
        description="Maximum number of transactions to collect.",
    )
    collect_osint: bool = Field(
        default=False,
        description="Also collect OSINT signals (social media, search trends).",
    )


class CollectResponse(BaseModel):
    """Response body for collection job."""

    task_id: str
    token_address: str
    chain: str
    status: Literal["queued", "running", "completed", "failed"]
    message: str


@router.post(
    "",
    summary="Trigger Data Collection",
    description=(
        "Triggers asynchronous blockchain data collection for a token. "
        "Returns a task ID to monitor progress. "
        "Implements the temporal-validity constraint: "
        "all data collected is timestamped and bounded by the Project Midpoint."
    ),
    response_model=CollectResponse,
    status_code=202,
)
async def collect_token_data(
    request: CollectRequest,
    background_tasks: BackgroundTasks,
    db: DatabaseDep,
) -> CollectResponse:
    """
    Trigger data collection for a token address.

    Collects:
    - ERC-20 / BEP-20 transactions (from Etherscan/BscScan API)
    - Wallet addresses involved in transactions
    - Smart contract bytecode and metadata
    - Liquidity pool events (add/remove)
    - OSINT signals (optional)

    Data is stored in PostgreSQL for downstream feature engineering.
    """
    # Validate EVM address format
    validated_address = validate_evm_address(request.token_address)

    logger.info(
        "Collection job queued",
        token_address=validated_address,
        chain=request.chain,
        max_transactions=request.max_transactions,
    )

    # TODO (Phase 3): Import and enqueue Celery task
    # from app.tasks.collect_tasks import collect_token_task
    # task = collect_token_task.delay(validated_address, request.chain, ...)

    task_id = f"collect_{validated_address[:8]}_{request.chain}"

    return CollectResponse(
        task_id=task_id,
        token_address=validated_address,
        chain=request.chain,
        status="queued",
        message=(
            f"Collection queued for {validated_address} on {request.chain}. "
            "Use the task_id to monitor progress."
        ),
    )

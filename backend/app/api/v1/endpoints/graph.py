"""POST /api/v1/graph — Build transaction graph from preprocessed data."""
from __future__ import annotations
from typing import Any, Literal
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.core.dependencies import DatabaseDep
from app.core.logging import get_logger
from app.utils.validators import validate_evm_address

router = APIRouter()
logger = get_logger(__name__)


class GraphBuildRequest(BaseModel):
    token_address: str = Field(..., description="Token contract address.")
    chain: Literal["ethereum", "bsc"] = Field(default="ethereum")
    max_hops: int = Field(default=2, ge=1, le=3, description="Graph neighbourhood depth.")


class GraphBuildResponse(BaseModel):
    task_id: str
    token_address: str
    status: Literal["queued", "running", "completed", "failed"]
    num_nodes: int | None = None
    num_edges: int | None = None
    message: str


@router.post("", summary="Build Transaction Graph", response_model=GraphBuildResponse, status_code=202)
async def build_graph(request: GraphBuildRequest, db: DatabaseDep) -> GraphBuildResponse:
    """
    Build the PyTorch Geometric transaction graph for a token.
    Nodes = wallet addresses. Edges = transactions (directed, weighted, timestamped).
    This supports the TGN continuous-time dynamic graph representation.
    Full implementation in Phase 5.
    """
    validated = validate_evm_address(request.token_address)
    logger.info("Graph build queued", token_address=validated)
    # TODO (Phase 5): Enqueue Celery graph build task
    return GraphBuildResponse(
        task_id=f"graph_{validated[:8]}_{request.chain}",
        token_address=validated,
        status="queued",
        message="Graph construction queued. Full implementation in Phase 5.",
    )

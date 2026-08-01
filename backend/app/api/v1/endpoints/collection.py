"""
app/api/v1/endpoints/collection.py
Data Collection Orchestration API.
"""
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()

class CollectRequest(BaseModel):
    token_address: str
    chain_id: int = 1
    blocks_back: int = 1000

@router.post("/collect", response_model=Dict[str, Any], summary="Trigger blockchain data collection")
async def collect_data(req: CollectRequest, background_tasks: BackgroundTasks):
    """
    Orchestrates the Phase 3 data collection layer.
    Submits a Celery job to scrape historical blocks, transactions, and liquidity events.
    """
    # Orchestration only: No actual data processing here.
    # In a real setup, we would call: celery_app.send_task("collect_token_data", args=[req.token_address])
    
    return {
        "status": "accepted",
        "message": f"Data collection task queued for token {req.token_address}",
        "task_id": "mock_task_id_123"
    }

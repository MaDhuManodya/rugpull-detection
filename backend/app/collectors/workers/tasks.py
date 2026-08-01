"""
app/collectors/workers/tasks.py
Celery Tasks for Event Queue.
"""
import asyncio
from app.collectors.core.queue import celery_app
from app.collectors.persistence.db_writer import DBWriter
from app.database.session import AsyncSessionLocal
import logging

logger = logging.getLogger(__name__)

def run_async(coro):
    """Helper to run async code inside sync Celery tasks."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)

@celery_app.task(bind=True, max_retries=3, queue="transactions")
def process_transaction(self, payload: dict):
    """Processes a raw transaction payload."""
    async def _process():
        async with AsyncSessionLocal() as db:
            await DBWriter.save_transaction(db, payload)
            
    try:
        run_async(_process())
    except Exception as exc:
        logger.error(f"Failed to process tx: {exc}")
        self.retry(exc=exc, countdown=2 ** self.request.retries)

@celery_app.task(bind=True, max_retries=3, queue="liquidity")
def process_liquidity_event(self, payload: dict):
    async def _process():
        async with AsyncSessionLocal() as db:
            await DBWriter.save_liquidity_event(db, payload)
    try:
        run_async(_process())
    except Exception as exc:
        self.retry(exc=exc, countdown=2 ** self.request.retries)

@celery_app.task(bind=True, max_retries=3, queue="contracts")
def process_contract_metadata(self, payload: dict):
    async def _process():
        async with AsyncSessionLocal() as db:
            await DBWriter.save_contract(db, payload)
    try:
        run_async(_process())
    except Exception as exc:
        self.retry(exc=exc, countdown=2 ** self.request.retries)

@celery_app.task(bind=True, max_retries=3, queue="tokens")
def process_token_metadata(self, payload: dict):
    async def _process():
        async with AsyncSessionLocal() as db:
            await DBWriter.save_token_metadata(db, payload)
    try:
        run_async(_process())
    except Exception as exc:
        self.retry(exc=exc, countdown=2 ** self.request.retries)

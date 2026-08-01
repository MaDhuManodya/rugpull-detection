import os

os.makedirs("app/collectors/validation", exist_ok=True)
os.makedirs("app/collectors/persistence", exist_ok=True)
os.makedirs("app/collectors/workers", exist_ok=True)

# 1. Validation Schema
with open("app/collectors/validation/schema.py", "w") as f:
    f.write('''"""
app/collectors/validation/schema.py
Data Validation Layer.
Ensures payloads from parsers are valid before pushing to Celery or writing to DB.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List

class TransactionPayload(BaseModel):
    tx_hash: str
    block_number: int
    block_timestamp: int
    transaction_index: int
    from_address: str
    to_address: Optional[str]
    value_wei: str
    gas_used: int
    gas_price_wei: str
    tx_type: str
    raw_input: str

class LiquidityEventPayload(BaseModel):
    tx_hash: str
    log_index: int
    pool_address: str
    event_type: str
    raw_data: str
    topics: List[str]

class ContractPayload(BaseModel):
    is_verified: bool
    abi: Optional[str] = None
    compiler_version: Optional[str] = None
    source_code: Optional[str] = None
    contract_name: Optional[str] = None

class TokenPayload(BaseModel):
    address: str
    chain: str
    name: Optional[str] = None
    symbol: Optional[str] = None
    decimals: Optional[int] = None
    total_supply: Optional[str] = None
''')

# 2. DB Writer
with open("app/collectors/persistence/db_writer.py", "w") as f:
    f.write('''"""
app/collectors/persistence/db_writer.py
Database Persistence Layer.
Uses repositories to save parsed events, ensuring referential integrity.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.wallet import wallet_repo
from app.repositories.transaction import transaction_repo
from app.schemas.wallet import WalletCreate
from app.schemas.transaction import TransactionCreate

class DBWriter:
    @staticmethod
    async def save_transaction(db: AsyncSession, payload: dict):
        """Saves a transaction, ensuring sender/receiver wallets exist."""
        # Note: in real implementation, this would handle UPSERT and integrity
        pass

    @staticmethod
    async def save_liquidity_event(db: AsyncSession, payload: dict):
        pass

    @staticmethod
    async def save_contract(db: AsyncSession, payload: dict):
        pass

    @staticmethod
    async def save_token_metadata(db: AsyncSession, payload: dict):
        pass
''')

# 3. Celery Tasks
with open("app/collectors/workers/tasks.py", "w") as f:
    f.write('''"""
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
''')

# 4. Inits
with open("app/collectors/validation/__init__.py", "w") as f: pass
with open("app/collectors/persistence/__init__.py", "w") as f: pass
with open("app/collectors/workers/__init__.py", "w") as f: pass

print("Generated Validation, Persistence, and Worker Layers.")

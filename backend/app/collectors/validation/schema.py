"""
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

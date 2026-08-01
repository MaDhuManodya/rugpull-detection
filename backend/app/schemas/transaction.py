from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class TransactionBase(BaseModel):
    pass # Define common fields here

class TransactionCreate(TransactionBase):
    pass # Fields required for creation

class TransactionUpdate(TransactionBase):
    pass # Fields for update, usually all Optional

class Transaction(TransactionBase):
    id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

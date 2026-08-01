from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class ContractBase(BaseModel):
    pass # Define common fields here

class ContractCreate(ContractBase):
    pass # Fields required for creation

class ContractUpdate(ContractBase):
    pass # Fields for update, usually all Optional

class Contract(ContractBase):
    id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

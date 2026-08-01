from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class LiquidityEventBase(BaseModel):
    pass # Define common fields here

class LiquidityEventCreate(LiquidityEventBase):
    pass # Fields required for creation

class LiquidityEventUpdate(LiquidityEventBase):
    pass # Fields for update, usually all Optional

class LiquidityEvent(LiquidityEventBase):
    id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

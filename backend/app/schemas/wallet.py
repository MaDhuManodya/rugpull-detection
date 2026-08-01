from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class WalletBase(BaseModel):
    pass # Define common fields here

class WalletCreate(WalletBase):
    pass # Fields required for creation

class WalletUpdate(WalletBase):
    pass # Fields for update, usually all Optional

class Wallet(WalletBase):
    id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

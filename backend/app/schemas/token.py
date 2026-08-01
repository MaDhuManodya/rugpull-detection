from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class TokenBase(BaseModel):
    pass # Define common fields here

class TokenCreate(TokenBase):
    pass # Fields required for creation

class TokenUpdate(TokenBase):
    pass # Fields for update, usually all Optional

class Token(TokenBase):
    id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

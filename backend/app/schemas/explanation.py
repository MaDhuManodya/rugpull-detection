from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class ExplanationBase(BaseModel):
    pass # Define common fields here

class ExplanationCreate(ExplanationBase):
    pass # Fields required for creation

class ExplanationUpdate(ExplanationBase):
    pass # Fields for update, usually all Optional

class Explanation(ExplanationBase):
    id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

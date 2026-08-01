from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class TokenFeatureBase(BaseModel):
    pass # Define common fields here

class TokenFeatureCreate(TokenFeatureBase):
    pass # Fields required for creation

class TokenFeatureUpdate(TokenFeatureBase):
    pass # Fields for update, usually all Optional

class TokenFeature(TokenFeatureBase):
    id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

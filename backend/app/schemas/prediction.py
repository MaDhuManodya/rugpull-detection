from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class PredictionBase(BaseModel):
    pass # Define common fields here

class PredictionCreate(PredictionBase):
    pass # Fields required for creation

class PredictionUpdate(PredictionBase):
    pass # Fields for update, usually all Optional

class Prediction(PredictionBase):
    id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

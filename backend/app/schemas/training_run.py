from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class TrainingRunBase(BaseModel):
    pass # Define common fields here

class TrainingRunCreate(TrainingRunBase):
    pass # Fields required for creation

class TrainingRunUpdate(TrainingRunBase):
    pass # Fields for update, usually all Optional

class TrainingRun(TrainingRunBase):
    id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

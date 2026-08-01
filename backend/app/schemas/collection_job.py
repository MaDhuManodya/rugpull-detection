from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class CollectionJobBase(BaseModel):
    pass # Define common fields here

class CollectionJobCreate(CollectionJobBase):
    pass # Fields required for creation

class CollectionJobUpdate(CollectionJobBase):
    pass # Fields for update, usually all Optional

class CollectionJob(CollectionJobBase):
    id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

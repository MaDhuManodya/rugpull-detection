import os

SCHEMAS_DIR = "app/schemas"
REPOS_DIR = "app/repositories"

os.makedirs(SCHEMAS_DIR, exist_ok=True)
os.makedirs(REPOS_DIR, exist_ok=True)

ENTITIES = [
    ("Token", "token", "TokenCreate", "TokenUpdate"),
    ("Wallet", "wallet", "WalletCreate", "WalletUpdate"),
    ("Contract", "contract", "ContractCreate", "ContractUpdate"),
    ("Transaction", "transaction", "TransactionCreate", "TransactionUpdate"),
    ("LiquidityEvent", "liquidity_event", "LiquidityEventCreate", "LiquidityEventUpdate"),
    ("TokenFeature", "token_feature", "TokenFeatureCreate", "TokenFeatureUpdate"),
    ("Prediction", "prediction", "PredictionCreate", "PredictionUpdate"),
    ("Explanation", "explanation", "ExplanationCreate", "ExplanationUpdate"),
    ("TrainingRun", "training_run", "TrainingRunCreate", "TrainingRunUpdate"),
    ("CollectionJob", "collection_job", "CollectionJobCreate", "CollectionJobUpdate"),
]

# Write Base Repository
with open(f"{REPOS_DIR}/base.py", "w") as f:
    f.write('''"""
Base generic repository pattern implementation.
"""
from typing import Any, Generic, Type, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=Any)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=Any)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: UUID) -> ModelType | None:
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalars().first()

    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[ModelType]:
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, *, db_obj: ModelType, obj_in: UpdateSchemaType | dict[str, Any]) -> ModelType:
        obj_data = db_obj.__dict__
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: UUID) -> ModelType | None:
        obj = await self.get(db, id=id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj
''')

# Write specific schemas and repositories
for model_name, file_name, create_schema, update_schema in ENTITIES:
    # Write Schema
    with open(f"{SCHEMAS_DIR}/{file_name}.py", "w") as f:
        f.write(f'''from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class {model_name}Base(BaseModel):
    pass # Define common fields here

class {create_schema}({model_name}Base):
    pass # Fields required for creation

class {update_schema}({model_name}Base):
    pass # Fields for update, usually all Optional

class {model_name}({model_name}Base):
    id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
''')
    
    # Write Repository
    with open(f"{REPOS_DIR}/{file_name}.py", "w") as f:
        f.write(f'''from app.models.{file_name} import {model_name}
from app.repositories.base import BaseRepository
from app.schemas.{file_name} import {create_schema}, {update_schema}

class Repository{model_name}(BaseRepository[{model_name}, {create_schema}, {update_schema}]):
    pass

{file_name}_repo = Repository{model_name}({model_name})
''')

# Write __init__.py for Repositories
with open(f"{REPOS_DIR}/__init__.py", "w") as f:
    for model_name, file_name, _, _ in ENTITIES:
        f.write(f"from .{file_name} import {file_name}_repo\n")

print("Generated schemas and repositories.")

"""
app/models/__init__.py
───────────────────────
Exports all ORM models so that Alembic can detect them when generating migrations.
All models inherit from `Base` which is also exported here.
"""

from app.database.base import Base

from app.models.collection_job import CollectionJob
from app.models.contract import Contract
from app.models.enums import (
    ChainEnum,
    JobStatusEnum,
    LabelEnum,
    LiquidityEventTypeEnum,
    ModelTypeEnum,
    TrainingStatusEnum,
    TxTypeEnum,
    WalletTypeEnum,
)
from app.models.explanation import Explanation
from app.models.liquidity_event import LiquidityEvent
from app.models.prediction import Prediction
from app.models.token import Token
from app.models.token_feature import TokenFeature
from app.models.training_run import TrainingRun
from app.models.transaction import Transaction
from app.models.wallet import Wallet

__all__ = [
    "Base",
    "CollectionJob",
    "Contract",
    "Explanation",
    "LiquidityEvent",
    "Prediction",
    "Token",
    "TokenFeature",
    "TrainingRun",
    "Transaction",
    "Wallet",
    "ChainEnum",
    "JobStatusEnum",
    "LabelEnum",
    "LiquidityEventTypeEnum",
    "ModelTypeEnum",
    "TrainingStatusEnum",
    "TxTypeEnum",
    "WalletTypeEnum",
]

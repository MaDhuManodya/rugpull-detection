from app.models.transaction import Transaction
from app.repositories.base import BaseRepository
from app.schemas.transaction import TransactionCreate, TransactionUpdate

class RepositoryTransaction(BaseRepository[Transaction, TransactionCreate, TransactionUpdate]):
    pass

transaction_repo = RepositoryTransaction(Transaction)

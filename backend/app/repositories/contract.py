from app.models.contract import Contract
from app.repositories.base import BaseRepository
from app.schemas.contract import ContractCreate, ContractUpdate

class RepositoryContract(BaseRepository[Contract, ContractCreate, ContractUpdate]):
    pass

contract_repo = RepositoryContract(Contract)

from app.models.wallet import Wallet
from app.repositories.base import BaseRepository
from app.schemas.wallet import WalletCreate, WalletUpdate

class RepositoryWallet(BaseRepository[Wallet, WalletCreate, WalletUpdate]):
    pass

wallet_repo = RepositoryWallet(Wallet)

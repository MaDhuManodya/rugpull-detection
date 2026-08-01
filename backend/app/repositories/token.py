from app.models.token import Token
from app.repositories.base import BaseRepository
from app.schemas.token import TokenCreate, TokenUpdate

class RepositoryToken(BaseRepository[Token, TokenCreate, TokenUpdate]):
    pass

token_repo = RepositoryToken(Token)

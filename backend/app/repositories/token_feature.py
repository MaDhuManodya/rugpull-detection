from app.models.token_feature import TokenFeature
from app.repositories.base import BaseRepository
from app.schemas.token_feature import TokenFeatureCreate, TokenFeatureUpdate

class RepositoryTokenFeature(BaseRepository[TokenFeature, TokenFeatureCreate, TokenFeatureUpdate]):
    pass

token_feature_repo = RepositoryTokenFeature(TokenFeature)

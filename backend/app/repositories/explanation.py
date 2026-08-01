from app.models.explanation import Explanation
from app.repositories.base import BaseRepository
from app.schemas.explanation import ExplanationCreate, ExplanationUpdate

class RepositoryExplanation(BaseRepository[Explanation, ExplanationCreate, ExplanationUpdate]):
    pass

explanation_repo = RepositoryExplanation(Explanation)

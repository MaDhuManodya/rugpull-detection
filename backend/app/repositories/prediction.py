from app.models.prediction import Prediction
from app.repositories.base import BaseRepository
from app.schemas.prediction import PredictionCreate, PredictionUpdate

class RepositoryPrediction(BaseRepository[Prediction, PredictionCreate, PredictionUpdate]):
    pass

prediction_repo = RepositoryPrediction(Prediction)

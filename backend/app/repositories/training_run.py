from app.models.training_run import TrainingRun
from app.repositories.base import BaseRepository
from app.schemas.training_run import TrainingRunCreate, TrainingRunUpdate

class RepositoryTrainingRun(BaseRepository[TrainingRun, TrainingRunCreate, TrainingRunUpdate]):
    pass

training_run_repo = RepositoryTrainingRun(TrainingRun)

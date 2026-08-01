from app.models.collection_job import CollectionJob
from app.repositories.base import BaseRepository
from app.schemas.collection_job import CollectionJobCreate, CollectionJobUpdate

class RepositoryCollectionJob(BaseRepository[CollectionJob, CollectionJobCreate, CollectionJobUpdate]):
    pass

collection_job_repo = RepositoryCollectionJob(CollectionJob)

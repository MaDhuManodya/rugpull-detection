from app.models.liquidity_event import LiquidityEvent
from app.repositories.base import BaseRepository
from app.schemas.liquidity_event import LiquidityEventCreate, LiquidityEventUpdate

class RepositoryLiquidityEvent(BaseRepository[LiquidityEvent, LiquidityEventCreate, LiquidityEventUpdate]):
    pass

liquidity_event_repo = RepositoryLiquidityEvent(LiquidityEvent)

from __future__ import annotations

from sqlalchemy.orm import Session

from src.entities.return_stats import ReturnStats
from src.repositories.base_repo import BaseRepository


class ReturnStatsRepository(BaseRepository[ReturnStats]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=ReturnStats)

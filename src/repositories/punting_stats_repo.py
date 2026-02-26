from __future__ import annotations

from sqlalchemy.orm import Session

from src.entities.punting_stats import PuntingStats
from src.repositories.base_repo import BaseRepository


class PuntingStatsRepository(BaseRepository[PuntingStats]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=PuntingStats)

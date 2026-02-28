from __future__ import annotations

from sqlalchemy.orm import Session

from src.entities.defense_stats import DefenseStats
from src.repositories.base_repo import BaseRepository


class DefenseStatsRepository(BaseRepository[DefenseStats]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=DefenseStats)

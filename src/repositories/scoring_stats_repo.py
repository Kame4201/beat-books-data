from __future__ import annotations

from sqlalchemy.orm import Session

from src.entities.scoring_stats import ScoringStats
from src.repositories.base_repo import BaseRepository


class ScoringStatsRepository(BaseRepository[ScoringStats]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=ScoringStats)

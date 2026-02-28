from __future__ import annotations

from sqlalchemy.orm import Session

from src.entities.kicking_stats import KickingStats
from src.repositories.base_repo import BaseRepository


class KickingStatsRepository(BaseRepository[KickingStats]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=KickingStats)

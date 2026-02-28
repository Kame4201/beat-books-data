from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.entities.rushing_stats import RushingStats
from src.repositories.base_repo import BaseRepository


class RushingStatsRepository(BaseRepository[RushingStats]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=RushingStats)

    def search_players(
        self,
        query: str,
        season: int | None = None,
        position: str | None = None,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[RushingStats]:
        """Search for players by name with optional filters."""
        stmt = select(self.model).where(self.model.player_name.ilike(f"%{query}%"))

        if season is not None:
            stmt = stmt.where(self.model.season == season)

        if position is not None:
            stmt = stmt.where(self.model.pos == position)

        stmt = stmt.order_by(self.model.player_name.asc()).limit(limit).offset(offset)
        return list(self.session.execute(stmt).scalars().all())

from __future__ import annotations

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, or_

from src.entities.passing_stats import PassingStats
from src.repositories.base_repo import BaseRepository


class PassingStatsRepository(BaseRepository[PassingStats]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=PassingStats)

    def find_by_player(self, player_name: str, season: Optional[int] = None, *, limit: int = 50, offset: int = 0) -> list[PassingStats]:
        """Find passing stats for a specific player, optionally filtered by season."""
        stmt = select(self.model).where(self.model.player_name.ilike(f"%{player_name}%"))

        if season is not None:
            stmt = stmt.where(self.model.season == season)

        stmt = stmt.order_by(self.model.season.desc()).limit(limit).offset(offset)
        return list(self.session.execute(stmt).scalars().all())

    def find_by_season_and_position(self, season: int, position: Optional[str] = None, *, limit: int = 50, offset: int = 0, sort_by: str = "yds", order: str = "desc") -> list[PassingStats]:
        """Find passing stats for a season, optionally filtered by position."""
        stmt = select(self.model).where(self.model.season == season)

        if position is not None:
            stmt = stmt.where(self.model.pos == position)

        # Apply sorting
        sort_column = getattr(self.model, sort_by, None)
        if sort_column is not None:
            if order.lower() == "asc":
                stmt = stmt.order_by(sort_column.asc())
            else:
                stmt = stmt.order_by(sort_column.desc())

        stmt = stmt.limit(limit).offset(offset)
        return list(self.session.execute(stmt).scalars().all())

    def search_players(self, query: str, season: Optional[int] = None, *, limit: int = 50, offset: int = 0) -> list[PassingStats]:
        """Search for players by name with optional season filter."""
        stmt = select(self.model).where(self.model.player_name.ilike(f"%{query}%"))

        if season is not None:
            stmt = stmt.where(self.model.season == season)

        stmt = stmt.order_by(self.model.player_name.asc()).limit(limit).offset(offset)
        return list(self.session.execute(stmt).scalars().all())

    def count_by_season(self, season: int, position: Optional[str] = None) -> int:
        """Count total passing stats entries for a season and optional position."""
        from sqlalchemy import func
        stmt = select(func.count()).select_from(self.model).where(self.model.season == season)

        if position is not None:
            stmt = stmt.where(self.model.pos == position)

        return self.session.execute(stmt).scalar() or 0

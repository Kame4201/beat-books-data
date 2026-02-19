from __future__ import annotations

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.entities.team_defense import TeamDefense
from src.repositories.base_repo import BaseRepository


class TeamDefenseRepository(BaseRepository[TeamDefense]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=TeamDefense)

    def find_by_season(
        self,
        season: int,
        *,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "pa",
        order: str = "asc",
    ) -> list[TeamDefense]:
        """Find all team defense stats for a given season with pagination and sorting."""
        stmt = select(self.model).where(self.model.season == season)

        sort_column = getattr(self.model, sort_by, None)
        if sort_column is not None:
            if order.lower() == "asc":
                stmt = stmt.order_by(sort_column.asc())
            else:
                stmt = stmt.order_by(sort_column.desc())

        stmt = stmt.limit(limit).offset(offset)
        return list(self.session.execute(stmt).scalars().all())

    def find_by_team_and_season(self, team: str, season: int) -> Optional[TeamDefense]:
        """Find team defense stats for a specific team and season."""
        stmt = select(self.model).where(
            self.model.tm == team, self.model.season == season
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def count_by_season(self, season: int) -> int:
        """Count total teams for a season."""
        from sqlalchemy import func

        stmt = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.season == season)
        )
        return self.session.execute(stmt).scalar() or 0

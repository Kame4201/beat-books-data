from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.entities.team_offense import TeamOffense
from src.repositories.base_repo import BaseRepository


class TeamOffenseRepository(BaseRepository[TeamOffense]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=TeamOffense)

    def find_by_season(
        self,
        season: int,
        *,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "pf",
        order: str = "desc",
    ) -> list[TeamOffense]:
        """Find team offense stats for a season."""
        stmt = select(self.model).where(self.model.season == season)

        # Apply sorting
        sort_column = getattr(self.model, sort_by, None)
        if sort_column is not None:
            if order.lower() == "asc":
                stmt = stmt.order_by(sort_column.asc())
            else:
                stmt = stmt.order_by(sort_column.desc())

        stmt = stmt.limit(limit).offset(offset)
        return list(self.session.execute(stmt).scalars().all())

    def find_by_team_and_season(self, team: str, season: int) -> TeamOffense | None:
        """Find team offense stats for a specific team and season."""
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

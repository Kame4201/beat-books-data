from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.entities.games import Games
from src.repositories.base_repo import BaseRepository


class GamesRepository(BaseRepository[Games]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=Games)

    def find_by_season(
        self,
        season: int,
        *,
        limit: int = 300,
        offset: int = 0,
        sort_by: str = "week",
        order: str = "asc",
    ) -> list[Games]:
        """Find all games for a given season with pagination and sorting."""
        stmt = select(self.model).where(self.model.season == season)

        sort_column = getattr(self.model, sort_by, None)
        if sort_column is not None:
            if order.lower() == "asc":
                stmt = stmt.order_by(sort_column.asc())
            else:
                stmt = stmt.order_by(sort_column.desc())

        stmt = stmt.limit(limit).offset(offset)
        return list(self.session.execute(stmt).scalars().all())

    def count_by_season(self, season: int) -> int:
        """Count total games for a season."""
        from sqlalchemy import func

        stmt = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.season == season)
        )
        return self.session.execute(stmt).scalar() or 0

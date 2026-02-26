from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.entities.standings import Standings
from src.repositories.base_repo import BaseRepository


class StandingsRepository(BaseRepository[Standings]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=Standings)

    def find_by_season(
        self,
        season: int,
        *,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "win_pct",
        order: str = "desc",
    ) -> list[Standings]:
        """Find all standings for a given season with pagination and sorting."""
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

    def count_by_season(self, season: int) -> int:
        """Count total standings entries for a season."""
        from sqlalchemy import func

        stmt = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.season == season)
        )
        return self.session.execute(stmt).scalar() or 0

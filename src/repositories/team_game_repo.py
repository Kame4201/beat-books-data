"""Repository for team game log operations.

Extends BaseRepository with specialized queries for game lookups,
season/week filtering, and upsert (create-or-skip) logic.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from src.entities.team_game import TeamGame
from src.dtos.team_game_dto import TeamGameCreate
from src.repositories.base_repo import BaseRepository


class TeamGameRepository(BaseRepository[TeamGame]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=TeamGame)

    def find_by_unique_key(
        self, team_abbr: str, season: int, week: int
    ) -> Optional[TeamGame]:
        """Find a game by its unique (team_abbr, season, week) key."""
        stmt = select(TeamGame).where(
            TeamGame.team_abbr == team_abbr,
            TeamGame.season == season,
            TeamGame.week == week,
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def create_from_dto(self, dto: TeamGameCreate, *, commit: bool = True) -> TeamGame:
        """Create a TeamGame entity from a DTO."""
        entity = TeamGame(**dto.model_dump())
        return self.create(entity, commit=commit)

    def create_or_skip(self, dto: TeamGameCreate) -> TeamGame:
        """Insert a game record, or return the existing one if duplicate."""
        existing = self.find_by_unique_key(dto.team_abbr, dto.season, dto.week)
        if existing:
            return existing
        return self.create_from_dto(dto)

    def find_by_season_and_week(
        self,
        season: int,
        week: Optional[int] = None,
        *,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "week",
        order: str = "asc",
    ) -> list[TeamGame]:
        """Find games for a season, optionally filtered by week."""
        stmt = select(TeamGame).where(TeamGame.season == season)

        if week is not None:
            stmt = stmt.where(TeamGame.week == week)

        sort_column = getattr(TeamGame, sort_by, None)
        if sort_column is not None:
            if order.lower() == "asc":
                stmt = stmt.order_by(sort_column.asc())
            else:
                stmt = stmt.order_by(sort_column.desc())

        stmt = stmt.limit(limit).offset(offset)
        return list(self.session.execute(stmt).scalars().all())

    def count_by_season(self, season: int, week: Optional[int] = None) -> int:
        """Count total games for a season and optional week."""
        stmt = (
            select(func.count()).select_from(TeamGame).where(TeamGame.season == season)
        )

        if week is not None:
            stmt = stmt.where(TeamGame.week == week)

        return self.session.execute(stmt).scalar() or 0

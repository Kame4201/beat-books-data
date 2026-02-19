# repositories/team_game_repo.py
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.entities.team_game import TeamGame
from src.dtos.team_game_dto import TeamGameCreate


class TeamGameRepository:

    @staticmethod
    def get_by_unique_key(db: Session, team_abbr: str, season: int, week: int):
        return (
            db.query(TeamGame)
            .filter(
                TeamGame.team_abbr == team_abbr,
                TeamGame.season == season,
                TeamGame.week == week,
            )
            .first()
        )

    @staticmethod
    def create(db: Session, obj: TeamGameCreate):
        db_obj = TeamGame(**obj.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def create_or_skip(db: Session, obj: TeamGameCreate):
        existing = TeamGameRepository.get_by_unique_key(
            db, obj.team_abbr, obj.season, obj.week
        )
        if existing:
            return existing  # Skip duplicate
        return TeamGameRepository.create(db, obj)

    @staticmethod
    def find_by_season_and_week(
        db: Session,
        season: int,
        week: Optional[int] = None,
        *,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "week",
        order: str = "asc"
    ) -> list[TeamGame]:
        """Find games for a season, optionally filtered by week."""
        stmt = select(TeamGame).where(TeamGame.season == season)

        if week is not None:
            stmt = stmt.where(TeamGame.week == week)

        # Apply sorting
        sort_column = getattr(TeamGame, sort_by, None)
        if sort_column is not None:
            if order.lower() == "asc":
                stmt = stmt.order_by(sort_column.asc())
            else:
                stmt = stmt.order_by(sort_column.desc())

        stmt = stmt.limit(limit).offset(offset)
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def count_by_season(db: Session, season: int, week: Optional[int] = None) -> int:
        """Count total games for a season and optional week."""
        from sqlalchemy import func

        stmt = (
            select(func.count()).select_from(TeamGame).where(TeamGame.season == season)
        )

        if week is not None:
            stmt = stmt.where(TeamGame.week == week)

        return db.execute(stmt).scalar() or 0

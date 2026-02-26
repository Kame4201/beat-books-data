"""Repository for odds data access."""

from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.dtos.odds_dto import OddsCreate
from src.entities.odds import Odds


class OddsRepository:
    """Data access layer for odds data. ALL SQL lives here."""

    @staticmethod
    def get_by_id(db: Session, odds_id: int) -> Odds | None:
        """Retrieve a single odds record by ID."""
        return db.query(Odds).filter(Odds.id == odds_id).first()

    @staticmethod
    def get_by_unique_key(
        db: Session,
        season: int,
        week: int,
        home_team: str,
        sportsbook: str,
        timestamp: datetime,
    ) -> Odds | None:
        """Get odds by unique constraint fields."""
        return (
            db.query(Odds)
            .filter(
                and_(
                    Odds.season == season,
                    Odds.week == week,
                    Odds.home_team == home_team,
                    Odds.sportsbook == sportsbook,
                    Odds.timestamp == timestamp,
                )
            )
            .first()
        )

    @staticmethod
    def create(db: Session, obj: OddsCreate) -> Odds:
        """Create a new odds record."""
        db_obj = Odds(**obj.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def create_or_skip(db: Session, obj: OddsCreate) -> Odds:
        """Create a new odds record or return existing if duplicate."""
        existing = OddsRepository.get_by_unique_key(
            db, obj.season, obj.week, obj.home_team, obj.sportsbook, obj.timestamp
        )
        if existing:
            return existing
        return OddsRepository.create(db, obj)

    @staticmethod
    def get_closing_lines(
        db: Session, season: int, week: int, sportsbook: str | None = None
    ) -> list[Odds]:
        """Get all closing lines for a specific week."""
        query = db.query(Odds).filter(
            and_(Odds.season == season, Odds.week == week, Odds.is_closing.is_(True))
        )
        if sportsbook:
            query = query.filter(Odds.sportsbook == sportsbook)
        return query.all()

    @staticmethod
    def get_opening_lines(
        db: Session, season: int, week: int, sportsbook: str | None = None
    ) -> list[Odds]:
        """Get all opening lines for a specific week."""
        query = db.query(Odds).filter(
            and_(Odds.season == season, Odds.week == week, Odds.is_opening.is_(True))
        )
        if sportsbook:
            query = query.filter(Odds.sportsbook == sportsbook)
        return query.all()

    @staticmethod
    def get_line_movement(
        db: Session, season: int, week: int, home_team: str, sportsbook: str
    ) -> list[Odds]:
        """Get all line movements for a specific game/sportsbook."""
        return (
            db.query(Odds)
            .filter(
                and_(
                    Odds.season == season,
                    Odds.week == week,
                    Odds.home_team == home_team,
                    Odds.sportsbook == sportsbook,
                )
            )
            .order_by(Odds.timestamp)
            .all()
        )

    @staticmethod
    def get_by_team(
        db: Session,
        team: str,
        season: int | None = None,
        week: int | None = None,
        is_closing: bool | None = None,
    ) -> list[Odds]:
        """Get all odds records for a specific team."""
        query = db.query(Odds).filter(
            (Odds.home_team == team) | (Odds.away_team == team)
        )

        if season is not None:
            query = query.filter(Odds.season == season)
        if week is not None:
            query = query.filter(Odds.week == week)
        if is_closing is not None:
            query = query.filter(Odds.is_closing == is_closing)

        return query.order_by(Odds.game_date, Odds.timestamp).all()

    @staticmethod
    def bulk_create(db: Session, odds_list: list[OddsCreate]) -> list[Odds]:
        """Bulk insert odds records."""
        db_objs = [Odds(**obj.model_dump()) for obj in odds_list]
        db.add_all(db_objs)
        db.commit()
        for obj in db_objs:
            db.refresh(obj)
        return db_objs

# repositories/team_game_repo.py
from sqlalchemy.orm import Session
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

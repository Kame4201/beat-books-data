# Entities/team_game.py
from sqlalchemy import Column, Integer, String, Date

from .base import Base


class TeamGame(Base):
    __tablename__ = "team_games"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_abbr = Column(String(8), nullable=False)
    season = Column(Integer, nullable=False)
    week = Column(Integer, nullable=False)

    day = Column(String(3))
    game_date = Column(Date)
    game_time = Column(String(16))

    winner = Column(String(64))
    loser = Column(String(64))

    pts_w = Column(Integer)
    pts_l = Column(Integer)
    yds_w = Column(Integer)
    to_w = Column(Integer)
    yds_l = Column(Integer)
    to_l = Column(Integer)

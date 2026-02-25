"""Team game log entity — individual team game results per season/week."""

from typing import Optional
from datetime import date

from sqlalchemy import Integer, String, Date
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class TeamGame(Base):
    __tablename__ = "team_games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    team_abbr: Mapped[str] = mapped_column(String(8), nullable=False)
    season: Mapped[int] = mapped_column(Integer, nullable=False)
    week: Mapped[int] = mapped_column(Integer, nullable=False)

    day: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    game_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    game_time: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)

    winner: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    loser: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    pts_w: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pts_l: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    yds_w: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    to_w: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    yds_l: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    to_l: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

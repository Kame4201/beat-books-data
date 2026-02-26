"""Team game log entity — individual team game results per season/week."""

from datetime import date

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class TeamGame(Base):
    __tablename__ = "team_games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    team_abbr: Mapped[str] = mapped_column(String(8), nullable=False)
    season: Mapped[int] = mapped_column(Integer, nullable=False)
    week: Mapped[int] = mapped_column(Integer, nullable=False)

    day: Mapped[str | None] = mapped_column(String(3), nullable=True)
    game_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    game_time: Mapped[str | None] = mapped_column(String(16), nullable=True)

    winner: Mapped[str | None] = mapped_column(String(64), nullable=True)
    loser: Mapped[str | None] = mapped_column(String(64), nullable=True)

    pts_w: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pts_l: Mapped[int | None] = mapped_column(Integer, nullable=True)
    yds_w: Mapped[int | None] = mapped_column(Integer, nullable=True)
    to_w: Mapped[int | None] = mapped_column(Integer, nullable=True)
    yds_l: Mapped[int | None] = mapped_column(Integer, nullable=True)
    to_l: Mapped[int | None] = mapped_column(Integer, nullable=True)

from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Games(Base):
    __tablename__ = "games"
    __table_args__ = (
        UniqueConstraint(
            "season",
            "week",
            "winner",
            "loser",
            name="uq_games_season_week_winner_loser",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season: Mapped[int | None] = mapped_column(Integer)

    week: Mapped[int | None] = mapped_column(Integer)
    game_day: Mapped[str | None] = mapped_column(String(16))
    game_date: Mapped[date | None] = mapped_column(Date)
    kickoff_time: Mapped[str | None] = mapped_column(String(16))
    winner: Mapped[str | None] = mapped_column(String(64))
    loser: Mapped[str | None] = mapped_column(String(64))
    boxscore: Mapped[str | None] = mapped_column(String(128))
    pts_w: Mapped[int | None] = mapped_column(Integer)
    pts_l: Mapped[int | None] = mapped_column(Integer)
    yds_w: Mapped[int | None] = mapped_column(Integer)
    to_w: Mapped[int | None] = mapped_column(Integer)
    yds_l: Mapped[int | None] = mapped_column(Integer)
    to_l: Mapped[int | None] = mapped_column(Integer)

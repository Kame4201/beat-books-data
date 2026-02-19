from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import Integer, String, Date, UniqueConstraint
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
    season: Mapped[Optional[int]] = mapped_column(Integer)

    week: Mapped[Optional[int]] = mapped_column(Integer)
    game_day: Mapped[Optional[str]] = mapped_column(String(16))
    game_date: Mapped[Optional[date]] = mapped_column(Date)
    kickoff_time: Mapped[Optional[str]] = mapped_column(String(16))
    winner: Mapped[Optional[str]] = mapped_column(String(64))
    loser: Mapped[Optional[str]] = mapped_column(String(64))
    boxscore: Mapped[Optional[str]] = mapped_column(String(128))
    pts_w: Mapped[Optional[int]] = mapped_column(Integer)
    pts_l: Mapped[Optional[int]] = mapped_column(Integer)
    yds_w: Mapped[Optional[int]] = mapped_column(Integer)
    to_w: Mapped[Optional[int]] = mapped_column(Integer)
    yds_l: Mapped[Optional[int]] = mapped_column(Integer)
    to_l: Mapped[Optional[int]] = mapped_column(Integer)

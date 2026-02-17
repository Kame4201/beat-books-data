from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import Integer, String, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class RushingStats(Base):
    __tablename__ = "rushing_stats"
    __table_args__ = (
        UniqueConstraint(
            "player_name", "season", "tm", name="uq_rushing_stats_player_season_tm"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season: Mapped[Optional[int]] = mapped_column(Integer)

    rk: Mapped[Optional[int]] = mapped_column(Integer)
    player_name: Mapped[Optional[str]] = mapped_column(String(128))
    age: Mapped[Optional[int]] = mapped_column(Integer)
    tm: Mapped[Optional[str]] = mapped_column(String(64))
    pos: Mapped[Optional[str]] = mapped_column(String(16))

    g: Mapped[Optional[int]] = mapped_column(Integer)
    gs: Mapped[Optional[int]] = mapped_column(Integer)

    att: Mapped[Optional[int]] = mapped_column(Integer)
    yds: Mapped[Optional[int]] = mapped_column(Integer)
    td: Mapped[Optional[int]] = mapped_column(Integer)
    first_downs: Mapped[Optional[int]] = mapped_column(Integer)
    succ_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    lng: Mapped[Optional[int]] = mapped_column(Integer)
    ypa: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    ypg: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    apg: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    fmb: Mapped[Optional[int]] = mapped_column(Integer)
    awards: Mapped[Optional[str]] = mapped_column(String(128))

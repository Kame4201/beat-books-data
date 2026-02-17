from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import Integer, String, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class PuntingStats(Base):
    __tablename__ = "punting_stats"
    __table_args__ = (
        UniqueConstraint(
            "player_name", "season", "tm", name="uq_punting_stats_player_season_tm"
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

    pnt: Mapped[Optional[int]] = mapped_column(Integer)
    yds: Mapped[Optional[int]] = mapped_column(Integer)
    ypp: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    ret_yds: Mapped[Optional[int]] = mapped_column(Integer)
    net_yds: Mapped[Optional[int]] = mapped_column(Integer)
    ny_pa: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    lng: Mapped[Optional[int]] = mapped_column(Integer)
    tb: Mapped[Optional[int]] = mapped_column(Integer)
    tb_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    pnt20: Mapped[Optional[int]] = mapped_column(Integer)
    in20_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    blck: Mapped[Optional[int]] = mapped_column(Integer)
    awards: Mapped[Optional[str]] = mapped_column(String(128))

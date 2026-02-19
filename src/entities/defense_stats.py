from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import Integer, String, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class DefenseStats(Base):
    __tablename__ = "defense_stats"
    __table_args__ = (
        UniqueConstraint(
            "player_name", "season", "tm", name="uq_defense_stats_player_season_tm"
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

    ints: Mapped[Optional[int]] = mapped_column(Integer)
    int_yds: Mapped[Optional[int]] = mapped_column(Integer)
    int_td: Mapped[Optional[int]] = mapped_column(Integer)
    int_lng: Mapped[Optional[int]] = mapped_column(Integer)
    pd: Mapped[Optional[int]] = mapped_column(Integer)
    ff: Mapped[Optional[int]] = mapped_column(Integer)
    fmb: Mapped[Optional[int]] = mapped_column(Integer)
    fr: Mapped[Optional[int]] = mapped_column(Integer)
    fr_yds: Mapped[Optional[int]] = mapped_column(Integer)
    fr_td: Mapped[Optional[int]] = mapped_column(Integer)

    sk: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    comb: Mapped[Optional[int]] = mapped_column(Integer)
    solo: Mapped[Optional[int]] = mapped_column(Integer)
    ast: Mapped[Optional[int]] = mapped_column(Integer)
    tfl: Mapped[Optional[int]] = mapped_column(Integer)
    qb_hits: Mapped[Optional[int]] = mapped_column(Integer)
    sfty: Mapped[Optional[int]] = mapped_column(Integer)

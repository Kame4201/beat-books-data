from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Integer, Numeric, String, UniqueConstraint
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
    season: Mapped[int | None] = mapped_column(Integer)

    rk: Mapped[int | None] = mapped_column(Integer)
    player_name: Mapped[str | None] = mapped_column(String(128))
    age: Mapped[int | None] = mapped_column(Integer)
    tm: Mapped[str | None] = mapped_column(String(64))
    pos: Mapped[str | None] = mapped_column(String(16))
    g: Mapped[int | None] = mapped_column(Integer)
    gs: Mapped[int | None] = mapped_column(Integer)

    ints: Mapped[int | None] = mapped_column(Integer)
    int_yds: Mapped[int | None] = mapped_column(Integer)
    int_td: Mapped[int | None] = mapped_column(Integer)
    int_lng: Mapped[int | None] = mapped_column(Integer)
    pd: Mapped[int | None] = mapped_column(Integer)
    ff: Mapped[int | None] = mapped_column(Integer)
    fmb: Mapped[int | None] = mapped_column(Integer)
    fr: Mapped[int | None] = mapped_column(Integer)
    fr_yds: Mapped[int | None] = mapped_column(Integer)
    fr_td: Mapped[int | None] = mapped_column(Integer)

    sk: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    comb: Mapped[int | None] = mapped_column(Integer)
    solo: Mapped[int | None] = mapped_column(Integer)
    ast: Mapped[int | None] = mapped_column(Integer)
    tfl: Mapped[int | None] = mapped_column(Integer)
    qb_hits: Mapped[int | None] = mapped_column(Integer)
    sfty: Mapped[int | None] = mapped_column(Integer)

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import Integer, String, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class PassingStats(Base):
    __tablename__ = "passing_stats"
    __table_args__ = (
        UniqueConstraint(
            "player_name", "season", "tm", name="uq_passing_stats_player_season_tm"
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
    qb_rec: Mapped[Optional[str]] = mapped_column(String(16))

    cmp: Mapped[Optional[int]] = mapped_column(Integer)
    att: Mapped[Optional[int]] = mapped_column(Integer)
    cmp_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    yds: Mapped[Optional[int]] = mapped_column(Integer)
    td: Mapped[Optional[int]] = mapped_column(Integer)
    td_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    ints: Mapped[Optional[int]] = mapped_column(Integer)
    int_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    first_downs: Mapped[Optional[int]] = mapped_column(Integer)
    succ_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    lng: Mapped[Optional[int]] = mapped_column(Integer)
    ypa: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    ay_pa: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    ypc: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    ypg: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    qbr: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    sk: Mapped[Optional[int]] = mapped_column(Integer)
    yds_sack: Mapped[Optional[int]] = mapped_column(Integer)
    sk_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 3))
    ny_pa: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    any_pa: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    four_qc: Mapped[Optional[int]] = mapped_column(Integer)
    gwd: Mapped[Optional[int]] = mapped_column(Integer)

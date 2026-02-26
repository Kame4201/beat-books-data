from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Integer, Numeric, String, UniqueConstraint
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
    season: Mapped[int | None] = mapped_column(Integer)

    rk: Mapped[int | None] = mapped_column(Integer)
    player_name: Mapped[str | None] = mapped_column(String(128))
    age: Mapped[int | None] = mapped_column(Integer)
    tm: Mapped[str | None] = mapped_column(String(64))
    pos: Mapped[str | None] = mapped_column(String(16))

    g: Mapped[int | None] = mapped_column(Integer)
    gs: Mapped[int | None] = mapped_column(Integer)
    qb_rec: Mapped[str | None] = mapped_column(String(16))

    cmp: Mapped[int | None] = mapped_column(Integer)
    att: Mapped[int | None] = mapped_column(Integer)
    cmp_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    yds: Mapped[int | None] = mapped_column(Integer)
    td: Mapped[int | None] = mapped_column(Integer)
    td_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    ints: Mapped[int | None] = mapped_column(Integer)
    int_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    first_downs: Mapped[int | None] = mapped_column(Integer)
    succ_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    lng: Mapped[int | None] = mapped_column(Integer)
    ypa: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    ay_pa: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    ypc: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    ypg: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    rate: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    qbr: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    sk: Mapped[int | None] = mapped_column(Integer)
    yds_sack: Mapped[int | None] = mapped_column(Integer)
    sk_pct: Mapped[Decimal | None] = mapped_column(Numeric(6, 3))
    ny_pa: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    any_pa: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    four_qc: Mapped[int | None] = mapped_column(Integer)
    gwd: Mapped[int | None] = mapped_column(Integer)

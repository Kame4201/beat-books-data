from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class TeamDefense(Base):
    __tablename__ = "team_defense"
    __table_args__ = (
        UniqueConstraint("tm", "season", name="uq_team_defense_tm_season"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season: Mapped[int | None] = mapped_column(Integer)

    rk: Mapped[int | None] = mapped_column(Integer)
    tm: Mapped[str | None] = mapped_column(String(64))
    g: Mapped[int | None] = mapped_column(Integer)
    pa: Mapped[int | None] = mapped_column(Integer)
    yds: Mapped[int | None] = mapped_column(Integer)
    ply: Mapped[int | None] = mapped_column(Integer)
    ypp: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    turnovers: Mapped[int | None] = mapped_column(Integer)
    fl: Mapped[int | None] = mapped_column(Integer)
    firstd_total: Mapped[int | None] = mapped_column(Integer)
    cmp: Mapped[int | None] = mapped_column(Integer)
    att_pass: Mapped[int | None] = mapped_column(Integer)
    yds_pass: Mapped[int | None] = mapped_column(Integer)
    td_pass: Mapped[int | None] = mapped_column(Integer)
    ints: Mapped[int | None] = mapped_column(Integer)
    nypa: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    firstd_pass: Mapped[int | None] = mapped_column(Integer)
    att_rush: Mapped[int | None] = mapped_column(Integer)
    yds_rush: Mapped[int | None] = mapped_column(Integer)
    td_rush: Mapped[int | None] = mapped_column(Integer)
    ypa: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    firstd_rush: Mapped[int | None] = mapped_column(Integer)
    pen: Mapped[int | None] = mapped_column(Integer)
    yds_pen: Mapped[int | None] = mapped_column(Integer)
    firstpy: Mapped[int | None] = mapped_column(Integer)
    sc_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    to_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    depa: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))

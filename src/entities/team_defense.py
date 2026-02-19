from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import Integer, String, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class TeamDefense(Base):
    __tablename__ = "team_defense"
    __table_args__ = (
        UniqueConstraint("tm", "season", name="uq_team_defense_tm_season"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season: Mapped[Optional[int]] = mapped_column(Integer)

    rk: Mapped[Optional[int]] = mapped_column(Integer)
    tm: Mapped[Optional[str]] = mapped_column(String(64))
    g: Mapped[Optional[int]] = mapped_column(Integer)
    pa: Mapped[Optional[int]] = mapped_column(Integer)
    yds: Mapped[Optional[int]] = mapped_column(Integer)
    ply: Mapped[Optional[int]] = mapped_column(Integer)
    ypp: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    turnovers: Mapped[Optional[int]] = mapped_column(Integer)
    fl: Mapped[Optional[int]] = mapped_column(Integer)
    firstd_total: Mapped[Optional[int]] = mapped_column(Integer)
    cmp: Mapped[Optional[int]] = mapped_column(Integer)
    att_pass: Mapped[Optional[int]] = mapped_column(Integer)
    yds_pass: Mapped[Optional[int]] = mapped_column(Integer)
    td_pass: Mapped[Optional[int]] = mapped_column(Integer)
    ints: Mapped[Optional[int]] = mapped_column(Integer)
    nypa: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    firstd_pass: Mapped[Optional[int]] = mapped_column(Integer)
    att_rush: Mapped[Optional[int]] = mapped_column(Integer)
    yds_rush: Mapped[Optional[int]] = mapped_column(Integer)
    td_rush: Mapped[Optional[int]] = mapped_column(Integer)
    ypa: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    firstd_rush: Mapped[Optional[int]] = mapped_column(Integer)
    pen: Mapped[Optional[int]] = mapped_column(Integer)
    yds_pen: Mapped[Optional[int]] = mapped_column(Integer)
    firstpy: Mapped[Optional[int]] = mapped_column(Integer)
    sc_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    to_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    depa: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2))

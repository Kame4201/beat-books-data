from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import Integer, String, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Punting(Base):
    __tablename__ = "punting"
    __table_args__ = (UniqueConstraint("tm", "season", name="uq_punting_tm_season"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season: Mapped[Optional[int]] = mapped_column(Integer)

    rk: Mapped[Optional[int]] = mapped_column(Integer)
    tm: Mapped[Optional[str]] = mapped_column(String(64))
    g: Mapped[Optional[int]] = mapped_column(Integer)

    pnt: Mapped[Optional[int]] = mapped_column(Integer)
    yds: Mapped[Optional[int]] = mapped_column(Integer)
    ypp: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    retyds: Mapped[Optional[int]] = mapped_column(Integer)
    net: Mapped[Optional[int]] = mapped_column(Integer)
    nyp: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    lng: Mapped[Optional[int]] = mapped_column(Integer)
    tb: Mapped[Optional[int]] = mapped_column(Integer)
    tb_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    in20: Mapped[Optional[int]] = mapped_column(Integer)
    in20_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    blck: Mapped[Optional[int]] = mapped_column(Integer)

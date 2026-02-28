from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Punting(Base):
    __tablename__ = "punting"
    __table_args__ = (UniqueConstraint("tm", "season", name="uq_punting_tm_season"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season: Mapped[int | None] = mapped_column(Integer)

    rk: Mapped[int | None] = mapped_column(Integer)
    tm: Mapped[str | None] = mapped_column(String(64))
    g: Mapped[int | None] = mapped_column(Integer)

    pnt: Mapped[int | None] = mapped_column(Integer)
    yds: Mapped[int | None] = mapped_column(Integer)
    ypp: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    retyds: Mapped[int | None] = mapped_column(Integer)
    net: Mapped[int | None] = mapped_column(Integer)
    nyp: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    lng: Mapped[int | None] = mapped_column(Integer)
    tb: Mapped[int | None] = mapped_column(Integer)
    tb_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    in20: Mapped[int | None] = mapped_column(Integer)
    in20_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    blck: Mapped[int | None] = mapped_column(Integer)

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Standings(Base):
    __tablename__ = "standings"
    __table_args__ = (UniqueConstraint("tm", "season", name="uq_standings_tm_season"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season: Mapped[int | None] = mapped_column(Integer)

    tm: Mapped[str | None] = mapped_column(String(64))
    w: Mapped[int | None] = mapped_column(Integer)
    losses: Mapped[int | None] = mapped_column("l", Integer)
    t: Mapped[int | None] = mapped_column(Integer)
    win_pct: Mapped[Decimal | None] = mapped_column(Numeric(6, 3))
    pf: Mapped[int | None] = mapped_column(Integer)
    pa: Mapped[int | None] = mapped_column(Integer)
    pd: Mapped[int | None] = mapped_column(Integer)
    mov: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    sos: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    srs: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    osrs: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    dsrs: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))

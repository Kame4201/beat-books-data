from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import Integer, String, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Standings(Base):
    __tablename__ = "standings"
    __table_args__ = (UniqueConstraint("tm", "season", name="uq_standings_tm_season"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season: Mapped[Optional[int]] = mapped_column(Integer)

    tm: Mapped[Optional[str]] = mapped_column(String(64))
    w: Mapped[Optional[int]] = mapped_column(Integer)
    l: Mapped[Optional[int]] = mapped_column(Integer)  # noqa: E741
    t: Mapped[Optional[int]] = mapped_column(Integer)
    win_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 3))
    pf: Mapped[Optional[int]] = mapped_column(Integer)
    pa: Mapped[Optional[int]] = mapped_column(Integer)
    pd: Mapped[Optional[int]] = mapped_column(Integer)
    mov: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    sos: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    srs: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    osrs: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    dsrs: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import Integer, String, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class TeamReturns(Base):
    __tablename__ = "returns"
    __table_args__ = (UniqueConstraint("tm", "season", name="uq_returns_tm_season"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season: Mapped[Optional[int]] = mapped_column(Integer)

    rk: Mapped[Optional[int]] = mapped_column(Integer)
    tm: Mapped[Optional[str]] = mapped_column(String(64))
    g: Mapped[Optional[int]] = mapped_column(Integer)

    ret_punt: Mapped[Optional[int]] = mapped_column(Integer)
    yds_punt: Mapped[Optional[int]] = mapped_column(Integer)
    td_punt: Mapped[Optional[int]] = mapped_column(Integer)
    lng_punt: Mapped[Optional[int]] = mapped_column(Integer)
    ypr_punt: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))

    ret_kick: Mapped[Optional[int]] = mapped_column(Integer)
    yds_kick: Mapped[Optional[int]] = mapped_column(Integer)
    td_kick: Mapped[Optional[int]] = mapped_column(Integer)
    lng_kick: Mapped[Optional[int]] = mapped_column(Integer)
    ypr_kick: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))

    apyd: Mapped[Optional[int]] = mapped_column(Integer)

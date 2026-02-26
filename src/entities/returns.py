from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class TeamReturns(Base):
    __tablename__ = "returns"
    __table_args__ = (UniqueConstraint("tm", "season", name="uq_returns_tm_season"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season: Mapped[int | None] = mapped_column(Integer)

    rk: Mapped[int | None] = mapped_column(Integer)
    tm: Mapped[str | None] = mapped_column(String(64))
    g: Mapped[int | None] = mapped_column(Integer)

    ret_punt: Mapped[int | None] = mapped_column(Integer)
    yds_punt: Mapped[int | None] = mapped_column(Integer)
    td_punt: Mapped[int | None] = mapped_column(Integer)
    lng_punt: Mapped[int | None] = mapped_column(Integer)
    ypr_punt: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))

    ret_kick: Mapped[int | None] = mapped_column(Integer)
    yds_kick: Mapped[int | None] = mapped_column(Integer)
    td_kick: Mapped[int | None] = mapped_column(Integer)
    lng_kick: Mapped[int | None] = mapped_column(Integer)
    ypr_kick: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))

    apyd: Mapped[int | None] = mapped_column(Integer)

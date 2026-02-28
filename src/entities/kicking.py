from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Kicking(Base):
    __tablename__ = "kicking"
    __table_args__ = (UniqueConstraint("tm", "season", name="uq_kicking_tm_season"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season: Mapped[int | None] = mapped_column(Integer)

    rk: Mapped[int | None] = mapped_column(Integer)
    tm: Mapped[str | None] = mapped_column(String(64))
    g: Mapped[int | None] = mapped_column(Integer)

    fga_0_19: Mapped[int | None] = mapped_column(Integer)
    fgm_0_19: Mapped[int | None] = mapped_column(Integer)
    fga_20_29: Mapped[int | None] = mapped_column(Integer)
    fgm_20_29: Mapped[int | None] = mapped_column(Integer)
    fga_30_39: Mapped[int | None] = mapped_column(Integer)
    fgm_30_39: Mapped[int | None] = mapped_column(Integer)
    fga_40_49: Mapped[int | None] = mapped_column(Integer)
    fgm_40_49: Mapped[int | None] = mapped_column(Integer)
    fga_50_plus: Mapped[int | None] = mapped_column(Integer)
    fgm_50_plus: Mapped[int | None] = mapped_column(Integer)

    fga: Mapped[int | None] = mapped_column(Integer)
    fgm: Mapped[int | None] = mapped_column(Integer)

    lng: Mapped[int | None] = mapped_column(Integer)
    fg_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    xpa: Mapped[int | None] = mapped_column(Integer)
    xpm: Mapped[int | None] = mapped_column(Integer)
    xp_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))

    ko: Mapped[int | None] = mapped_column(Integer)
    ko_yds: Mapped[int | None] = mapped_column(Integer)
    tb: Mapped[int | None] = mapped_column(Integer)
    tb_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    ko_avg: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))

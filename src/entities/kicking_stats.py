from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import Integer, String, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class KickingStats(Base):
    __tablename__ = "kicking_stats"
    __table_args__ = (
        UniqueConstraint(
            "player_name", "season", "tm", name="uq_kicking_stats_player_season_tm"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season: Mapped[Optional[int]] = mapped_column(Integer)

    rk: Mapped[Optional[int]] = mapped_column(Integer)
    player_name: Mapped[Optional[str]] = mapped_column(String(128))
    age: Mapped[Optional[int]] = mapped_column(Integer)
    tm: Mapped[Optional[str]] = mapped_column(String(64))
    pos: Mapped[Optional[str]] = mapped_column(String(16))

    g: Mapped[Optional[int]] = mapped_column(Integer)
    gs: Mapped[Optional[int]] = mapped_column(Integer)

    fga_0_19: Mapped[Optional[int]] = mapped_column(Integer)
    fgm_0_19: Mapped[Optional[int]] = mapped_column(Integer)
    fga_20_29: Mapped[Optional[int]] = mapped_column(Integer)
    fgm_20_29: Mapped[Optional[int]] = mapped_column(Integer)
    fga_30_39: Mapped[Optional[int]] = mapped_column(Integer)
    fgm_30_39: Mapped[Optional[int]] = mapped_column(Integer)
    fga_40_49: Mapped[Optional[int]] = mapped_column(Integer)
    fgm_40_49: Mapped[Optional[int]] = mapped_column(Integer)
    fga_50_plus: Mapped[Optional[int]] = mapped_column(Integer)
    fgm_50_plus: Mapped[Optional[int]] = mapped_column(Integer)

    fga: Mapped[Optional[int]] = mapped_column(Integer)
    fgm: Mapped[Optional[int]] = mapped_column(Integer)

    lng: Mapped[Optional[int]] = mapped_column(Integer)
    fg_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    xpa: Mapped[Optional[int]] = mapped_column(Integer)
    xpm: Mapped[Optional[int]] = mapped_column(Integer)
    xp_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))

    ko: Mapped[Optional[int]] = mapped_column(Integer)
    ko_yds: Mapped[Optional[int]] = mapped_column(Integer)
    tb: Mapped[Optional[int]] = mapped_column(Integer)
    tb_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    ko_avg: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))

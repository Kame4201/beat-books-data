from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import Integer, String, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ReturnStats(Base):
    __tablename__ = "return_stats"
    __table_args__ = (
        UniqueConstraint(
            "player_name", "season", "tm", name="uq_return_stats_player_season_tm"
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

    pr: Mapped[Optional[int]] = mapped_column(Integer)
    pr_yds: Mapped[Optional[int]] = mapped_column(Integer)
    pr_td: Mapped[Optional[int]] = mapped_column(Integer)
    pr_lng: Mapped[Optional[int]] = mapped_column(Integer)
    pr_ypr: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))

    kr: Mapped[Optional[int]] = mapped_column(Integer)
    kr_yds: Mapped[Optional[int]] = mapped_column(Integer)
    kr_td: Mapped[Optional[int]] = mapped_column(Integer)
    kr_lng: Mapped[Optional[int]] = mapped_column(Integer)
    kr_ypr: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))

    apyd: Mapped[Optional[int]] = mapped_column(Integer)
    awards: Mapped[Optional[str]] = mapped_column(String(128))

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import Integer, String, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ScoringStats(Base):
    __tablename__ = "scoring_stats"
    __table_args__ = (
        UniqueConstraint(
            "player_name", "season", "tm", name="uq_scoring_stats_player_season_tm"
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

    rush_td: Mapped[Optional[int]] = mapped_column(Integer)
    rec_td: Mapped[Optional[int]] = mapped_column(Integer)
    pr_td: Mapped[Optional[int]] = mapped_column(Integer)
    kr_td: Mapped[Optional[int]] = mapped_column(Integer)
    fr_td: Mapped[Optional[int]] = mapped_column(Integer)
    int_td: Mapped[Optional[int]] = mapped_column(Integer)
    oth_td: Mapped[Optional[int]] = mapped_column(Integer)
    all_td: Mapped[Optional[int]] = mapped_column(Integer)

    two_pm: Mapped[Optional[int]] = mapped_column(Integer)
    d2p: Mapped[Optional[int]] = mapped_column(Integer)

    xpm: Mapped[Optional[int]] = mapped_column(Integer)
    xpa: Mapped[Optional[int]] = mapped_column(Integer)
    fgm: Mapped[Optional[int]] = mapped_column(Integer)
    fga: Mapped[Optional[int]] = mapped_column(Integer)
    sfty: Mapped[Optional[int]] = mapped_column(Integer)
    pts: Mapped[Optional[int]] = mapped_column(Integer)
    pts_pg: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    awards: Mapped[Optional[str]] = mapped_column(String(128))

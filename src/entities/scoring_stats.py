from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Integer, Numeric, String, UniqueConstraint
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
    season: Mapped[int | None] = mapped_column(Integer)

    rk: Mapped[int | None] = mapped_column(Integer)
    player_name: Mapped[str | None] = mapped_column(String(128))
    age: Mapped[int | None] = mapped_column(Integer)
    tm: Mapped[str | None] = mapped_column(String(64))
    pos: Mapped[str | None] = mapped_column(String(16))

    g: Mapped[int | None] = mapped_column(Integer)
    gs: Mapped[int | None] = mapped_column(Integer)

    rush_td: Mapped[int | None] = mapped_column(Integer)
    rec_td: Mapped[int | None] = mapped_column(Integer)
    pr_td: Mapped[int | None] = mapped_column(Integer)
    kr_td: Mapped[int | None] = mapped_column(Integer)
    fr_td: Mapped[int | None] = mapped_column(Integer)
    int_td: Mapped[int | None] = mapped_column(Integer)
    oth_td: Mapped[int | None] = mapped_column(Integer)
    all_td: Mapped[int | None] = mapped_column(Integer)

    two_pm: Mapped[int | None] = mapped_column(Integer)
    d2p: Mapped[int | None] = mapped_column(Integer)

    xpm: Mapped[int | None] = mapped_column(Integer)
    xpa: Mapped[int | None] = mapped_column(Integer)
    fgm: Mapped[int | None] = mapped_column(Integer)
    fga: Mapped[int | None] = mapped_column(Integer)
    sfty: Mapped[int | None] = mapped_column(Integer)
    pts: Mapped[int | None] = mapped_column(Integer)
    pts_pg: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    awards: Mapped[str | None] = mapped_column(String(128))

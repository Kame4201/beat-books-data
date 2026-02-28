from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Integer, Numeric, String, UniqueConstraint
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
    season: Mapped[int | None] = mapped_column(Integer)

    rk: Mapped[int | None] = mapped_column(Integer)
    player_name: Mapped[str | None] = mapped_column(String(128))
    age: Mapped[int | None] = mapped_column(Integer)
    tm: Mapped[str | None] = mapped_column(String(64))
    pos: Mapped[str | None] = mapped_column(String(16))

    g: Mapped[int | None] = mapped_column(Integer)
    gs: Mapped[int | None] = mapped_column(Integer)

    pr: Mapped[int | None] = mapped_column(Integer)
    pr_yds: Mapped[int | None] = mapped_column(Integer)
    pr_td: Mapped[int | None] = mapped_column(Integer)
    pr_lng: Mapped[int | None] = mapped_column(Integer)
    pr_ypr: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))

    kr: Mapped[int | None] = mapped_column(Integer)
    kr_yds: Mapped[int | None] = mapped_column(Integer)
    kr_td: Mapped[int | None] = mapped_column(Integer)
    kr_lng: Mapped[int | None] = mapped_column(Integer)
    kr_ypr: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))

    apyd: Mapped[int | None] = mapped_column(Integer)
    awards: Mapped[str | None] = mapped_column(String(128))

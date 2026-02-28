from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ReceivingStats(Base):
    __tablename__ = "receiving_stats"
    __table_args__ = (
        UniqueConstraint(
            "player_name", "season", "tm", name="uq_receiving_stats_player_season_tm"
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

    tgt: Mapped[int | None] = mapped_column(Integer)
    rec: Mapped[int | None] = mapped_column(Integer)
    yds: Mapped[int | None] = mapped_column(Integer)
    ypr: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    td: Mapped[int | None] = mapped_column(Integer)
    first_downs: Mapped[int | None] = mapped_column(Integer)
    succ_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    lng: Mapped[int | None] = mapped_column(Integer)
    rpg: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    ypg: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    catch_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    ypt: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    fmb: Mapped[int | None] = mapped_column(Integer)

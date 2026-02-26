"""SQLAlchemy entity for odds data."""

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)

from src.entities.base import Base


class Odds(Base):
    """
    Stores betting odds/lines from various sportsbooks.
    Tracks opening lines, closing lines, and line movements over time.
    """

    __tablename__ = "odds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    season = Column(Integer, nullable=False)
    week = Column(Integer, nullable=False)
    game_date = Column(Date, nullable=False)

    home_team = Column(String(64), nullable=False)
    away_team = Column(String(64), nullable=False)
    sportsbook = Column(String(64), nullable=False)

    # Spread (e.g., -7.5 for home team, +7.5 for away team)
    spread_home = Column(Numeric(5, 2))
    spread_away = Column(Numeric(5, 2))

    # Moneyline (e.g., -150, +130)
    moneyline_home = Column(Integer)
    moneyline_away = Column(Integer)

    # Over/Under total points
    over_under = Column(Numeric(5, 2))

    # Timestamp when this line was recorded
    timestamp = Column(DateTime, nullable=False)

    # Track opening vs closing lines
    is_opening = Column(Boolean, default=False)
    is_closing = Column(Boolean, default=False)

    # Ensure uniqueness per game/sportsbook/timestamp
    __table_args__ = (
        UniqueConstraint(
            "season",
            "week",
            "home_team",
            "sportsbook",
            "timestamp",
            name="uq_odds_game_sportsbook_timestamp",
        ),
    )

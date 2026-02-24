"""
Entity for tracking game weather conditions.
"""

from __future__ import annotations

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime
from src.entities.base import Base


class GameWeather(Base):
    """
    Tracks weather conditions for NFL games.

    Weather data is particularly relevant for outdoor stadiums
    as it can impact game performance and outcomes.
    """

    __tablename__ = "game_weather"

    id = Column(Integer, primary_key=True, autoincrement=True)
    season = Column(Integer, nullable=False, index=True)
    week = Column(Integer, nullable=False, index=True)
    home_team = Column(String(10), nullable=False, index=True)
    stadium = Column(String(255), nullable=True)
    is_dome = Column(Boolean, nullable=False, default=False)

    # Weather conditions (null for domed stadiums)
    temperature = Column(Float, nullable=True)  # Fahrenheit
    wind_speed = Column(Float, nullable=True)  # mph
    precipitation = Column(Float, nullable=True)  # inches
    humidity = Column(Float, nullable=True)  # percentage
    weather_condition = Column(
        String(100), nullable=True
    )  # clear, cloudy, rain, snow, etc.

    # Metadata
    game_time = Column(DateTime, nullable=True)  # Scheduled game time
    fetched_at = Column(
        DateTime, nullable=False, default=datetime.now
    )  # When weather was fetched

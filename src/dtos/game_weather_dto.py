"""
DTOs for game weather operations.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class GameWeatherCreate(BaseModel):
    """DTO for creating game weather records."""

    season: int = Field(..., gt=1900, description="NFL season year")
    week: int = Field(
        ..., ge=0, le=22, description="Week number (0-22, includes playoffs)"
    )
    home_team: str = Field(
        ..., min_length=2, max_length=10, description="Home team abbreviation"
    )
    stadium: Optional[str] = Field(None, max_length=255, description="Stadium name")
    is_dome: bool = Field(False, description="Whether stadium is domed/indoor")
    temperature: Optional[float] = Field(None, description="Temperature in Fahrenheit")
    wind_speed: Optional[float] = Field(None, ge=0, description="Wind speed in mph")
    precipitation: Optional[float] = Field(
        None, ge=0, description="Precipitation in inches"
    )
    humidity: Optional[float] = Field(
        None, ge=0, le=100, description="Humidity percentage"
    )
    weather_condition: Optional[str] = Field(
        None, max_length=100, description="Weather description"
    )
    game_time: Optional[datetime] = Field(None, description="Scheduled game time")
    fetched_at: Optional[datetime] = Field(
        default_factory=datetime.now, description="When weather was fetched"
    )


class GameWeatherRead(BaseModel):
    """DTO for reading game weather data."""

    id: int
    season: int
    week: int
    home_team: str
    stadium: Optional[str]
    is_dome: bool
    temperature: Optional[float]
    wind_speed: Optional[float]
    precipitation: Optional[float]
    humidity: Optional[float]
    weather_condition: Optional[str]
    game_time: Optional[datetime]
    fetched_at: datetime

    class Config:
        from_attributes = True

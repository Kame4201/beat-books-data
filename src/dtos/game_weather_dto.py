"""
DTOs for game weather operations.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GameWeatherCreate(BaseModel):
    """DTO for creating game weather records."""

    season: int = Field(..., gt=1900, description="NFL season year")
    week: int = Field(
        ..., ge=0, le=22, description="Week number (0-22, includes playoffs)"
    )
    home_team: str = Field(
        ..., min_length=2, max_length=10, description="Home team abbreviation"
    )
    stadium: str | None = Field(
        default=None, max_length=255, description="Stadium name"
    )
    is_dome: bool = Field(default=False, description="Whether stadium is domed/indoor")
    temperature: float | None = Field(
        default=None, description="Temperature in Fahrenheit"
    )
    wind_speed: float | None = Field(
        default=None, ge=0, description="Wind speed in mph"
    )
    precipitation: float | None = Field(
        default=None, ge=0, description="Precipitation in inches"
    )
    humidity: float | None = Field(
        default=None, ge=0, le=100, description="Humidity percentage"
    )
    weather_condition: str | None = Field(
        default=None, max_length=100, description="Weather description"
    )
    game_time: datetime | None = Field(default=None, description="Scheduled game time")
    fetched_at: datetime | None = Field(
        default_factory=datetime.now, description="When weather was fetched"
    )


class GameWeatherRead(BaseModel):
    """DTO for reading game weather data."""

    id: int
    season: int
    week: int
    home_team: str
    stadium: str | None
    is_dome: bool
    temperature: float | None
    wind_speed: float | None
    precipitation: float | None
    humidity: float | None
    weather_condition: str | None
    game_time: datetime | None
    fetched_at: datetime

    model_config = ConfigDict(from_attributes=True)

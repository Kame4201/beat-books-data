"""
DTOs for games operations.
"""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class GamesCreate(BaseModel):
    """DTO for creating games records."""

    season: int = Field(..., ge=1920, le=2100, description="Season year")

    week: int | None = Field(None, ge=0, description="Week number")
    game_day: str | None = Field(None, max_length=16, description="Day of week")
    game_date: date | None = Field(None, description="Game date")
    kickoff_time: str | None = Field(None, max_length=16, description="Kickoff time")
    winner: str | None = Field(None, max_length=64, description="Winning team")
    loser: str | None = Field(None, max_length=64, description="Losing team")
    boxscore: str | None = Field(None, max_length=128, description="Boxscore link")
    pts_w: int | None = Field(None, ge=0, description="Points by winner")
    pts_l: int | None = Field(None, ge=0, description="Points by loser")
    yds_w: int | None = Field(None, ge=0, description="Yards by winner")
    to_w: int | None = Field(None, ge=0, description="Turnovers by winner")
    yds_l: int | None = Field(None, ge=0, description="Yards by loser")
    to_l: int | None = Field(None, ge=0, description="Turnovers by loser")


class GamesResponse(GamesCreate):
    """DTO for games response."""

    id: int = Field(..., description="Record ID")

    model_config = ConfigDict(from_attributes=True)

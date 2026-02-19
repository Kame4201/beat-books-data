"""
DTOs for games operations.
"""

from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class GamesCreate(BaseModel):
    """DTO for creating games records."""

    season: int = Field(..., ge=1920, le=2100, description="Season year")

    week: Optional[int] = Field(None, ge=0, description="Week number")
    game_day: Optional[str] = Field(None, max_length=16, description="Day of week")
    game_date: Optional[date] = Field(None, description="Game date")
    kickoff_time: Optional[str] = Field(None, max_length=16, description="Kickoff time")
    winner: Optional[str] = Field(None, max_length=64, description="Winning team")
    loser: Optional[str] = Field(None, max_length=64, description="Losing team")
    boxscore: Optional[str] = Field(None, max_length=128, description="Boxscore link")
    pts_w: Optional[int] = Field(None, ge=0, description="Points by winner")
    pts_l: Optional[int] = Field(None, ge=0, description="Points by loser")
    yds_w: Optional[int] = Field(None, ge=0, description="Yards by winner")
    to_w: Optional[int] = Field(None, ge=0, description="Turnovers by winner")
    yds_l: Optional[int] = Field(None, ge=0, description="Yards by loser")
    to_l: Optional[int] = Field(None, ge=0, description="Turnovers by loser")


class GamesResponse(GamesCreate):
    """DTO for games response."""

    id: int = Field(..., description="Record ID")

    model_config = ConfigDict(from_attributes=True)

"""
DTOs for rushing stats operations.
"""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class RushingStatsCreate(BaseModel):
    """DTO for creating rushing stats records."""

    season: int = Field(..., ge=1920, le=2100, description="Season year")

    rk: int | None = Field(None, ge=0, description="Rank")
    player_name: str = Field(
        ..., min_length=1, max_length=128, description="Player name"
    )
    age: int | None = Field(None, ge=0, description="Player age")
    tm: str = Field(..., min_length=1, max_length=64, description="Team name")
    pos: str | None = Field(None, max_length=16, description="Position")

    g: int | None = Field(None, ge=0, description="Games played")
    gs: int | None = Field(None, ge=0, description="Games started")

    att: int | None = Field(None, ge=0, description="Rush attempts")
    yds: int | None = Field(None, ge=0, description="Rushing yards")
    td: int | None = Field(None, ge=0, description="Touchdowns")
    first_downs: int | None = Field(None, ge=0, description="First downs")
    succ_pct: Decimal | None = Field(
        None, ge=0, le=100, description="Success percentage"
    )
    lng: int | None = Field(None, ge=0, description="Longest rush")
    ypa: Decimal | None = Field(None, ge=0, description="Yards per attempt")
    ypg: Decimal | None = Field(None, ge=0, description="Yards per game")
    apg: Decimal | None = Field(None, ge=0, description="Attempts per game")
    fmb: int | None = Field(None, ge=0, description="Fumbles")
    awards: str | None = Field(None, max_length=128, description="Awards")


class RushingStatsResponse(RushingStatsCreate):
    """DTO for rushing stats response."""

    id: int = Field(..., description="Record ID")

    model_config = ConfigDict(from_attributes=True)

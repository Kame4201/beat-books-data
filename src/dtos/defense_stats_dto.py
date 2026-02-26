"""
DTOs for defense stats operations.
"""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class DefenseStatsCreate(BaseModel):
    """DTO for creating defense stats records."""

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

    ints: int | None = Field(None, ge=0, description="Interceptions")
    int_yds: int | None = Field(None, ge=0, description="Interception yards")
    int_td: int | None = Field(None, ge=0, description="Interception touchdowns")
    int_lng: int | None = Field(None, ge=0, description="Longest interception return")
    pd: int | None = Field(None, ge=0, description="Passes defended")
    ff: int | None = Field(None, ge=0, description="Forced fumbles")
    fmb: int | None = Field(None, ge=0, description="Fumbles")
    fr: int | None = Field(None, ge=0, description="Fumbles recovered")
    fr_yds: int | None = Field(None, ge=0, description="Fumble recovery yards")
    fr_td: int | None = Field(None, ge=0, description="Fumble recovery touchdowns")

    sk: Decimal | None = Field(None, ge=0, description="Sacks")
    comb: int | None = Field(None, ge=0, description="Combined tackles")
    solo: int | None = Field(None, ge=0, description="Solo tackles")
    ast: int | None = Field(None, ge=0, description="Assisted tackles")
    tfl: int | None = Field(None, ge=0, description="Tackles for loss")
    qb_hits: int | None = Field(None, ge=0, description="QB hits")
    sfty: int | None = Field(None, ge=0, description="Safeties")


class DefenseStatsResponse(DefenseStatsCreate):
    """DTO for defense stats response."""

    id: int = Field(..., description="Record ID")

    model_config = ConfigDict(from_attributes=True)

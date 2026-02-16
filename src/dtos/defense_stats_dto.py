"""
DTOs for defense stats operations.
"""
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class DefenseStatsCreate(BaseModel):
    """DTO for creating defense stats records."""
    season: int = Field(..., ge=1920, le=2100, description="Season year")

    rk: Optional[int] = Field(None, ge=0, description="Rank")
    player_name: str = Field(..., min_length=1, max_length=128, description="Player name")
    age: Optional[int] = Field(None, ge=0, description="Player age")
    tm: str = Field(..., min_length=1, max_length=64, description="Team name")
    pos: Optional[str] = Field(None, max_length=16, description="Position")
    g: Optional[int] = Field(None, ge=0, description="Games played")
    gs: Optional[int] = Field(None, ge=0, description="Games started")

    ints: Optional[int] = Field(None, ge=0, description="Interceptions")
    int_yds: Optional[int] = Field(None, ge=0, description="Interception yards")
    int_td: Optional[int] = Field(None, ge=0, description="Interception touchdowns")
    int_lng: Optional[int] = Field(None, ge=0, description="Longest interception return")
    pd: Optional[int] = Field(None, ge=0, description="Passes defended")
    ff: Optional[int] = Field(None, ge=0, description="Forced fumbles")
    fmb: Optional[int] = Field(None, ge=0, description="Fumbles")
    fr: Optional[int] = Field(None, ge=0, description="Fumbles recovered")
    fr_yds: Optional[int] = Field(None, ge=0, description="Fumble recovery yards")
    fr_td: Optional[int] = Field(None, ge=0, description="Fumble recovery touchdowns")

    sk: Optional[Decimal] = Field(None, ge=0, description="Sacks")
    comb: Optional[int] = Field(None, ge=0, description="Combined tackles")
    solo: Optional[int] = Field(None, ge=0, description="Solo tackles")
    ast: Optional[int] = Field(None, ge=0, description="Assisted tackles")
    tfl: Optional[int] = Field(None, ge=0, description="Tackles for loss")
    qb_hits: Optional[int] = Field(None, ge=0, description="QB hits")
    sfty: Optional[int] = Field(None, ge=0, description="Safeties")


class DefenseStatsResponse(DefenseStatsCreate):
    """DTO for defense stats response."""
    id: int = Field(..., description="Record ID")

    class Config:
        from_attributes = True

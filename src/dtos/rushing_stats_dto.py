"""
DTOs for rushing stats operations.
"""
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class RushingStatsCreate(BaseModel):
    """DTO for creating rushing stats records."""
    season: int = Field(..., ge=1920, le=2100, description="Season year")

    rk: Optional[int] = Field(None, ge=0, description="Rank")
    player_name: str = Field(..., min_length=1, max_length=128, description="Player name")
    age: Optional[int] = Field(None, ge=0, description="Player age")
    tm: str = Field(..., min_length=1, max_length=64, description="Team name")
    pos: Optional[str] = Field(None, max_length=16, description="Position")

    g: Optional[int] = Field(None, ge=0, description="Games played")
    gs: Optional[int] = Field(None, ge=0, description="Games started")

    att: Optional[int] = Field(None, ge=0, description="Rush attempts")
    yds: Optional[int] = Field(None, ge=0, description="Rushing yards")
    td: Optional[int] = Field(None, ge=0, description="Touchdowns")
    first_downs: Optional[int] = Field(None, ge=0, description="First downs")
    succ_pct: Optional[Decimal] = Field(None, ge=0, le=100, description="Success percentage")
    lng: Optional[int] = Field(None, ge=0, description="Longest rush")
    ypa: Optional[Decimal] = Field(None, ge=0, description="Yards per attempt")
    ypg: Optional[Decimal] = Field(None, ge=0, description="Yards per game")
    apg: Optional[Decimal] = Field(None, ge=0, description="Attempts per game")
    fmb: Optional[int] = Field(None, ge=0, description="Fumbles")
    awards: Optional[str] = Field(None, max_length=128, description="Awards")


class RushingStatsResponse(RushingStatsCreate):
    """DTO for rushing stats response."""
    id: int = Field(..., description="Record ID")

    class Config:
        from_attributes = True

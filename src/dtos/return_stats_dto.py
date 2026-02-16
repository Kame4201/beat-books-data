"""
DTOs for return stats operations.
"""
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class ReturnStatsCreate(BaseModel):
    """DTO for creating return stats records."""
    season: int = Field(..., ge=1920, le=2100, description="Season year")

    rk: Optional[int] = Field(None, ge=0, description="Rank")
    player_name: str = Field(..., min_length=1, max_length=128, description="Player name")
    age: Optional[int] = Field(None, ge=0, description="Player age")
    tm: str = Field(..., min_length=1, max_length=64, description="Team name")
    pos: Optional[str] = Field(None, max_length=16, description="Position")

    g: Optional[int] = Field(None, ge=0, description="Games played")
    gs: Optional[int] = Field(None, ge=0, description="Games started")

    pr: Optional[int] = Field(None, ge=0, description="Punt returns")
    pr_yds: Optional[int] = Field(None, ge=0, description="Punt return yards")
    pr_td: Optional[int] = Field(None, ge=0, description="Punt return touchdowns")
    pr_lng: Optional[int] = Field(None, ge=0, description="Longest punt return")
    pr_ypr: Optional[Decimal] = Field(None, ge=0, description="Yards per punt return")

    kr: Optional[int] = Field(None, ge=0, description="Kickoff returns")
    kr_yds: Optional[int] = Field(None, ge=0, description="Kickoff return yards")
    kr_td: Optional[int] = Field(None, ge=0, description="Kickoff return touchdowns")
    kr_lng: Optional[int] = Field(None, ge=0, description="Longest kickoff return")
    kr_ypr: Optional[Decimal] = Field(None, ge=0, description="Yards per kickoff return")

    apyd: Optional[int] = Field(None, ge=0, description="All-purpose yards")
    awards: Optional[str] = Field(None, max_length=128, description="Awards")


class ReturnStatsResponse(ReturnStatsCreate):
    """DTO for return stats response."""
    id: int = Field(..., description="Record ID")

    class Config:
        from_attributes = True

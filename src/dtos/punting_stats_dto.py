"""
DTOs for punting stats operations.
"""

from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class PuntingStatsCreate(BaseModel):
    """DTO for creating punting stats records."""

    season: int = Field(..., ge=1920, le=2100, description="Season year")

    rk: Optional[int] = Field(None, ge=0, description="Rank")
    player_name: str = Field(
        ..., min_length=1, max_length=128, description="Player name"
    )
    age: Optional[int] = Field(None, ge=0, description="Player age")
    tm: str = Field(..., min_length=1, max_length=64, description="Team name")
    pos: Optional[str] = Field(None, max_length=16, description="Position")

    g: Optional[int] = Field(None, ge=0, description="Games played")
    gs: Optional[int] = Field(None, ge=0, description="Games started")

    pnt: Optional[int] = Field(None, ge=0, description="Punts")
    yds: Optional[int] = Field(None, ge=0, description="Punt yards")
    ypp: Optional[Decimal] = Field(None, ge=0, description="Yards per punt")
    ret_yds: Optional[int] = Field(None, ge=0, description="Return yards allowed")
    net_yds: Optional[int] = Field(None, ge=0, description="Net yards")
    ny_pa: Optional[Decimal] = Field(None, ge=0, description="Net yards per punt")
    lng: Optional[int] = Field(None, ge=0, description="Longest punt")
    tb: Optional[int] = Field(None, ge=0, description="Touchbacks")
    tb_pct: Optional[Decimal] = Field(
        None, ge=0, le=100, description="Touchback percentage"
    )
    pnt20: Optional[int] = Field(None, ge=0, description="Punts inside 20")
    in20_pct: Optional[Decimal] = Field(
        None, ge=0, le=100, description="Inside 20 percentage"
    )
    blck: Optional[int] = Field(None, ge=0, description="Blocked punts")
    awards: Optional[str] = Field(None, max_length=128, description="Awards")


class PuntingStatsResponse(PuntingStatsCreate):
    """DTO for punting stats response."""

    id: int = Field(..., description="Record ID")

    model_config = ConfigDict(from_attributes=True)

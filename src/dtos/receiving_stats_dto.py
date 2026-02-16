"""
DTOs for receiving stats operations.
"""
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class ReceivingStatsCreate(BaseModel):
    """DTO for creating receiving stats records."""
    season: int = Field(..., ge=1920, le=2100, description="Season year")

    rk: Optional[int] = Field(None, ge=0, description="Rank")
    player_name: str = Field(..., min_length=1, max_length=128, description="Player name")
    age: Optional[int] = Field(None, ge=0, description="Player age")
    tm: str = Field(..., min_length=1, max_length=64, description="Team name")
    pos: Optional[str] = Field(None, max_length=16, description="Position")

    g: Optional[int] = Field(None, ge=0, description="Games played")
    gs: Optional[int] = Field(None, ge=0, description="Games started")

    tgt: Optional[int] = Field(None, ge=0, description="Targets")
    rec: Optional[int] = Field(None, ge=0, description="Receptions")
    yds: Optional[int] = Field(None, ge=0, description="Receiving yards")
    ypr: Optional[Decimal] = Field(None, ge=0, description="Yards per reception")
    td: Optional[int] = Field(None, ge=0, description="Touchdowns")
    first_downs: Optional[int] = Field(None, ge=0, description="First downs")
    succ_pct: Optional[Decimal] = Field(None, ge=0, le=100, description="Success percentage")
    lng: Optional[int] = Field(None, ge=0, description="Longest reception")
    rpg: Optional[Decimal] = Field(None, ge=0, description="Receptions per game")
    ypg: Optional[Decimal] = Field(None, ge=0, description="Yards per game")
    catch_pct: Optional[Decimal] = Field(None, ge=0, le=100, description="Catch percentage")
    ypt: Optional[Decimal] = Field(None, ge=0, description="Yards per target")
    fmb: Optional[int] = Field(None, ge=0, description="Fumbles")


class ReceivingStatsResponse(ReceivingStatsCreate):
    """DTO for receiving stats response."""
    id: int = Field(..., description="Record ID")

    class Config:
        from_attributes = True

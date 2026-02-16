"""
DTOs for standings operations.
"""
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class StandingsCreate(BaseModel):
    """DTO for creating standings records."""
    season: int = Field(..., ge=1920, le=2100, description="Season year")

    tm: str = Field(..., min_length=1, max_length=64, description="Team name")
    w: Optional[int] = Field(None, ge=0, description="Wins")
    l: Optional[int] = Field(None, ge=0, description="Losses")
    t: Optional[int] = Field(None, ge=0, description="Ties")
    win_pct: Optional[Decimal] = Field(None, ge=0, le=1, description="Win percentage")
    pf: Optional[int] = Field(None, ge=0, description="Points for")
    pa: Optional[int] = Field(None, ge=0, description="Points against")
    pd: Optional[int] = Field(None, description="Point differential")
    mov: Optional[Decimal] = Field(None, description="Margin of victory")
    sos: Optional[Decimal] = Field(None, description="Strength of schedule")
    srs: Optional[Decimal] = Field(None, description="Simple rating system")
    osrs: Optional[Decimal] = Field(None, description="Offensive SRS")
    dsrs: Optional[Decimal] = Field(None, description="Defensive SRS")


class StandingsResponse(StandingsCreate):
    """DTO for standings response."""
    id: int = Field(..., description="Record ID")

    class Config:
        from_attributes = True

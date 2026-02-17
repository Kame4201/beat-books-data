"""
DTOs for team punting operations.
"""

from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class PuntingCreate(BaseModel):
    """DTO for creating team punting records."""

    season: int = Field(..., ge=1920, le=2100, description="Season year")

    rk: Optional[int] = Field(None, ge=0, description="Rank")
    tm: str = Field(..., min_length=1, max_length=64, description="Team name")
    g: Optional[int] = Field(None, ge=0, description="Games played")

    pnt: Optional[int] = Field(None, ge=0, description="Punts")
    yds: Optional[int] = Field(None, ge=0, description="Punt yards")
    ypp: Optional[Decimal] = Field(None, ge=0, description="Yards per punt")
    retyds: Optional[int] = Field(None, ge=0, description="Return yards allowed")
    net: Optional[int] = Field(None, ge=0, description="Net yards")
    nyp: Optional[Decimal] = Field(None, ge=0, description="Net yards per punt")
    lng: Optional[int] = Field(None, ge=0, description="Longest punt")
    tb: Optional[int] = Field(None, ge=0, description="Touchbacks")
    tb_pct: Optional[Decimal] = Field(
        None, ge=0, le=100, description="Touchback percentage"
    )
    in20: Optional[int] = Field(None, ge=0, description="Punts inside 20")
    in20_pct: Optional[Decimal] = Field(
        None, ge=0, le=100, description="Inside 20 percentage"
    )
    blck: Optional[int] = Field(None, ge=0, description="Blocked punts")


class PuntingResponse(PuntingCreate):
    """DTO for team punting response."""

    id: int = Field(..., description="Record ID")

    model_config = ConfigDict(from_attributes=True)

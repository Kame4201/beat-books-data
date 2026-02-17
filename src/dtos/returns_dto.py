"""
DTOs for team returns operations.
"""

from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TeamReturnsCreate(BaseModel):
    """DTO for creating team returns records."""

    season: int = Field(..., ge=1920, le=2100, description="Season year")

    rk: Optional[int] = Field(None, ge=0, description="Rank")
    tm: str = Field(..., min_length=1, max_length=64, description="Team name")
    g: Optional[int] = Field(None, ge=0, description="Games played")

    ret_punt: Optional[int] = Field(None, ge=0, description="Punt returns")
    yds_punt: Optional[int] = Field(None, ge=0, description="Punt return yards")
    td_punt: Optional[int] = Field(None, ge=0, description="Punt return touchdowns")
    lng_punt: Optional[int] = Field(None, ge=0, description="Longest punt return")
    ypr_punt: Optional[Decimal] = Field(None, ge=0, description="Yards per punt return")

    ret_kick: Optional[int] = Field(None, ge=0, description="Kickoff returns")
    yds_kick: Optional[int] = Field(None, ge=0, description="Kickoff return yards")
    td_kick: Optional[int] = Field(None, ge=0, description="Kickoff return touchdowns")
    lng_kick: Optional[int] = Field(None, ge=0, description="Longest kickoff return")
    ypr_kick: Optional[Decimal] = Field(
        None, ge=0, description="Yards per kickoff return"
    )

    apyd: Optional[int] = Field(None, ge=0, description="All-purpose yards")


class TeamReturnsResponse(TeamReturnsCreate):
    """DTO for team returns response."""

    id: int = Field(..., description="Record ID")

    model_config = ConfigDict(from_attributes=True)

"""
DTOs for team returns operations.
"""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TeamReturnsCreate(BaseModel):
    """DTO for creating team returns records."""

    season: int = Field(..., ge=1920, le=2100, description="Season year")

    rk: int | None = Field(None, ge=0, description="Rank")
    tm: str = Field(..., min_length=1, max_length=64, description="Team name")
    g: int | None = Field(None, ge=0, description="Games played")

    ret_punt: int | None = Field(None, ge=0, description="Punt returns")
    yds_punt: int | None = Field(None, ge=0, description="Punt return yards")
    td_punt: int | None = Field(None, ge=0, description="Punt return touchdowns")
    lng_punt: int | None = Field(None, ge=0, description="Longest punt return")
    ypr_punt: Decimal | None = Field(None, ge=0, description="Yards per punt return")

    ret_kick: int | None = Field(None, ge=0, description="Kickoff returns")
    yds_kick: int | None = Field(None, ge=0, description="Kickoff return yards")
    td_kick: int | None = Field(None, ge=0, description="Kickoff return touchdowns")
    lng_kick: int | None = Field(None, ge=0, description="Longest kickoff return")
    ypr_kick: Decimal | None = Field(None, ge=0, description="Yards per kickoff return")

    apyd: int | None = Field(None, ge=0, description="All-purpose yards")


class TeamReturnsResponse(TeamReturnsCreate):
    """DTO for team returns response."""

    id: int = Field(..., description="Record ID")

    model_config = ConfigDict(from_attributes=True)

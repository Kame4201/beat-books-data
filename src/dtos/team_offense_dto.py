"""
DTOs for team offense operations.
"""

from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TeamOffenseCreate(BaseModel):
    """DTO for creating team offense records."""

    season: int = Field(..., ge=1920, le=2100, description="Season year")

    rk: Optional[int] = Field(None, ge=0, description="Rank")
    tm: str = Field(..., min_length=1, max_length=64, description="Team name")
    g: Optional[int] = Field(None, ge=0, description="Games played")
    pf: Optional[int] = Field(None, ge=0, description="Points for")
    yds: Optional[int] = Field(None, ge=0, description="Total yards")
    ply: Optional[int] = Field(None, ge=0, description="Total plays")
    ypp: Optional[Decimal] = Field(None, ge=0, description="Yards per play")
    turnovers: Optional[int] = Field(None, ge=0, description="Turnovers")
    fl: Optional[int] = Field(None, ge=0, description="Fumbles lost")
    firstd_total: Optional[int] = Field(None, ge=0, description="First downs total")

    cmp: Optional[int] = Field(None, ge=0, description="Completions")
    att_pass: Optional[int] = Field(None, ge=0, description="Pass attempts")
    yds_pass: Optional[int] = Field(None, ge=0, description="Passing yards")
    td_pass: Optional[int] = Field(None, ge=0, description="Passing touchdowns")
    ints: Optional[int] = Field(None, ge=0, description="Interceptions")
    nypa: Optional[Decimal] = Field(
        None, ge=0, description="Net yards per pass attempt"
    )
    firstd_pass: Optional[int] = Field(None, ge=0, description="First downs by passing")

    att_rush: Optional[int] = Field(None, ge=0, description="Rush attempts")
    yds_rush: Optional[int] = Field(None, ge=0, description="Rushing yards")
    td_rush: Optional[int] = Field(None, ge=0, description="Rushing touchdowns")
    ypa: Optional[Decimal] = Field(None, ge=0, description="Yards per rush attempt")
    firstd_rush: Optional[int] = Field(None, ge=0, description="First downs by rushing")

    pen: Optional[int] = Field(None, ge=0, description="Penalties")
    yds_pen: Optional[int] = Field(None, ge=0, description="Penalty yards")
    firstpy: Optional[int] = Field(None, ge=0, description="First downs by penalty")
    sc_pct: Optional[Decimal] = Field(
        None, ge=0, le=100, description="Scoring percentage"
    )
    to_pct: Optional[Decimal] = Field(
        None, ge=0, le=100, description="Turnover percentage"
    )
    opea: Optional[Decimal] = Field(None, description="Offensive expected points added")


class TeamOffenseResponse(TeamOffenseCreate):
    """DTO for team offense response."""

    id: int = Field(..., description="Record ID")

    model_config = ConfigDict(from_attributes=True)

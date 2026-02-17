"""
DTOs for team defense operations.
"""

from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TeamDefenseCreate(BaseModel):
    """DTO for creating team defense records."""

    season: int = Field(..., ge=1920, le=2100, description="Season year")

    rk: Optional[int] = Field(None, ge=0, description="Rank")
    tm: str = Field(..., min_length=1, max_length=64, description="Team name")
    g: Optional[int] = Field(None, ge=0, description="Games played")
    pa: Optional[int] = Field(None, ge=0, description="Points allowed")
    yds: Optional[int] = Field(None, ge=0, description="Total yards allowed")
    ply: Optional[int] = Field(None, ge=0, description="Plays faced")
    ypp: Optional[Decimal] = Field(None, ge=0, description="Yards per play allowed")
    turnovers: Optional[int] = Field(None, ge=0, description="Takeaways")
    fl: Optional[int] = Field(None, ge=0, description="Fumbles recovered")
    firstd_total: Optional[int] = Field(None, ge=0, description="First downs allowed")

    cmp: Optional[int] = Field(None, ge=0, description="Completions allowed")
    att_pass: Optional[int] = Field(None, ge=0, description="Pass attempts faced")
    yds_pass: Optional[int] = Field(None, ge=0, description="Passing yards allowed")
    td_pass: Optional[int] = Field(None, ge=0, description="Passing TDs allowed")
    ints: Optional[int] = Field(None, ge=0, description="Interceptions made")
    nypa: Optional[Decimal] = Field(
        None, ge=0, description="Net yards per pass attempt allowed"
    )
    firstd_pass: Optional[int] = Field(
        None, ge=0, description="First downs allowed via pass"
    )

    att_rush: Optional[int] = Field(None, ge=0, description="Rush attempts faced")
    yds_rush: Optional[int] = Field(None, ge=0, description="Rushing yards allowed")
    td_rush: Optional[int] = Field(None, ge=0, description="Rushing TDs allowed")
    ypa: Optional[Decimal] = Field(None, ge=0, description="Yards per rush allowed")
    firstd_rush: Optional[int] = Field(
        None, ge=0, description="First downs allowed via rush"
    )

    pen: Optional[int] = Field(None, ge=0, description="Penalties committed")
    yds_pen: Optional[int] = Field(None, ge=0, description="Penalty yards")
    firstpy: Optional[int] = Field(
        None, ge=0, description="First downs allowed via penalty"
    )
    sc_pct: Optional[Decimal] = Field(
        None, ge=0, le=100, description="Scoring percentage allowed"
    )
    to_pct: Optional[Decimal] = Field(
        None, ge=0, le=100, description="Turnover percentage forced"
    )
    depa: Optional[Decimal] = Field(
        None, description="Defensive expected points allowed"
    )


class TeamDefenseResponse(TeamDefenseCreate):
    """DTO for team defense response."""

    id: int = Field(..., description="Record ID")

    model_config = ConfigDict(from_attributes=True)

"""
DTOs for team offense operations.
"""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TeamOffenseCreate(BaseModel):
    """DTO for creating team offense records."""

    season: int = Field(..., ge=1920, le=2100, description="Season year")

    rk: int | None = Field(None, ge=0, description="Rank")
    tm: str = Field(..., min_length=1, max_length=64, description="Team name")
    g: int | None = Field(None, ge=0, description="Games played")
    pf: int | None = Field(None, ge=0, description="Points for")
    yds: int | None = Field(None, ge=0, description="Total yards")
    ply: int | None = Field(None, ge=0, description="Total plays")
    ypp: Decimal | None = Field(None, ge=0, description="Yards per play")
    turnovers: int | None = Field(None, ge=0, description="Turnovers")
    fl: int | None = Field(None, ge=0, description="Fumbles lost")
    firstd_total: int | None = Field(None, ge=0, description="First downs total")

    cmp: int | None = Field(None, ge=0, description="Completions")
    att_pass: int | None = Field(None, ge=0, description="Pass attempts")
    yds_pass: int | None = Field(None, ge=0, description="Passing yards")
    td_pass: int | None = Field(None, ge=0, description="Passing touchdowns")
    ints: int | None = Field(None, ge=0, description="Interceptions")
    nypa: Decimal | None = Field(None, ge=0, description="Net yards per pass attempt")
    firstd_pass: int | None = Field(None, ge=0, description="First downs by passing")

    att_rush: int | None = Field(None, ge=0, description="Rush attempts")
    yds_rush: int | None = Field(None, ge=0, description="Rushing yards")
    td_rush: int | None = Field(None, ge=0, description="Rushing touchdowns")
    ypa: Decimal | None = Field(None, ge=0, description="Yards per rush attempt")
    firstd_rush: int | None = Field(None, ge=0, description="First downs by rushing")

    pen: int | None = Field(None, ge=0, description="Penalties")
    yds_pen: int | None = Field(None, ge=0, description="Penalty yards")
    firstpy: int | None = Field(None, ge=0, description="First downs by penalty")
    sc_pct: Decimal | None = Field(None, ge=0, le=100, description="Scoring percentage")
    to_pct: Decimal | None = Field(
        None, ge=0, le=100, description="Turnover percentage"
    )
    opea: Decimal | None = Field(None, description="Offensive expected points added")


class TeamOffenseResponse(TeamOffenseCreate):
    """DTO for team offense response."""

    id: int = Field(..., description="Record ID")

    model_config = ConfigDict(from_attributes=True)

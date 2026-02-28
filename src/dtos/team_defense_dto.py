"""
DTOs for team defense operations.
"""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TeamDefenseCreate(BaseModel):
    """DTO for creating team defense records."""

    season: int = Field(..., ge=1920, le=2100, description="Season year")

    rk: int | None = Field(None, ge=0, description="Rank")
    tm: str = Field(..., min_length=1, max_length=64, description="Team name")
    g: int | None = Field(None, ge=0, description="Games played")
    pa: int | None = Field(None, ge=0, description="Points allowed")
    yds: int | None = Field(None, ge=0, description="Total yards allowed")
    ply: int | None = Field(None, ge=0, description="Plays faced")
    ypp: Decimal | None = Field(None, ge=0, description="Yards per play allowed")
    turnovers: int | None = Field(None, ge=0, description="Takeaways")
    fl: int | None = Field(None, ge=0, description="Fumbles recovered")
    firstd_total: int | None = Field(None, ge=0, description="First downs allowed")

    cmp: int | None = Field(None, ge=0, description="Completions allowed")
    att_pass: int | None = Field(None, ge=0, description="Pass attempts faced")
    yds_pass: int | None = Field(None, ge=0, description="Passing yards allowed")
    td_pass: int | None = Field(None, ge=0, description="Passing TDs allowed")
    ints: int | None = Field(None, ge=0, description="Interceptions made")
    nypa: Decimal | None = Field(
        None, ge=0, description="Net yards per pass attempt allowed"
    )
    firstd_pass: int | None = Field(
        None, ge=0, description="First downs allowed via pass"
    )

    att_rush: int | None = Field(None, ge=0, description="Rush attempts faced")
    yds_rush: int | None = Field(None, ge=0, description="Rushing yards allowed")
    td_rush: int | None = Field(None, ge=0, description="Rushing TDs allowed")
    ypa: Decimal | None = Field(None, ge=0, description="Yards per rush allowed")
    firstd_rush: int | None = Field(
        None, ge=0, description="First downs allowed via rush"
    )

    pen: int | None = Field(None, ge=0, description="Penalties committed")
    yds_pen: int | None = Field(None, ge=0, description="Penalty yards")
    firstpy: int | None = Field(
        None, ge=0, description="First downs allowed via penalty"
    )
    sc_pct: Decimal | None = Field(
        None, ge=0, le=100, description="Scoring percentage allowed"
    )
    to_pct: Decimal | None = Field(
        None, ge=0, le=100, description="Turnover percentage forced"
    )
    depa: Decimal | None = Field(None, description="Defensive expected points allowed")


class TeamDefenseResponse(TeamDefenseCreate):
    """DTO for team defense response."""

    id: int = Field(..., description="Record ID")

    model_config = ConfigDict(from_attributes=True)

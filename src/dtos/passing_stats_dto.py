"""
DTOs for passing stats operations.
"""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PassingStatsCreate(BaseModel):
    """DTO for creating passing stats records."""

    season: int = Field(..., ge=1920, le=2100, description="Season year")

    rk: int | None = Field(None, ge=0, description="Rank")
    player_name: str = Field(
        ..., min_length=1, max_length=128, description="Player name"
    )
    age: int | None = Field(None, ge=0, description="Player age")
    tm: str = Field(..., min_length=1, max_length=64, description="Team name")
    pos: str | None = Field(None, max_length=16, description="Position")

    g: int | None = Field(None, ge=0, description="Games played")
    gs: int | None = Field(None, ge=0, description="Games started")
    qb_rec: str | None = Field(None, max_length=16, description="QB record")

    cmp: int | None = Field(None, ge=0, description="Completions")
    att: int | None = Field(None, ge=0, description="Attempts")
    cmp_pct: Decimal | None = Field(
        None, ge=0, le=100, description="Completion percentage"
    )
    yds: int | None = Field(None, ge=0, description="Passing yards")
    td: int | None = Field(None, ge=0, description="Touchdowns")
    td_pct: Decimal | None = Field(
        None, ge=0, le=100, description="Touchdown percentage"
    )
    ints: int | None = Field(None, ge=0, description="Interceptions")
    int_pct: Decimal | None = Field(
        None, ge=0, le=100, description="Interception percentage"
    )
    first_downs: int | None = Field(None, ge=0, description="First downs")
    succ_pct: Decimal | None = Field(
        None, ge=0, le=100, description="Success percentage"
    )
    lng: int | None = Field(None, ge=0, description="Longest pass")
    ypa: Decimal | None = Field(None, ge=0, description="Yards per attempt")
    ay_pa: Decimal | None = Field(None, description="Adjusted yards per attempt")
    ypc: Decimal | None = Field(None, ge=0, description="Yards per completion")
    ypg: Decimal | None = Field(None, ge=0, description="Yards per game")
    rate: Decimal | None = Field(None, ge=0, description="Passer rating")
    qbr: Decimal | None = Field(None, ge=0, description="QB rating")
    sk: int | None = Field(None, ge=0, description="Sacks")
    yds_sack: int | None = Field(None, ge=0, description="Sack yards")
    sk_pct: Decimal | None = Field(None, ge=0, le=100, description="Sack percentage")
    ny_pa: Decimal | None = Field(None, description="Net yards per attempt")
    any_pa: Decimal | None = Field(None, description="Adjusted net yards per attempt")
    four_qc: int | None = Field(None, ge=0, description="Fourth quarter comebacks")
    gwd: int | None = Field(None, ge=0, description="Game winning drives")


class PassingStatsResponse(PassingStatsCreate):
    """DTO for passing stats response."""

    id: int = Field(..., description="Record ID")

    model_config = ConfigDict(from_attributes=True)

"""
DTOs for scoring stats operations.
"""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ScoringStatsCreate(BaseModel):
    """DTO for creating scoring stats records."""

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

    rush_td: int | None = Field(None, ge=0, description="Rushing touchdowns")
    rec_td: int | None = Field(None, ge=0, description="Receiving touchdowns")
    pr_td: int | None = Field(None, ge=0, description="Punt return touchdowns")
    kr_td: int | None = Field(None, ge=0, description="Kickoff return touchdowns")
    fr_td: int | None = Field(None, ge=0, description="Fumble return touchdowns")
    int_td: int | None = Field(None, ge=0, description="Interception return touchdowns")
    oth_td: int | None = Field(None, ge=0, description="Other touchdowns")
    all_td: int | None = Field(None, ge=0, description="All touchdowns")

    two_pm: int | None = Field(None, ge=0, description="Two-point conversions made")
    d2p: int | None = Field(None, ge=0, description="Defensive two-point conversions")

    xpm: int | None = Field(None, ge=0, description="Extra points made")
    xpa: int | None = Field(None, ge=0, description="Extra point attempts")
    fgm: int | None = Field(None, ge=0, description="Field goals made")
    fga: int | None = Field(None, ge=0, description="Field goal attempts")
    sfty: int | None = Field(None, ge=0, description="Safeties")
    pts: int | None = Field(None, ge=0, description="Total points")
    pts_pg: Decimal | None = Field(None, ge=0, description="Points per game")
    awards: str | None = Field(None, max_length=128, description="Awards")


class ScoringStatsResponse(ScoringStatsCreate):
    """DTO for scoring stats response."""

    id: int = Field(..., description="Record ID")

    model_config = ConfigDict(from_attributes=True)

"""
DTOs for scoring stats operations.
"""

from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ScoringStatsCreate(BaseModel):
    """DTO for creating scoring stats records."""

    season: int = Field(..., ge=1920, le=2100, description="Season year")

    rk: Optional[int] = Field(None, ge=0, description="Rank")
    player_name: str = Field(
        ..., min_length=1, max_length=128, description="Player name"
    )
    age: Optional[int] = Field(None, ge=0, description="Player age")
    tm: str = Field(..., min_length=1, max_length=64, description="Team name")
    pos: Optional[str] = Field(None, max_length=16, description="Position")

    g: Optional[int] = Field(None, ge=0, description="Games played")
    gs: Optional[int] = Field(None, ge=0, description="Games started")

    rush_td: Optional[int] = Field(None, ge=0, description="Rushing touchdowns")
    rec_td: Optional[int] = Field(None, ge=0, description="Receiving touchdowns")
    pr_td: Optional[int] = Field(None, ge=0, description="Punt return touchdowns")
    kr_td: Optional[int] = Field(None, ge=0, description="Kickoff return touchdowns")
    fr_td: Optional[int] = Field(None, ge=0, description="Fumble return touchdowns")
    int_td: Optional[int] = Field(
        None, ge=0, description="Interception return touchdowns"
    )
    oth_td: Optional[int] = Field(None, ge=0, description="Other touchdowns")
    all_td: Optional[int] = Field(None, ge=0, description="All touchdowns")

    two_pm: Optional[int] = Field(None, ge=0, description="Two-point conversions made")
    d2p: Optional[int] = Field(
        None, ge=0, description="Defensive two-point conversions"
    )

    xpm: Optional[int] = Field(None, ge=0, description="Extra points made")
    xpa: Optional[int] = Field(None, ge=0, description="Extra point attempts")
    fgm: Optional[int] = Field(None, ge=0, description="Field goals made")
    fga: Optional[int] = Field(None, ge=0, description="Field goal attempts")
    sfty: Optional[int] = Field(None, ge=0, description="Safeties")
    pts: Optional[int] = Field(None, ge=0, description="Total points")
    pts_pg: Optional[Decimal] = Field(None, ge=0, description="Points per game")
    awards: Optional[str] = Field(None, max_length=128, description="Awards")


class ScoringStatsResponse(ScoringStatsCreate):
    """DTO for scoring stats response."""

    id: int = Field(..., description="Record ID")

    model_config = ConfigDict(from_attributes=True)

"""
DTOs for return stats operations.
"""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ReturnStatsCreate(BaseModel):
    """DTO for creating return stats records."""

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

    pr: int | None = Field(None, ge=0, description="Punt returns")
    pr_yds: int | None = Field(None, ge=0, description="Punt return yards")
    pr_td: int | None = Field(None, ge=0, description="Punt return touchdowns")
    pr_lng: int | None = Field(None, ge=0, description="Longest punt return")
    pr_ypr: Decimal | None = Field(None, ge=0, description="Yards per punt return")

    kr: int | None = Field(None, ge=0, description="Kickoff returns")
    kr_yds: int | None = Field(None, ge=0, description="Kickoff return yards")
    kr_td: int | None = Field(None, ge=0, description="Kickoff return touchdowns")
    kr_lng: int | None = Field(None, ge=0, description="Longest kickoff return")
    kr_ypr: Decimal | None = Field(None, ge=0, description="Yards per kickoff return")

    apyd: int | None = Field(None, ge=0, description="All-purpose yards")
    awards: str | None = Field(None, max_length=128, description="Awards")


class ReturnStatsResponse(ReturnStatsCreate):
    """DTO for return stats response."""

    id: int = Field(..., description="Record ID")

    model_config = ConfigDict(from_attributes=True)

"""
DTOs for injury report operations.
"""

from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


class InjuryReportCreate(BaseModel):
    """DTO for creating injury report records."""

    season: int = Field(..., gt=1900, description="NFL season year")
    week: int = Field(
        ..., ge=0, le=22, description="Week number (0-22, includes playoffs)"
    )
    player_name: str = Field(
        ..., min_length=1, max_length=255, description="Player full name"
    )
    team: str = Field(..., min_length=2, max_length=10, description="Team abbreviation")
    position: Optional[str] = Field(
        None, max_length=10, description="Player position (QB, RB, etc.)"
    )
    designation: str = Field(
        ..., description="Injury designation (Questionable/Doubtful/Out/IR)"
    )
    injury_type: Optional[str] = Field(
        None, max_length=100, description="Type of injury"
    )
    report_date: Optional[date] = Field(None, description="Date of injury report")


class InjuryReportRead(BaseModel):
    """DTO for reading injury report data."""

    id: int
    season: int
    week: int
    player_name: str
    team: str
    position: Optional[str]
    designation: str
    injury_type: Optional[str]
    report_date: Optional[date]

    class Config:
        from_attributes = True

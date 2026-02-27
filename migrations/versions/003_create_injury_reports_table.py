"""create injury_reports table

Revision ID: 003
Revises: 002
Create Date: 2026-02-16 00:00:00.000000

Adds the injury_reports table to track weekly NFL injury designations
(Questionable, Doubtful, Out, IR) scraped from Pro-Football-Reference.
This data is used by the model service to factor injury impact into predictions.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the injury_reports table and indexes.

    Columns match src/entities/injury_report.py InjuryReport entity.
    Indexes on season, week, player_name, and team support common query patterns
    (e.g., "all injuries for week 5" or "all injuries for the Bills").
    """
    op.create_table(
        "injury_reports",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("season", sa.Integer(), nullable=False),
        sa.Column("week", sa.Integer(), nullable=False),
        sa.Column("player_name", sa.String(255), nullable=False),
        sa.Column("team", sa.String(10), nullable=False),
        sa.Column("position", sa.String(10), nullable=True),
        sa.Column("designation", sa.String(50), nullable=False),
        sa.Column("injury_type", sa.String(100), nullable=True),
        sa.Column("report_date", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Indexes for common query patterns
    op.create_index("ix_injury_reports_season", "injury_reports", ["season"])
    op.create_index("ix_injury_reports_week", "injury_reports", ["week"])
    op.create_index(
        "ix_injury_reports_player_name", "injury_reports", ["player_name"]
    )
    op.create_index("ix_injury_reports_team", "injury_reports", ["team"])


def downgrade() -> None:
    """Drop the injury_reports table and its indexes."""
    op.drop_index("ix_injury_reports_team", table_name="injury_reports")
    op.drop_index("ix_injury_reports_player_name", table_name="injury_reports")
    op.drop_index("ix_injury_reports_week", table_name="injury_reports")
    op.drop_index("ix_injury_reports_season", table_name="injury_reports")
    op.drop_table("injury_reports")

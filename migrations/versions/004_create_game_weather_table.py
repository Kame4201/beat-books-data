"""create game_weather table

Revision ID: 004
Revises: 003
Create Date: 2026-02-16 00:00:00.000000

Adds the game_weather table to store weather conditions for NFL games.
Weather data is fetched from the OpenWeatherMap API for outdoor stadiums;
domed stadiums get a record with is_dome=True and null weather fields.
Used by the model service to factor weather impact into game predictions.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the game_weather table and indexes.

    Columns match src/entities/game_weather.py GameWeather entity.
    - Weather fields (temperature, wind_speed, etc.) are nullable for domed stadiums.
    - fetched_at defaults to CURRENT_TIMESTAMP to track data freshness.
    - Indexes on season, week, and home_team support common query patterns.
    """
    op.create_table(
        "game_weather",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("season", sa.Integer(), nullable=False),
        sa.Column("week", sa.Integer(), nullable=False),
        sa.Column("home_team", sa.String(10), nullable=False),
        sa.Column("stadium", sa.String(255), nullable=True),
        sa.Column(
            "is_dome",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column("temperature", sa.Float(), nullable=True),
        sa.Column("wind_speed", sa.Float(), nullable=True),
        sa.Column("precipitation", sa.Float(), nullable=True),
        sa.Column("humidity", sa.Float(), nullable=True),
        sa.Column("weather_condition", sa.String(100), nullable=True),
        sa.Column("game_time", sa.DateTime(), nullable=True),
        sa.Column(
            "fetched_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Indexes for common query patterns
    op.create_index("ix_game_weather_season", "game_weather", ["season"])
    op.create_index("ix_game_weather_week", "game_weather", ["week"])
    op.create_index(
        "ix_game_weather_home_team", "game_weather", ["home_team"]
    )


def downgrade() -> None:
    """Drop the game_weather table and its indexes."""
    op.drop_index("ix_game_weather_home_team", table_name="game_weather")
    op.drop_index("ix_game_weather_week", table_name="game_weather")
    op.drop_index("ix_game_weather_season", table_name="game_weather")
    op.drop_table("game_weather")

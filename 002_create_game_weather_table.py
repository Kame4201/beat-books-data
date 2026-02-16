"""create game_weather table

Revision ID: 002_game_weather
Revises: 001_injury_reports
Create Date: 2026-02-16 00:00:00.000000

NOTE: This migration file should be moved to migrations/versions/ once Alembic is set up.

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_game_weather'
down_revision: Union[str, None] = '001_injury_reports'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create game_weather table."""
    op.create_table(
        'game_weather',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('season', sa.Integer(), nullable=False),
        sa.Column('week', sa.Integer(), nullable=False),
        sa.Column('home_team', sa.String(10), nullable=False),
        sa.Column('stadium', sa.String(255), nullable=True),
        sa.Column('is_dome', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('wind_speed', sa.Float(), nullable=True),
        sa.Column('precipitation', sa.Float(), nullable=True),
        sa.Column('humidity', sa.Float(), nullable=True),
        sa.Column('weather_condition', sa.String(100), nullable=True),
        sa.Column('game_time', sa.DateTime(), nullable=True),
        sa.Column('fetched_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for common queries
    op.create_index('ix_game_weather_season', 'game_weather', ['season'])
    op.create_index('ix_game_weather_week', 'game_weather', ['week'])
    op.create_index('ix_game_weather_home_team', 'game_weather', ['home_team'])


def downgrade() -> None:
    """Drop game_weather table."""
    op.drop_index('ix_game_weather_home_team', table_name='game_weather')
    op.drop_index('ix_game_weather_week', table_name='game_weather')
    op.drop_index('ix_game_weather_season', table_name='game_weather')
    op.drop_table('game_weather')

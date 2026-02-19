"""add performance indexes

Revision ID: 002_performance_indexes
Revises: 001_initial_schema
Create Date: 2026-02-16 00:00:00.000000

This migration adds recommended database indexes for common query patterns
on NFL stats tables to improve query performance.

Indexes added:
- passing_stats: season, player_name, tm (team)
- team_offense: season
- rushing_stats: season
- receiving_stats: season
- games: composite index on (season, week)
- standings: season

These indexes are designed to optimize common queries such as:
- Filtering stats by season
- Looking up player stats by name
- Filtering team stats
- Querying games by season and week
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_performance_indexes'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add performance indexes to NFL stats tables."""

    # Passing stats indexes - season, player lookup, and team filtering
    op.create_index(
        'idx_passing_stats_season',
        'passing_stats',
        ['season'],
        unique=False
    )
    op.create_index(
        'idx_passing_stats_player',
        'passing_stats',
        ['player_name'],
        unique=False
    )
    op.create_index(
        'idx_passing_stats_team',
        'passing_stats',
        ['tm'],
        unique=False
    )

    # Team offense index - season filtering
    op.create_index(
        'idx_team_offense_season',
        'team_offense',
        ['season'],
        unique=False
    )

    # Rushing stats index - season filtering
    op.create_index(
        'idx_rushing_stats_season',
        'rushing_stats',
        ['season'],
        unique=False
    )

    # Receiving stats index - season filtering
    op.create_index(
        'idx_receiving_stats_season',
        'receiving_stats',
        ['season'],
        unique=False
    )

    # Games index - composite index on season and week for efficient game queries
    op.create_index(
        'idx_games_season_week',
        'games',
        ['season', 'week'],
        unique=False
    )

    # Standings index - season filtering
    op.create_index(
        'idx_standings_season',
        'standings',
        ['season'],
        unique=False
    )


def downgrade() -> None:
    """Remove performance indexes from NFL stats tables."""

    # Drop indexes in reverse order
    op.drop_index('idx_standings_season', table_name='standings')
    op.drop_index('idx_games_season_week', table_name='games')
    op.drop_index('idx_receiving_stats_season', table_name='receiving_stats')
    op.drop_index('idx_rushing_stats_season', table_name='rushing_stats')
    op.drop_index('idx_team_offense_season', table_name='team_offense')
    op.drop_index('idx_passing_stats_team', table_name='passing_stats')
    op.drop_index('idx_passing_stats_player', table_name='passing_stats')
    op.drop_index('idx_passing_stats_season', table_name='passing_stats')

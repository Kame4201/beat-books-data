"""create odds table for betting lines and odds data

This migration creates the `odds` table, which stores betting lines and odds
data from various sportsbooks for NFL games. It supports tracking:

  - Spreads (point spread for home/away teams)
  - Moneylines (American odds format, e.g., -150, +130)
  - Over/Under (total points line)
  - Line movement over time (multiple snapshots per game/sportsbook)
  - Opening and closing lines (flagged via boolean columns)

Index strategy:
  - (season, week): Most queries filter by week within a season.
  - (home_team), (away_team): Fast lookup by team, whether home or away.
  - (sportsbook): Filter by specific book (DraftKings, FanDuel, etc.).
  - (game_date): Date-based filtering for scheduling and time-series queries.
  - Partial indexes on is_closing and is_opening WHERE TRUE: These are sparse
    flags (only a small fraction of rows are opening/closing lines), so partial
    indexes give fast lookups without bloating the index for all rows.

Revision ID: 002
Revises: 001
Create Date: 2026-02-19 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '002_performance_indexes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the odds table for storing betting lines from sportsbooks
    op.create_table(
        'odds',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('season', sa.Integer(), nullable=False),
        sa.Column('week', sa.Integer(), nullable=False),
        sa.Column('game_date', sa.Date(), nullable=False),
        sa.Column('home_team', sa.String(length=64), nullable=False),
        sa.Column('away_team', sa.String(length=64), nullable=False),
        sa.Column('sportsbook', sa.String(length=64), nullable=False),
        sa.Column('spread_home', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('spread_away', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('moneyline_home', sa.Integer(), nullable=True),
        sa.Column('moneyline_away', sa.Integer(), nullable=True),
        sa.Column('over_under', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('is_opening', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.Column('is_closing', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'season', 'week', 'home_team', 'sportsbook', 'timestamp',
            name='uq_odds_game_sportsbook_timestamp'
        ),
    )

    # Composite index for the most common query pattern: filter by season + week
    op.create_index('idx_odds_season_week', 'odds', ['season', 'week'])

    # Single-column indexes for team lookups (home and away searched independently)
    op.create_index('idx_odds_home_team', 'odds', ['home_team'])
    op.create_index('idx_odds_away_team', 'odds', ['away_team'])

    # Sportsbook filter index
    op.create_index('idx_odds_sportsbook', 'odds', ['sportsbook'])

    # Date-based queries
    op.create_index('idx_odds_game_date', 'odds', ['game_date'])

    # Partial indexes for opening/closing line lookups (sparse flags)
    op.create_index(
        'idx_odds_closing', 'odds', ['is_closing'],
        postgresql_where=sa.text('is_closing = true')
    )
    op.create_index(
        'idx_odds_opening', 'odds', ['is_opening'],
        postgresql_where=sa.text('is_opening = true')
    )


def downgrade() -> None:
    # Drop indexes first, then the table
    op.drop_index('idx_odds_opening', table_name='odds')
    op.drop_index('idx_odds_closing', table_name='odds')
    op.drop_index('idx_odds_game_date', table_name='odds')
    op.drop_index('idx_odds_sportsbook', table_name='odds')
    op.drop_index('idx_odds_away_team', table_name='odds')
    op.drop_index('idx_odds_home_team', table_name='odds')
    op.drop_index('idx_odds_season_week', table_name='odds')
    op.drop_table('odds')

"""initial schema from Tables.sql

Revision ID: 001
Revises:
Create Date: 2026-02-15 23:58:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ===========================
    # TEAM-LEVEL TABLES
    # ===========================

    # Create team_offense table
    op.create_table('team_offense',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('season', sa.Integer(), nullable=True),
        sa.Column('rk', sa.Integer(), nullable=True),
        sa.Column('tm', sa.String(length=64), nullable=True),
        sa.Column('g', sa.Integer(), nullable=True),
        sa.Column('pf', sa.Integer(), nullable=True),
        sa.Column('yds', sa.Integer(), nullable=True),
        sa.Column('ply', sa.Integer(), nullable=True),
        sa.Column('ypp', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('turnovers', sa.Integer(), nullable=True),
        sa.Column('fl', sa.Integer(), nullable=True),
        sa.Column('firstd_total', sa.Integer(), nullable=True),
        sa.Column('cmp', sa.Integer(), nullable=True),
        sa.Column('att_pass', sa.Integer(), nullable=True),
        sa.Column('yds_pass', sa.Integer(), nullable=True),
        sa.Column('td_pass', sa.Integer(), nullable=True),
        sa.Column('ints', sa.Integer(), nullable=True),
        sa.Column('nypa', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('firstd_pass', sa.Integer(), nullable=True),
        sa.Column('att_rush', sa.Integer(), nullable=True),
        sa.Column('yds_rush', sa.Integer(), nullable=True),
        sa.Column('td_rush', sa.Integer(), nullable=True),
        sa.Column('ypa', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('firstd_rush', sa.Integer(), nullable=True),
        sa.Column('pen', sa.Integer(), nullable=True),
        sa.Column('yds_pen', sa.Integer(), nullable=True),
        sa.Column('firstpy', sa.Integer(), nullable=True),
        sa.Column('sc_pct', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('to_pct', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('opea', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tm', 'season', name='uq_team_offense_tm_season')
    )

    # Create team_defense table
    op.create_table('team_defense',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('season', sa.Integer(), nullable=True),
        sa.Column('rk', sa.Integer(), nullable=True),
        sa.Column('tm', sa.String(length=64), nullable=True),
        sa.Column('g', sa.Integer(), nullable=True),
        sa.Column('pa', sa.Integer(), nullable=True),
        sa.Column('yds', sa.Integer(), nullable=True),
        sa.Column('ply', sa.Integer(), nullable=True),
        sa.Column('ypp', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('turnovers', sa.Integer(), nullable=True),
        sa.Column('fl', sa.Integer(), nullable=True),
        sa.Column('firstd_total', sa.Integer(), nullable=True),
        sa.Column('cmp', sa.Integer(), nullable=True),
        sa.Column('att_pass', sa.Integer(), nullable=True),
        sa.Column('yds_pass', sa.Integer(), nullable=True),
        sa.Column('td_pass', sa.Integer(), nullable=True),
        sa.Column('ints', sa.Integer(), nullable=True),
        sa.Column('nypa', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('firstd_pass', sa.Integer(), nullable=True),
        sa.Column('att_rush', sa.Integer(), nullable=True),
        sa.Column('yds_rush', sa.Integer(), nullable=True),
        sa.Column('td_rush', sa.Integer(), nullable=True),
        sa.Column('ypa', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('firstd_rush', sa.Integer(), nullable=True),
        sa.Column('pen', sa.Integer(), nullable=True),
        sa.Column('yds_pen', sa.Integer(), nullable=True),
        sa.Column('firstpy', sa.Integer(), nullable=True),
        sa.Column('sc_pct', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('to_pct', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('depa', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tm', 'season')
    )

    # Create returns table (team-level)
    op.create_table('returns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('season', sa.Integer(), nullable=True),
        sa.Column('rk', sa.Integer(), nullable=True),
        sa.Column('tm', sa.String(length=64), nullable=True),
        sa.Column('g', sa.Integer(), nullable=True),
        sa.Column('ret_punt', sa.Integer(), nullable=True),
        sa.Column('yds_punt', sa.Integer(), nullable=True),
        sa.Column('td_punt', sa.Integer(), nullable=True),
        sa.Column('lng_punt', sa.Integer(), nullable=True),
        sa.Column('ypr_punt', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('ret_kick', sa.Integer(), nullable=True),
        sa.Column('yds_kick', sa.Integer(), nullable=True),
        sa.Column('td_kick', sa.Integer(), nullable=True),
        sa.Column('lng_kick', sa.Integer(), nullable=True),
        sa.Column('ypr_kick', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('apyd', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tm', 'season')
    )

    # Create kicking table (team-level)
    op.create_table('kicking',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('season', sa.Integer(), nullable=True),
        sa.Column('rk', sa.Integer(), nullable=True),
        sa.Column('tm', sa.String(length=64), nullable=True),
        sa.Column('g', sa.Integer(), nullable=True),
        sa.Column('fga_0_19', sa.Integer(), nullable=True),
        sa.Column('fgm_0_19', sa.Integer(), nullable=True),
        sa.Column('fga_20_29', sa.Integer(), nullable=True),
        sa.Column('fgm_20_29', sa.Integer(), nullable=True),
        sa.Column('fga_30_39', sa.Integer(), nullable=True),
        sa.Column('fgm_30_39', sa.Integer(), nullable=True),
        sa.Column('fga_40_49', sa.Integer(), nullable=True),
        sa.Column('fgm_40_49', sa.Integer(), nullable=True),
        sa.Column('fga_50_plus', sa.Integer(), nullable=True),
        sa.Column('fgm_50_plus', sa.Integer(), nullable=True),
        sa.Column('fga', sa.Integer(), nullable=True),
        sa.Column('fgm', sa.Integer(), nullable=True),
        sa.Column('lng', sa.Integer(), nullable=True),
        sa.Column('fg_pct', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('xpa', sa.Integer(), nullable=True),
        sa.Column('xpm', sa.Integer(), nullable=True),
        sa.Column('xp_pct', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('ko', sa.Integer(), nullable=True),
        sa.Column('ko_yds', sa.Integer(), nullable=True),
        sa.Column('tb', sa.Integer(), nullable=True),
        sa.Column('tb_pct', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('ko_avg', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tm', 'season')
    )

    # Create punting table (team-level)
    op.create_table('punting',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('season', sa.Integer(), nullable=True),
        sa.Column('rk', sa.Integer(), nullable=True),
        sa.Column('tm', sa.String(length=64), nullable=True),
        sa.Column('g', sa.Integer(), nullable=True),
        sa.Column('pnt', sa.Integer(), nullable=True),
        sa.Column('yds', sa.Integer(), nullable=True),
        sa.Column('ypp', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('retyds', sa.Integer(), nullable=True),
        sa.Column('net', sa.Integer(), nullable=True),
        sa.Column('nyp', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('lng', sa.Integer(), nullable=True),
        sa.Column('tb', sa.Integer(), nullable=True),
        sa.Column('tb_pct', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('in20', sa.Integer(), nullable=True),
        sa.Column('in20_pct', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('blck', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tm', 'season')
    )

    # ===========================
    # PLAYER-LEVEL TABLES
    # ===========================

    # Create passing_stats table
    op.create_table('passing_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('season', sa.Integer(), nullable=True),
        sa.Column('rk', sa.Integer(), nullable=True),
        sa.Column('player_name', sa.String(length=128), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('tm', sa.String(length=64), nullable=True),
        sa.Column('pos', sa.String(length=16), nullable=True),
        sa.Column('g', sa.Integer(), nullable=True),
        sa.Column('gs', sa.Integer(), nullable=True),
        sa.Column('qb_rec', sa.String(length=16), nullable=True),
        sa.Column('cmp', sa.Integer(), nullable=True),
        sa.Column('att', sa.Integer(), nullable=True),
        sa.Column('cmp_pct', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('yds', sa.Integer(), nullable=True),
        sa.Column('td', sa.Integer(), nullable=True),
        sa.Column('td_pct', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('ints', sa.Integer(), nullable=True),
        sa.Column('int_pct', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('first_downs', sa.Integer(), nullable=True),
        sa.Column('succ_pct', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('lng', sa.Integer(), nullable=True),
        sa.Column('ypa', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('ay_pa', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('ypc', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('ypg', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('rate', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('qbr', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('sk', sa.Integer(), nullable=True),
        sa.Column('yds_sack', sa.Integer(), nullable=True),
        sa.Column('sk_pct', sa.Numeric(precision=6, scale=3), nullable=True),
        sa.Column('ny_pa', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('any_pa', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('four_qc', sa.Integer(), nullable=True),
        sa.Column('gwd', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('player_name', 'season', 'tm')
    )

    # Create rushing_stats table
    op.create_table('rushing_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('season', sa.Integer(), nullable=True),
        sa.Column('rk', sa.Integer(), nullable=True),
        sa.Column('player_name', sa.String(length=128), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('tm', sa.String(length=64), nullable=True),
        sa.Column('pos', sa.String(length=16), nullable=True),
        sa.Column('g', sa.Integer(), nullable=True),
        sa.Column('gs', sa.Integer(), nullable=True),
        sa.Column('att', sa.Integer(), nullable=True),
        sa.Column('yds', sa.Integer(), nullable=True),
        sa.Column('td', sa.Integer(), nullable=True),
        sa.Column('first_downs', sa.Integer(), nullable=True),
        sa.Column('succ_pct', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('lng', sa.Integer(), nullable=True),
        sa.Column('ypa', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('ypg', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('apg', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('fmb', sa.Integer(), nullable=True),
        sa.Column('awards', sa.String(length=128), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('player_name', 'season', 'tm')
    )

    # Create receiving_stats table
    op.create_table('receiving_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('season', sa.Integer(), nullable=True),
        sa.Column('rk', sa.Integer(), nullable=True),
        sa.Column('player_name', sa.String(length=128), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('tm', sa.String(length=64), nullable=True),
        sa.Column('pos', sa.String(length=16), nullable=True),
        sa.Column('g', sa.Integer(), nullable=True),
        sa.Column('gs', sa.Integer(), nullable=True),
        sa.Column('tgt', sa.Integer(), nullable=True),
        sa.Column('rec', sa.Integer(), nullable=True),
        sa.Column('yds', sa.Integer(), nullable=True),
        sa.Column('ypr', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('td', sa.Integer(), nullable=True),
        sa.Column('first_downs', sa.Integer(), nullable=True),
        sa.Column('succ_pct', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('lng', sa.Integer(), nullable=True),
        sa.Column('rpg', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('ypg', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('catch_pct', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('ypt', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('fmb', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('player_name', 'season', 'tm')
    )

    # Create defense_stats table
    op.create_table('defense_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('season', sa.Integer(), nullable=True),
        sa.Column('rk', sa.Integer(), nullable=True),
        sa.Column('player_name', sa.String(length=128), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('tm', sa.String(length=64), nullable=True),
        sa.Column('pos', sa.String(length=16), nullable=True),
        sa.Column('g', sa.Integer(), nullable=True),
        sa.Column('gs', sa.Integer(), nullable=True),
        sa.Column('ints', sa.Integer(), nullable=True),
        sa.Column('int_yds', sa.Integer(), nullable=True),
        sa.Column('int_td', sa.Integer(), nullable=True),
        sa.Column('int_lng', sa.Integer(), nullable=True),
        sa.Column('pd', sa.Integer(), nullable=True),
        sa.Column('ff', sa.Integer(), nullable=True),
        sa.Column('fmb', sa.Integer(), nullable=True),
        sa.Column('fr', sa.Integer(), nullable=True),
        sa.Column('fr_yds', sa.Integer(), nullable=True),
        sa.Column('fr_td', sa.Integer(), nullable=True),
        sa.Column('sk', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('comb', sa.Integer(), nullable=True),
        sa.Column('solo', sa.Integer(), nullable=True),
        sa.Column('ast', sa.Integer(), nullable=True),
        sa.Column('tfl', sa.Integer(), nullable=True),
        sa.Column('qb_hits', sa.Integer(), nullable=True),
        sa.Column('sfty', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('player_name', 'season', 'tm')
    )

    # Create kicking_stats table
    op.create_table('kicking_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('season', sa.Integer(), nullable=True),
        sa.Column('rk', sa.Integer(), nullable=True),
        sa.Column('player_name', sa.String(length=128), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('tm', sa.String(length=64), nullable=True),
        sa.Column('pos', sa.String(length=16), nullable=True),
        sa.Column('g', sa.Integer(), nullable=True),
        sa.Column('gs', sa.Integer(), nullable=True),
        sa.Column('fga_0_19', sa.Integer(), nullable=True),
        sa.Column('fgm_0_19', sa.Integer(), nullable=True),
        sa.Column('fga_20_29', sa.Integer(), nullable=True),
        sa.Column('fgm_20_29', sa.Integer(), nullable=True),
        sa.Column('fga_30_39', sa.Integer(), nullable=True),
        sa.Column('fgm_30_39', sa.Integer(), nullable=True),
        sa.Column('fga_40_49', sa.Integer(), nullable=True),
        sa.Column('fgm_40_49', sa.Integer(), nullable=True),
        sa.Column('fga_50_plus', sa.Integer(), nullable=True),
        sa.Column('fgm_50_plus', sa.Integer(), nullable=True),
        sa.Column('fga', sa.Integer(), nullable=True),
        sa.Column('fgm', sa.Integer(), nullable=True),
        sa.Column('lng', sa.Integer(), nullable=True),
        sa.Column('fg_pct', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('xpa', sa.Integer(), nullable=True),
        sa.Column('xpm', sa.Integer(), nullable=True),
        sa.Column('xp_pct', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('ko', sa.Integer(), nullable=True),
        sa.Column('ko_yds', sa.Integer(), nullable=True),
        sa.Column('tb', sa.Integer(), nullable=True),
        sa.Column('tb_pct', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('ko_avg', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('player_name', 'season', 'tm')
    )

    # Create punting_stats table
    op.create_table('punting_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('season', sa.Integer(), nullable=True),
        sa.Column('rk', sa.Integer(), nullable=True),
        sa.Column('player_name', sa.String(length=128), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('tm', sa.String(length=64), nullable=True),
        sa.Column('pos', sa.String(length=16), nullable=True),
        sa.Column('g', sa.Integer(), nullable=True),
        sa.Column('gs', sa.Integer(), nullable=True),
        sa.Column('pnt', sa.Integer(), nullable=True),
        sa.Column('yds', sa.Integer(), nullable=True),
        sa.Column('ypp', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('ret_yds', sa.Integer(), nullable=True),
        sa.Column('net_yds', sa.Integer(), nullable=True),
        sa.Column('ny_pa', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('lng', sa.Integer(), nullable=True),
        sa.Column('tb', sa.Integer(), nullable=True),
        sa.Column('tb_pct', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('pnt20', sa.Integer(), nullable=True),
        sa.Column('in20_pct', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('blck', sa.Integer(), nullable=True),
        sa.Column('awards', sa.String(length=128), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('player_name', 'season', 'tm')
    )

    # Create return_stats table
    op.create_table('return_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('season', sa.Integer(), nullable=True),
        sa.Column('rk', sa.Integer(), nullable=True),
        sa.Column('player_name', sa.String(length=128), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('tm', sa.String(length=64), nullable=True),
        sa.Column('pos', sa.String(length=16), nullable=True),
        sa.Column('g', sa.Integer(), nullable=True),
        sa.Column('gs', sa.Integer(), nullable=True),
        sa.Column('pr', sa.Integer(), nullable=True),
        sa.Column('pr_yds', sa.Integer(), nullable=True),
        sa.Column('pr_td', sa.Integer(), nullable=True),
        sa.Column('pr_lng', sa.Integer(), nullable=True),
        sa.Column('pr_ypr', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('kr', sa.Integer(), nullable=True),
        sa.Column('kr_yds', sa.Integer(), nullable=True),
        sa.Column('kr_td', sa.Integer(), nullable=True),
        sa.Column('kr_lng', sa.Integer(), nullable=True),
        sa.Column('kr_ypr', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('apyd', sa.Integer(), nullable=True),
        sa.Column('awards', sa.String(length=128), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('player_name', 'season', 'tm')
    )

    # Create scoring_stats table
    op.create_table('scoring_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('season', sa.Integer(), nullable=True),
        sa.Column('rk', sa.Integer(), nullable=True),
        sa.Column('player_name', sa.String(length=128), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('tm', sa.String(length=64), nullable=True),
        sa.Column('pos', sa.String(length=16), nullable=True),
        sa.Column('g', sa.Integer(), nullable=True),
        sa.Column('gs', sa.Integer(), nullable=True),
        sa.Column('rush_td', sa.Integer(), nullable=True),
        sa.Column('rec_td', sa.Integer(), nullable=True),
        sa.Column('pr_td', sa.Integer(), nullable=True),
        sa.Column('kr_td', sa.Integer(), nullable=True),
        sa.Column('fr_td', sa.Integer(), nullable=True),
        sa.Column('int_td', sa.Integer(), nullable=True),
        sa.Column('oth_td', sa.Integer(), nullable=True),
        sa.Column('all_td', sa.Integer(), nullable=True),
        sa.Column('two_pm', sa.Integer(), nullable=True),
        sa.Column('d2p', sa.Integer(), nullable=True),
        sa.Column('xpm', sa.Integer(), nullable=True),
        sa.Column('xpa', sa.Integer(), nullable=True),
        sa.Column('fgm', sa.Integer(), nullable=True),
        sa.Column('fga', sa.Integer(), nullable=True),
        sa.Column('sfty', sa.Integer(), nullable=True),
        sa.Column('pts', sa.Integer(), nullable=True),
        sa.Column('pts_pg', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('awards', sa.String(length=128), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('player_name', 'season', 'tm')
    )

    # ===========================
    # STANDINGS + GAMES
    # ===========================

    # Create standings table
    op.create_table('standings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('season', sa.Integer(), nullable=True),
        sa.Column('tm', sa.String(length=64), nullable=True),
        sa.Column('w', sa.Integer(), nullable=True),
        sa.Column('l', sa.Integer(), nullable=True),
        sa.Column('t', sa.Integer(), nullable=True),
        sa.Column('win_pct', sa.Numeric(precision=6, scale=3), nullable=True),
        sa.Column('pf', sa.Integer(), nullable=True),
        sa.Column('pa', sa.Integer(), nullable=True),
        sa.Column('pd', sa.Integer(), nullable=True),
        sa.Column('mov', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('sos', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('srs', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('osrs', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('dsrs', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tm', 'season')
    )

    # Create games table
    op.create_table('games',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('season', sa.Integer(), nullable=True),
        sa.Column('week', sa.Integer(), nullable=True),
        sa.Column('game_day', sa.String(length=16), nullable=True),
        sa.Column('game_date', sa.Date(), nullable=True),
        sa.Column('kickoff_time', sa.String(length=16), nullable=True),
        sa.Column('winner', sa.String(length=64), nullable=True),
        sa.Column('loser', sa.String(length=64), nullable=True),
        sa.Column('boxscore', sa.String(length=128), nullable=True),
        sa.Column('pts_w', sa.Integer(), nullable=True),
        sa.Column('pts_l', sa.Integer(), nullable=True),
        sa.Column('yds_w', sa.Integer(), nullable=True),
        sa.Column('to_w', sa.Integer(), nullable=True),
        sa.Column('yds_l', sa.Integer(), nullable=True),
        sa.Column('to_l', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('season', 'week', 'winner', 'loser')
    )


def downgrade() -> None:
    # Drop all tables in reverse order
    op.drop_table('games')
    op.drop_table('standings')
    op.drop_table('scoring_stats')
    op.drop_table('return_stats')
    op.drop_table('punting_stats')
    op.drop_table('kicking_stats')
    op.drop_table('defense_stats')
    op.drop_table('receiving_stats')
    op.drop_table('rushing_stats')
    op.drop_table('passing_stats')
    op.drop_table('punting')
    op.drop_table('kicking')
    op.drop_table('returns')
    op.drop_table('team_defense')
    op.drop_table('team_offense')

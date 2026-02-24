import logging
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import the SQLAlchemy Base from entities
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from src
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.entities.base import Base
from src.core.config import settings

# Import all entity models so Alembic can detect them
from src.entities.team_offense import TeamOffense
from src.entities.team_defense import TeamDefense
from src.entities.passing_stats import PassingStats
from src.entities.rushing_stats import RushingStats
from src.entities.receiving_stats import ReceivingStats
from src.entities.defense_stats import DefenseStats
from src.entities.kicking_stats import KickingStats
from src.entities.punting_stats import PuntingStats
from src.entities.return_stats import ReturnStats
from src.entities.scoring_stats import ScoringStats
from src.entities.kicking import Kicking
from src.entities.punting import Punting
from src.entities.returns import TeamReturns
from src.entities.games import Games
from src.entities.standings import Standings
from src.entities.team_game import TeamGame
<<<<<<< claude/issue-8-20260216-0000
from src.entities.injury_report import InjuryReport
from src.entities.game_weather import GameWeather
=======
from src.entities.odds import Odds
>>>>>>> main

logger = logging.getLogger("alembic.env")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Set the sqlalchemy.url from our settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata


def _log_environment_banner() -> None:
    """Log which environment migrations are targeting."""
    env = settings.ENV
    banner = f"  ALEMBIC MIGRATION TARGET: {env.upper()}  "
    separator = "=" * len(banner)
    logger.warning("")
    logger.warning(separator)
    logger.warning(banner)
    logger.warning(separator)
    if env == "main":
        logger.warning("*** PRODUCTION DATABASE -- Proceed with caution ***")
    logger.warning("")


def _check_production_safety() -> None:
    """Block migrations on main unless ALLOW_PRODUCTION_MIGRATE=true is set."""
    if settings.ENV == "main":
        if os.environ.get("ALLOW_PRODUCTION_MIGRATE") != "true":
            raise RuntimeError(
                "Refusing to migrate production database. "
                "Set ALLOW_PRODUCTION_MIGRATE=true to proceed."
            )


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    _log_environment_banner()
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    _log_environment_banner()
    _check_production_safety()

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

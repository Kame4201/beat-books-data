"""
Shared test fixtures for beat-books-data.

Provides:
- db_session: In-memory SQLite session with all tables created
- sample_team_offense: A sample TeamOffense entity for testing
- sample_passing_stats: A sample PassingStats entity for testing
"""

import os

# Force sqlite for tests so we never accidentally hit a real database.
# Must be set before any src imports (Settings() validates at import time).
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Strip unknown env vars that may exist in .env but aren't in Settings.
for _key in list(os.environ):
    if _key.startswith("SCRAPE_BACKEND"):
        del os.environ[_key]

import pytest
from decimal import Decimal
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from src.entities.base import Base
from src.entities.team_offense import TeamOffense
from src.entities.passing_stats import PassingStats


@pytest.fixture
def db_session():
    """In-memory SQLite for unit tests. Never hits production DB."""
    engine = create_engine("sqlite:///:memory:")

    # Enable foreign key support for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Create all tables from ORM models
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture
def sample_team_offense():
    """Return a sample TeamOffense entity for testing."""
    return TeamOffense(
        season=2023,
        rk=1,
        tm="KAN",
        g=17,
        pf=450,
        yds=6200,
        ply=1050,
        ypp=Decimal("5.90"),
        turnovers=12,
        fl=5,
        firstd_total=350,
        cmp=380,
        att_pass=580,
        yds_pass=4800,
        td_pass=35,
        ints=10,
        nypa=Decimal("7.20"),
        firstd_pass=200,
        att_rush=420,
        yds_rush=1400,
        td_rush=15,
        ypa=Decimal("4.50"),
        firstd_rush=100,
        pen=95,
        yds_pen=800,
        firstpy=50,
        sc_pct=Decimal("42.50"),
        to_pct=Decimal("10.20"),
        opea=Decimal("125.50"),
    )


@pytest.fixture
def sample_passing_stats():
    """Return a sample PassingStats entity for testing."""
    return PassingStats(
        season=2023,
        rk=1,
        player_name="Patrick Mahomes",
        age=28,
        tm="KAN",
        pos="QB",
        g=17,
        gs=17,
        qb_rec="11-6-0",
        cmp=401,
        att=597,
        cmp_pct=Decimal("67.17"),
        yds=4839,
        td=27,
        td_pct=Decimal("4.52"),
        ints=14,
        int_pct=Decimal("2.35"),
        first_downs=230,
        succ_pct=Decimal("48.50"),
        lng=67,
        ypa=Decimal("8.11"),
        ay_pa=Decimal("7.50"),
        ypc=Decimal("12.07"),
        ypg=Decimal("284.65"),
        rate=Decimal("92.60"),
        qbr=Decimal("64.30"),
        sk=28,
        yds_sack=190,
        sk_pct=Decimal("4.480"),
        ny_pa=Decimal("7.43"),
        any_pa=Decimal("6.95"),
        four_qc=3,
        gwd=5,
    )

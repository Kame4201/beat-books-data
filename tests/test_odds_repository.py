"""Unit tests for odds repository."""

import pytest
from datetime import datetime, date
from decimal import Decimal

from src.entities.odds import Odds
from src.entities.base import Base
from src.dtos.odds_dto import OddsCreate
from src.repositories.odds_repo import OddsRepository

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def db_session():
    """In-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_odds_dto():
    """Sample OddsCreate DTO for testing."""
    return OddsCreate(
        season=2024,
        week=1,
        game_date=date(2024, 9, 8),
        home_team="KC",
        away_team="BAL",
        sportsbook="DraftKings",
        spread_home=Decimal("-3.0"),
        spread_away=Decimal("3.0"),
        moneyline_home=-150,
        moneyline_away=130,
        over_under=Decimal("47.5"),
        timestamp=datetime(2024, 9, 7, 10, 0, 0),
        is_opening=False,
        is_closing=True,
    )


class TestOddsRepository:
    """Test suite for OddsRepository data access layer."""

    def test_create_odds(self, db_session, sample_odds_dto):
        """Test creating a new odds record."""
        odds = OddsRepository.create(db_session, sample_odds_dto)

        assert odds.id is not None
        assert odds.season == 2024
        assert odds.week == 1
        assert odds.home_team == "KC"
        assert odds.away_team == "BAL"
        assert odds.sportsbook == "DraftKings"
        assert float(odds.spread_home) == -3.0
        assert odds.is_closing is True

    def test_get_by_id(self, db_session, sample_odds_dto):
        """Test retrieving odds by ID."""
        created = OddsRepository.create(db_session, sample_odds_dto)
        retrieved = OddsRepository.get_by_id(db_session, created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.home_team == "KC"

    def test_get_by_unique_key(self, db_session, sample_odds_dto):
        """Test retrieving odds by unique constraint."""
        OddsRepository.create(db_session, sample_odds_dto)

        retrieved = OddsRepository.get_by_unique_key(
            db_session,
            season=2024,
            week=1,
            home_team="KC",
            sportsbook="DraftKings",
            timestamp=datetime(2024, 9, 7, 10, 0, 0),
        )

        assert retrieved is not None
        assert retrieved.home_team == "KC"
        assert retrieved.sportsbook == "DraftKings"

    def test_create_or_skip_new(self, db_session, sample_odds_dto):
        """Test create_or_skip with new record."""
        odds = OddsRepository.create_or_skip(db_session, sample_odds_dto)

        assert odds.id is not None
        assert odds.home_team == "KC"

    def test_create_or_skip_duplicate(self, db_session, sample_odds_dto):
        """Test create_or_skip with duplicate record."""
        first = OddsRepository.create_or_skip(db_session, sample_odds_dto)
        second = OddsRepository.create_or_skip(db_session, sample_odds_dto)

        # Should return the same record
        assert first.id == second.id

    def test_get_closing_lines(self, db_session, sample_odds_dto):
        """Test retrieving closing lines."""
        OddsRepository.create(db_session, sample_odds_dto)

        closing = OddsRepository.get_closing_lines(db_session, 2024, 1)

        assert len(closing) == 1
        assert closing[0].is_closing is True

    def test_get_closing_lines_by_sportsbook(self, db_session, sample_odds_dto):
        """Test retrieving closing lines filtered by sportsbook."""
        OddsRepository.create(db_session, sample_odds_dto)

        # Create another with different sportsbook
        other_dto = OddsCreate(
            season=2024,
            week=1,
            game_date=date(2024, 9, 8),
            home_team="DAL",
            away_team="NYG",
            sportsbook="FanDuel",
            spread_home=Decimal("-7.0"),
            spread_away=Decimal("7.0"),
            timestamp=datetime(2024, 9, 7, 10, 0, 0),
            is_closing=True,
        )
        OddsRepository.create(db_session, other_dto)

        # Filter by DraftKings
        closing = OddsRepository.get_closing_lines(
            db_session, 2024, 1, sportsbook="DraftKings"
        )

        assert len(closing) == 1
        assert closing[0].sportsbook == "DraftKings"

    def test_get_opening_lines(self, db_session):
        """Test retrieving opening lines."""
        opening_dto = OddsCreate(
            season=2024,
            week=1,
            game_date=date(2024, 9, 8),
            home_team="KC",
            away_team="BAL",
            sportsbook="DraftKings",
            timestamp=datetime(2024, 9, 1, 10, 0, 0),
            is_opening=True,
        )
        OddsRepository.create(db_session, opening_dto)

        opening = OddsRepository.get_opening_lines(db_session, 2024, 1)

        assert len(opening) == 1
        assert opening[0].is_opening is True

    def test_get_line_movement(self, db_session):
        """Test retrieving line movement history."""
        # Create multiple timestamps for same game
        for hour in [10, 12, 14]:
            dto = OddsCreate(
                season=2024,
                week=1,
                game_date=date(2024, 9, 8),
                home_team="KC",
                away_team="BAL",
                sportsbook="DraftKings",
                spread_home=Decimal(f"-{3 + hour * 0.1}"),
                timestamp=datetime(2024, 9, 7, hour, 0, 0),
            )
            OddsRepository.create(db_session, dto)

        movements = OddsRepository.get_line_movement(
            db_session, 2024, 1, "KC", "DraftKings"
        )

        assert len(movements) == 3
        # Should be ordered by timestamp
        assert movements[0].timestamp.hour == 10
        assert movements[2].timestamp.hour == 14

    def test_get_by_team(self, db_session, sample_odds_dto):
        """Test retrieving odds by team."""
        OddsRepository.create(db_session, sample_odds_dto)

        # Search as home team
        odds = OddsRepository.get_by_team(db_session, "KC", season=2024, week=1)
        assert len(odds) == 1

        # Search as away team
        odds = OddsRepository.get_by_team(db_session, "BAL", season=2024, week=1)
        assert len(odds) == 1

    def test_bulk_create(self, db_session):
        """Test bulk insert of odds records."""
        dtos = [
            OddsCreate(
                season=2024,
                week=1,
                game_date=date(2024, 9, 8),
                home_team="KC",
                away_team="BAL",
                sportsbook="DraftKings",
                timestamp=datetime(2024, 9, 7, 10, 0, 0),
            ),
            OddsCreate(
                season=2024,
                week=1,
                game_date=date(2024, 9, 8),
                home_team="DAL",
                away_team="NYG",
                sportsbook="DraftKings",
                timestamp=datetime(2024, 9, 7, 10, 0, 0),
            ),
        ]

        created = OddsRepository.bulk_create(db_session, dtos)

        assert len(created) == 2
        assert all(odds.id is not None for odds in created)

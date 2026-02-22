"""Unit tests for StatsRetrievalService."""

import pytest
from unittest.mock import Mock, MagicMock
from decimal import Decimal

from src.services.stats_retrieval_service import StatsRetrievalService
from src.entities.team_offense import TeamOffense
from src.entities.passing_stats import PassingStats
from src.entities.standings import Standings


class TestStatsRetrievalService:
    """Test suite for StatsRetrievalService with mocked repositories."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock()

    @pytest.fixture
    def service(self, mock_session):
        """Create a StatsRetrievalService with mocked repositories."""
        service = StatsRetrievalService(mock_session)

        # Mock all repositories
        service.team_offense_repo = Mock()
        service.passing_stats_repo = Mock()
        service.rushing_stats_repo = Mock()
        service.receiving_stats_repo = Mock()
        service.standings_repo = Mock()
        service.team_game_repo = Mock()

        return service

    # Tests for get_all_teams
    def test_get_all_teams_returns_data_with_pagination(self, service):
        """Test that get_all_teams returns teams with pagination info."""
        # Arrange
        mock_teams = [
            TeamOffense(id=1, season=2023, tm="Team A", pf=400),
            TeamOffense(id=2, season=2023, tm="Team B", pf=350),
        ]
        service.team_offense_repo.find_by_season.return_value = mock_teams
        service.team_offense_repo.count_by_season.return_value = 32

        # Act
        result = service.get_all_teams(season=2023, offset=0, limit=50)

        # Assert
        assert result["data"] == mock_teams
        assert result["total"] == 32
        assert result["offset"] == 0
        assert result["limit"] == 50
        service.team_offense_repo.find_by_season.assert_called_once_with(
            season=2023, limit=50, offset=0, sort_by="pf", order="desc"
        )

    def test_get_all_teams_enforces_max_limit(self, service):
        """Test that get_all_teams enforces maximum limit of 200."""
        # Arrange
        service.team_offense_repo.find_by_season.return_value = []
        service.team_offense_repo.count_by_season.return_value = 0

        # Act
        result = service.get_all_teams(season=2023, limit=500)

        # Assert
        service.team_offense_repo.find_by_season.assert_called_once()
        call_args = service.team_offense_repo.find_by_season.call_args
        assert call_args.kwargs["limit"] == 200

    def test_get_all_teams_with_custom_sort(self, service):
        """Test that get_all_teams respects custom sorting parameters."""
        # Arrange
        service.team_offense_repo.find_by_season.return_value = []
        service.team_offense_repo.count_by_season.return_value = 0

        # Act
        service.get_all_teams(season=2023, sort_by="yds", order="asc")

        # Assert
        service.team_offense_repo.find_by_season.assert_called_once_with(
            season=2023, limit=50, offset=0, sort_by="yds", order="asc"
        )

    def test_get_all_teams_empty_result(self, service):
        """Test that get_all_teams returns empty list when no data exists."""
        # Arrange
        service.team_offense_repo.find_by_season.return_value = []
        service.team_offense_repo.count_by_season.return_value = 0

        # Act
        result = service.get_all_teams(season=2025)

        # Assert
        assert result["data"] == []
        assert result["total"] == 0

    # Tests for get_team_stats
    def test_get_team_stats_returns_formatted_data(self, service):
        """Test that get_team_stats returns properly formatted team stats."""
        # Arrange
        mock_team = TeamOffense(
            id=1,
            season=2023,
            tm="Chiefs",
            g=17,
            pf=450,
            yds=6000,
            ply=1000,
            ypp=Decimal("6.00"),
            turnovers=15,
            fl=5,
            firstd_total=300,
            cmp=400,
            att_pass=600,
            yds_pass=4000,
            td_pass=35,
            ints=10,
            nypa=Decimal("6.50"),
            firstd_pass=200,
            att_rush=400,
            yds_rush=2000,
            td_rush=20,
            ypa=Decimal("5.00"),
            firstd_rush=100,
            pen=80,
            yds_pen=600,
            firstpy=20,
            sc_pct=Decimal("45.00"),
            to_pct=Decimal("12.00"),
        )
        service.team_offense_repo.find_by_team_and_season.return_value = mock_team

        # Act
        result = service.get_team_stats("Chiefs", 2023)

        # Assert
        assert result is not None
        assert result["team"] == "Chiefs"
        assert result["season"] == 2023
        assert result["points_for"] == 450
        assert result["passing"]["yards"] == 4000
        assert result["rushing"]["yards"] == 2000

    def test_get_team_stats_not_found(self, service):
        """Test that get_team_stats returns None when team not found."""
        # Arrange
        service.team_offense_repo.find_by_team_and_season.return_value = None

        # Act
        result = service.get_team_stats("NonExistent", 2023)

        # Assert
        assert result is None

    # Tests for get_player_stats
    def test_get_player_stats_returns_all_categories(self, service):
        """Test that get_player_stats returns stats from all categories."""
        # Arrange
        mock_passing = [PassingStats(id=1, player_name="Patrick Mahomes")]
        mock_rushing = []
        mock_receiving = []

        service.passing_stats_repo.find_by_player.return_value = mock_passing
        service.rushing_stats_repo.search_players.return_value = mock_rushing
        service.receiving_stats_repo.search_players.return_value = mock_receiving

        # Act
        result = service.get_player_stats("Mahomes", 2023)

        # Assert
        assert result["player_name"] == "Mahomes"
        assert result["season"] == 2023
        assert result["passing"] == mock_passing
        assert result["rushing"] == mock_rushing
        assert result["receiving"] == mock_receiving

    def test_get_player_stats_empty_results(self, service):
        """Test that get_player_stats handles no results gracefully."""
        # Arrange
        service.passing_stats_repo.find_by_player.return_value = []
        service.rushing_stats_repo.search_players.return_value = []
        service.receiving_stats_repo.search_players.return_value = []

        # Act
        result = service.get_player_stats("Unknown", 2023)

        # Assert
        assert result["passing"] == []
        assert result["rushing"] == []
        assert result["receiving"] == []

    # Tests for get_standings
    def test_get_standings_returns_data_with_pagination(self, service):
        """Test that get_standings returns standings with pagination."""
        # Arrange
        mock_standings = [
            Standings(id=1, season=2023, tm="Team A", w=12, losses=5),
            Standings(id=2, season=2023, tm="Team B", w=10, losses=7),
        ]
        service.standings_repo.find_by_season.return_value = mock_standings
        service.standings_repo.count_by_season.return_value = 32

        # Act
        result = service.get_standings(season=2023)

        # Assert
        assert result["data"] == mock_standings
        assert result["total"] == 32
        assert result["offset"] == 0
        assert result["limit"] == 50

    def test_get_standings_empty_result(self, service):
        """Test that get_standings returns empty list when no data."""
        # Arrange
        service.standings_repo.find_by_season.return_value = []
        service.standings_repo.count_by_season.return_value = 0

        # Act
        result = service.get_standings(season=2025)

        # Assert
        assert result["data"] == []
        assert result["total"] == 0

    # Tests for get_games
    def test_get_games_returns_all_games_for_season(self, service):
        """Test that get_games returns all games when week is not specified."""
        # Arrange
        mock_games = [Mock(), Mock(), Mock()]
        service.team_game_repo.find_by_season_and_week.return_value = mock_games
        service.team_game_repo.count_by_season.return_value = 256

        # Act
        result = service.get_games(season=2023)

        # Assert
        assert result["data"] == mock_games
        assert result["total"] == 256
        assert result["week"] is None

    def test_get_games_filters_by_week(self, service):
        """Test that get_games filters by week when specified."""
        # Arrange
        mock_games = [Mock(), Mock()]
        service.team_game_repo.find_by_season_and_week.return_value = mock_games
        service.team_game_repo.count_by_season.return_value = 16

        # Act
        result = service.get_games(season=2023, week=10)

        # Assert
        service.team_game_repo.find_by_season_and_week.assert_called_once()
        call_args = service.team_game_repo.find_by_season_and_week.call_args
        assert call_args.kwargs["week"] == 10
        assert result["week"] == 10

    def test_get_games_empty_result(self, service):
        """Test that get_games returns empty list when no games found."""
        # Arrange
        service.team_game_repo.find_by_season_and_week.return_value = []
        service.team_game_repo.count_by_season.return_value = 0

        # Act
        result = service.get_games(season=2025, week=99)

        # Assert
        assert result["data"] == []
        assert result["total"] == 0

    # Tests for search_players
    def test_search_players_searches_all_categories(self, service):
        """Test that search_players queries all stat categories."""
        # Arrange
        mock_passing = [Mock()]
        mock_rushing = [Mock()]
        mock_receiving = [Mock()]

        service.passing_stats_repo.search_players.return_value = mock_passing
        service.rushing_stats_repo.search_players.return_value = mock_rushing
        service.receiving_stats_repo.search_players.return_value = mock_receiving

        # Act
        result = service.search_players(query="Smith")

        # Assert
        assert result["query"] == "Smith"
        assert result["passing"] == mock_passing
        assert result["rushing"] == mock_rushing
        assert result["receiving"] == mock_receiving

    def test_search_players_with_filters(self, service):
        """Test that search_players respects season and position filters."""
        # Arrange
        service.passing_stats_repo.search_players.return_value = []
        service.rushing_stats_repo.search_players.return_value = []
        service.receiving_stats_repo.search_players.return_value = []

        # Act
        result = service.search_players(query="Jones", season=2023, position="RB")

        # Assert
        assert result["season"] == 2023
        assert result["position"] == "RB"
        service.rushing_stats_repo.search_players.assert_called_once()
        call_args = service.rushing_stats_repo.search_players.call_args
        assert call_args.kwargs["season"] == 2023
        assert call_args.kwargs["position"] == "RB"

    def test_search_players_enforces_max_limit(self, service):
        """Test that search_players enforces maximum limit of 200."""
        # Arrange
        service.passing_stats_repo.search_players.return_value = []
        service.rushing_stats_repo.search_players.return_value = []
        service.receiving_stats_repo.search_players.return_value = []

        # Act
        result = service.search_players(query="Test", limit=500)

        # Assert
        service.passing_stats_repo.search_players.assert_called_once()
        call_args = service.passing_stats_repo.search_players.call_args
        assert call_args.kwargs["limit"] == 200

    def test_search_players_empty_results(self, service):
        """Test that search_players returns empty lists when no matches."""
        # Arrange
        service.passing_stats_repo.search_players.return_value = []
        service.rushing_stats_repo.search_players.return_value = []
        service.receiving_stats_repo.search_players.return_value = []

        # Act
        result = service.search_players(query="NonExistentPlayer")

        # Assert
        assert result["passing"] == []
        assert result["rushing"] == []
        assert result["receiving"] == []

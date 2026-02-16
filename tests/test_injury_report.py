"""
Unit tests for injury report functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date

from src.entities.injury_report import InjuryReport
from src.dtos.injury_report_dto import InjuryReportCreate
from src.repositories.injury_report_repo import InjuryReportRepository
from src.services.injury_report_service import InjuryReportService


class TestInjuryReportEntity:
    """Test InjuryReport entity."""

    def test_injury_report_creation(self):
        """Test that InjuryReport entity can be instantiated."""
        injury = InjuryReport(
            season=2024,
            week=5,
            player_name="Patrick Mahomes",
            team="KC",
            position="QB",
            designation="Questionable",
            injury_type="ankle",
            report_date=date(2024, 10, 1)
        )

        assert injury.season == 2024
        assert injury.week == 5
        assert injury.player_name == "Patrick Mahomes"
        assert injury.team == "KC"
        assert injury.position == "QB"
        assert injury.designation == "Questionable"
        assert injury.injury_type == "ankle"


class TestInjuryReportDTO:
    """Test InjuryReportCreate DTO validation."""

    def test_valid_dto_creation(self):
        """Test creating a valid DTO."""
        dto = InjuryReportCreate(
            season=2024,
            week=5,
            player_name="Patrick Mahomes",
            team="KC",
            position="QB",
            designation="Questionable",
            injury_type="ankle",
            report_date=date(2024, 10, 1)
        )

        assert dto.season == 2024
        assert dto.week == 5
        assert dto.player_name == "Patrick Mahomes"

    def test_dto_validation_season(self):
        """Test that season must be > 1900."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            InjuryReportCreate(
                season=1800,  # Invalid
                week=5,
                player_name="Test Player",
                team="KC",
                designation="Out"
            )

    def test_dto_validation_week(self):
        """Test that week must be 0-22."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            InjuryReportCreate(
                season=2024,
                week=30,  # Invalid
                player_name="Test Player",
                team="KC",
                designation="Out"
            )

    def test_dto_optional_fields(self):
        """Test that position, injury_type, and report_date are optional."""
        dto = InjuryReportCreate(
            season=2024,
            week=5,
            player_name="Test Player",
            team="KC",
            designation="Out"
        )

        assert dto.position is None
        assert dto.injury_type is None
        assert dto.report_date is None


class TestInjuryReportRepository:
    """Test InjuryReportRepository."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock()

    @pytest.fixture
    def repo(self, mock_session):
        """Create a repository with mock session."""
        return InjuryReportRepository(mock_session)

    def test_create_from_dto(self, repo, mock_session):
        """Test creating an injury report from DTO."""
        dto = InjuryReportCreate(
            season=2024,
            week=5,
            player_name="Patrick Mahomes",
            team="KC",
            position="QB",
            designation="Questionable",
            injury_type="ankle"
        )

        # Mock the session behavior
        mock_session.add = Mock()
        mock_session.commit = Mock()
        mock_session.refresh = Mock()

        result = repo.create_from_dto(dto)

        assert result.season == 2024
        assert result.player_name == "Patrick Mahomes"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()


class TestInjuryReportService:
    """Test InjuryReportService with mocked scraping."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return Mock()

    @pytest.fixture
    def service(self, mock_db_session):
        """Create a service with mock session."""
        return InjuryReportService(mock_db_session)

    @patch('src.services.injury_report_service.webdriver.Chrome')
    def test_scrape_weekly_injuries_pfr(self, mock_chrome, service):
        """Test scraping injury reports with mocked responses."""
        # Mock driver and response
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        # Mock HTML response
        mock_html = """
        <html>
            <table id="injuries">
                <tbody>
                    <tr>
                        <td>Patrick Mahomes</td>
                        <td>KC</td>
                        <td>QB</td>
                        <td>Ankle</td>
                        <td>Questionable</td>
                    </tr>
                    <tr>
                        <td>Travis Kelce</td>
                        <td>KC</td>
                        <td>TE</td>
                        <td>Knee</td>
                        <td>Doubtful</td>
                    </tr>
                </tbody>
            </table>
        </html>
        """
        mock_driver.page_source = mock_html
        mock_driver.get = Mock()
        mock_driver.quit = Mock()

        # Run the scrape
        results = service.scrape_weekly_injuries_pfr(2024, 5)

        # Verify results
        assert len(results) == 2
        assert results[0].player_name == "Patrick Mahomes"
        assert results[0].team == "KC"
        assert results[0].position == "QB"
        assert results[0].designation == "Questionable"
        assert results[0].injury_type == "Ankle"

        assert results[1].player_name == "Travis Kelce"
        assert results[1].designation == "Doubtful"

        # Verify driver was called correctly
        mock_driver.get.assert_called_once()
        mock_driver.quit.assert_called_once()

    @patch('src.services.injury_report_service.webdriver.Chrome')
    def test_scrape_no_table(self, mock_chrome, service):
        """Test scraping when no injury table is found."""
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        # Mock HTML without injury table
        mock_html = "<html><body>No injuries table</body></html>"
        mock_driver.page_source = mock_html
        mock_driver.get = Mock()
        mock_driver.quit = Mock()

        results = service.scrape_weekly_injuries_pfr(2024, 5)

        assert len(results) == 0
        mock_driver.quit.assert_called_once()

    def test_get_week_injuries(self, service, mock_db_session):
        """Test getting injuries for a week."""
        mock_repo = Mock()
        service.repo = mock_repo

        mock_injuries = [
            Mock(player_name="Player 1", team="KC"),
            Mock(player_name="Player 2", team="BUF")
        ]
        mock_repo.get_by_week.return_value = mock_injuries

        results = service.get_week_injuries(2024, 5)

        assert len(results) == 2
        mock_repo.get_by_week.assert_called_once_with(2024, 5)

    def test_get_team_injuries(self, service, mock_db_session):
        """Test getting injuries for a specific team."""
        mock_repo = Mock()
        service.repo = mock_repo

        mock_injuries = [Mock(player_name="Player 1", team="KC")]
        mock_repo.get_by_team.return_value = mock_injuries

        results = service.get_team_injuries(2024, 5, "KC")

        assert len(results) == 1
        mock_repo.get_by_team.assert_called_once_with(2024, 5, "KC")

"""
Unit tests for game weather functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.entities.game_weather import GameWeather
from src.dtos.game_weather_dto import GameWeatherCreate
from src.repositories.game_weather_repo import GameWeatherRepository
from src.services.game_weather_service import GameWeatherService, STADIUM_INFO


class TestGameWeatherEntity:
    """Test GameWeather entity."""

    def test_game_weather_creation(self):
        """Test that GameWeather entity can be instantiated."""
        weather = GameWeather(
            season=2024,
            week=5,
            home_team="GB",
            stadium="Lambeau Field",
            is_dome=False,
            temperature=32.0,
            wind_speed=15.5,
            precipitation=0.0,
            humidity=65.0,
            weather_condition="Clear"
        )

        assert weather.season == 2024
        assert weather.week == 5
        assert weather.home_team == "GB"
        assert weather.stadium == "Lambeau Field"
        assert weather.is_dome is False
        assert weather.temperature == 32.0
        assert weather.wind_speed == 15.5

    def test_dome_stadium(self):
        """Test dome stadium with null weather fields."""
        weather = GameWeather(
            season=2024,
            week=5,
            home_team="DET",
            stadium="Ford Field",
            is_dome=True
        )

        assert weather.is_dome is True
        assert weather.temperature is None
        assert weather.wind_speed is None


class TestGameWeatherDTO:
    """Test GameWeatherCreate DTO validation."""

    def test_valid_dto_creation(self):
        """Test creating a valid DTO."""
        dto = GameWeatherCreate(
            season=2024,
            week=5,
            home_team="GB",
            stadium="Lambeau Field",
            is_dome=False,
            temperature=32.0,
            wind_speed=15.5,
            precipitation=0.0,
            humidity=65.0,
            weather_condition="Clear"
        )

        assert dto.season == 2024
        assert dto.home_team == "GB"
        assert dto.temperature == 32.0

    def test_dto_validation_season(self):
        """Test that season must be > 1900."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            GameWeatherCreate(
                season=1800,  # Invalid
                week=5,
                home_team="GB",
                is_dome=False
            )

    def test_dto_validation_wind_speed(self):
        """Test that wind_speed must be >= 0."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            GameWeatherCreate(
                season=2024,
                week=5,
                home_team="GB",
                is_dome=False,
                wind_speed=-10  # Invalid
            )

    def test_dto_validation_humidity(self):
        """Test that humidity must be 0-100."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            GameWeatherCreate(
                season=2024,
                week=5,
                home_team="GB",
                is_dome=False,
                humidity=150  # Invalid
            )

    def test_dto_optional_fields(self):
        """Test that weather fields are optional."""
        dto = GameWeatherCreate(
            season=2024,
            week=5,
            home_team="GB",
            is_dome=False
        )

        assert dto.temperature is None
        assert dto.wind_speed is None
        assert dto.precipitation is None


class TestGameWeatherRepository:
    """Test GameWeatherRepository."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock()

    @pytest.fixture
    def repo(self, mock_session):
        """Create a repository with mock session."""
        return GameWeatherRepository(mock_session)

    def test_create_from_dto(self, repo, mock_session):
        """Test creating weather data from DTO."""
        dto = GameWeatherCreate(
            season=2024,
            week=5,
            home_team="GB",
            stadium="Lambeau Field",
            is_dome=False,
            temperature=32.0,
            wind_speed=15.5
        )

        # Mock the session behavior
        mock_session.add = Mock()
        mock_session.commit = Mock()
        mock_session.refresh = Mock()

        result = repo.create_from_dto(dto)

        assert result.season == 2024
        assert result.home_team == "GB"
        assert result.temperature == 32.0
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()


class TestGameWeatherService:
    """Test GameWeatherService with mocked API calls."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return Mock()

    @pytest.fixture
    def service(self, mock_db_session):
        """Create a service with mock session and API key."""
        return GameWeatherService(mock_db_session, api_key="test_api_key")

    def test_get_stadium_info(self, service):
        """Test getting stadium information."""
        info = service.get_stadium_info("GB")

        assert info is not None
        stadium_name, is_dome, lat, lon = info
        assert stadium_name == "Lambeau Field"
        assert is_dome is False
        assert lat == 44.5013
        assert lon == -88.0622

    def test_get_stadium_info_dome(self, service):
        """Test getting dome stadium information."""
        info = service.get_stadium_info("DET")

        assert info is not None
        stadium_name, is_dome, lat, lon = info
        assert stadium_name == "Ford Field"
        assert is_dome is True

    def test_get_stadium_info_invalid_team(self, service):
        """Test getting stadium info for invalid team."""
        info = service.get_stadium_info("XXX")
        assert info is None

    @patch('src.services.game_weather_service.requests.get')
    def test_fetch_weather_from_api(self, mock_get, service):
        """Test fetching weather from OpenWeatherMap API."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'main': {
                'temp': 32.5,
                'humidity': 65
            },
            'wind': {
                'speed': 15.2
            },
            'weather': [
                {'main': 'Clear'}
            ],
            'rain': {'1h': 0.0},
            'snow': {'1h': 0.0}
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Fetch weather
        weather_data = service.fetch_weather_from_api(44.5013, -88.0622)

        # Verify results
        assert weather_data['temperature'] == 32.5
        assert weather_data['humidity'] == 65
        assert weather_data['wind_speed'] == 15.2
        assert weather_data['weather_condition'] == 'Clear'
        assert weather_data['precipitation'] == 0.0

        # Verify API was called correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert 'lat' in call_args[1]['params']
        assert call_args[1]['params']['lat'] == 44.5013

    @patch('src.services.game_weather_service.requests.get')
    def test_fetch_weather_api_error(self, mock_get, service):
        """Test handling API errors."""
        mock_get.side_effect = Exception("API Error")

        with pytest.raises(Exception):
            service.fetch_weather_from_api(44.5013, -88.0622)

    @patch('src.services.game_weather_service.requests.get')
    def test_fetch_and_store_outdoor_game(self, mock_get, service, mock_db_session):
        """Test fetching and storing weather for outdoor game."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'main': {'temp': 32.5, 'humidity': 65},
            'wind': {'speed': 15.2},
            'weather': [{'main': 'Clear'}],
            'rain': {'1h': 0.0},
            'snow': {'1h': 0.0}
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Mock repository
        mock_repo = Mock()
        mock_weather = Mock()
        mock_repo.upsert_game_weather.return_value = mock_weather
        service.repo = mock_repo

        # Fetch and store
        result = service.fetch_and_store_game_weather(2024, 5, "GB")

        # Verify
        assert result == mock_weather
        mock_repo.upsert_game_weather.assert_called_once()

        # Verify DTO passed to repo
        dto_arg = mock_repo.upsert_game_weather.call_args[0][0]
        assert dto_arg.home_team == "GB"
        assert dto_arg.is_dome is False
        assert dto_arg.temperature == 32.5

    def test_fetch_and_store_dome_game(self, service, mock_db_session):
        """Test storing weather for dome game (no API call)."""
        # Mock repository
        mock_repo = Mock()
        mock_weather = Mock()
        mock_repo.upsert_game_weather.return_value = mock_weather
        service.repo = mock_repo

        # Fetch and store for dome
        result = service.fetch_and_store_game_weather(2024, 5, "DET")

        # Verify
        assert result == mock_weather
        mock_repo.upsert_game_weather.assert_called_once()

        # Verify DTO has is_dome=True and no weather data
        dto_arg = mock_repo.upsert_game_weather.call_args[0][0]
        assert dto_arg.home_team == "DET"
        assert dto_arg.is_dome is True
        assert dto_arg.temperature is None

    @patch('src.services.game_weather_service.requests.get')
    def test_fetch_week_weather(self, mock_get, service, mock_db_session):
        """Test fetching weather for multiple games."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'main': {'temp': 32.5, 'humidity': 65},
            'wind': {'speed': 15.2},
            'weather': [{'main': 'Clear'}],
            'rain': {'1h': 0.0},
            'snow': {'1h': 0.0}
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Mock repository
        mock_repo = Mock()
        mock_repo.upsert_game_weather.return_value = Mock()
        service.repo = mock_repo

        # Fetch for multiple teams
        teams = ["GB", "DET", "KC"]
        results = service.fetch_week_weather(2024, 5, teams)

        # Verify
        assert len(results) == 3
        assert mock_repo.upsert_game_weather.call_count == 3

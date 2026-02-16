"""
Service for fetching and managing game weather data.
"""
import os
from typing import List, Optional, Dict
from datetime import datetime
import requests

from src.core.database import SessionLocal
from src.repositories.game_weather_repo import GameWeatherRepository
from src.dtos.game_weather_dto import GameWeatherCreate
from src.entities.game_weather import GameWeather


# Stadium information: team -> (stadium_name, is_dome, latitude, longitude)
STADIUM_INFO: Dict[str, tuple] = {
    'ARI': ('State Farm Stadium', True, 33.5276, -112.2626),
    'ATL': ('Mercedes-Benz Stadium', True, 33.7553, -84.4009),
    'BAL': ('M&T Bank Stadium', False, 39.2780, -76.6227),
    'BUF': ('Highmark Stadium', False, 42.7738, -78.7870),
    'CAR': ('Bank of America Stadium', False, 35.2258, -80.8530),
    'CHI': ('Soldier Field', False, 41.8623, -87.6167),
    'CIN': ('Paycor Stadium', False, 39.0954, -84.5160),
    'CLE': ('Cleveland Browns Stadium', False, 41.5061, -81.6995),
    'DAL': ('AT&T Stadium', True, 32.7473, -97.0945),
    'DEN': ('Empower Field at Mile High', False, 39.7439, -105.0201),
    'DET': ('Ford Field', True, 42.3400, -83.0456),
    'GB': ('Lambeau Field', False, 44.5013, -88.0622),
    'HOU': ('NRG Stadium', True, 29.6847, -95.4107),
    'IND': ('Lucas Oil Stadium', True, 39.7601, -86.1639),
    'JAX': ('TIAA Bank Field', False, 30.3239, -81.6373),
    'KC': ('GEHA Field at Arrowhead Stadium', False, 39.0489, -94.4839),
    'LAC': ('SoFi Stadium', True, 33.9535, -118.3392),
    'LAR': ('SoFi Stadium', True, 33.9535, -118.3392),
    'LV': ('Allegiant Stadium', True, 36.0909, -115.1833),
    'MIA': ('Hard Rock Stadium', False, 25.9580, -80.2389),
    'MIN': ('U.S. Bank Stadium', True, 44.9738, -93.2577),
    'NE': ('Gillette Stadium', False, 42.0909, -71.2643),
    'NO': ('Caesars Superdome', True, 29.9511, -90.0812),
    'NYG': ('MetLife Stadium', False, 40.8128, -74.0742),
    'NYJ': ('MetLife Stadium', False, 40.8128, -74.0742),
    'PHI': ('Lincoln Financial Field', False, 39.9008, -75.1675),
    'PIT': ('Acrisure Stadium', False, 40.4468, -80.0158),
    'SEA': ('Lumen Field', False, 47.5952, -122.3316),
    'SF': ('Levi\'s Stadium', False, 37.4032, -121.9698),
    'TB': ('Raymond James Stadium', False, 27.9759, -82.5033),
    'TEN': ('Nissan Stadium', False, 36.1665, -86.7713),
    'WAS': ('FedExField', False, 38.9076, -76.8645),
}


class GameWeatherService:
    """
    Service for fetching and storing game weather data.

    Uses OpenWeatherMap API to fetch weather conditions for outdoor stadium games.
    """

    def __init__(self, db_session: Optional[SessionLocal] = None, api_key: Optional[str] = None):
        """
        Initialize the service.

        Args:
            db_session: Optional database session (will create new if not provided)
            api_key: OpenWeatherMap API key (will read from env if not provided)
        """
        self.db = db_session or SessionLocal()
        self.repo = GameWeatherRepository(self.db)
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')

        if not self.api_key:
            print("Warning: OPENWEATHER_API_KEY not set. Weather fetching will not work.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            self.db.close()

    def get_stadium_info(self, team: str) -> Optional[tuple]:
        """
        Get stadium information for a team.

        Args:
            team: Team abbreviation

        Returns:
            Tuple of (stadium_name, is_dome, latitude, longitude) or None
        """
        return STADIUM_INFO.get(team.upper())

    def fetch_weather_from_api(self, latitude: float, longitude: float, game_time: Optional[datetime] = None) -> dict:
        """
        Fetch weather data from OpenWeatherMap API.

        Args:
            latitude: Stadium latitude
            longitude: Stadium longitude
            game_time: Optional scheduled game time (for forecast)

        Returns:
            Dictionary with weather data

        Raises:
            Exception: If API request fails
        """
        if not self.api_key:
            raise Exception("OpenWeatherMap API key not configured")

        # Use current weather endpoint (could be extended to use forecast API)
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'lat': latitude,
            'lon': longitude,
            'appid': self.api_key,
            'units': 'imperial'  # Fahrenheit
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Extract relevant weather data
            weather_data = {
                'temperature': data['main'].get('temp'),
                'humidity': data['main'].get('humidity'),
                'wind_speed': data['wind'].get('speed'),
                'weather_condition': data['weather'][0].get('main') if data.get('weather') else None,
                'precipitation': data.get('rain', {}).get('1h', 0) + data.get('snow', {}).get('1h', 0),
            }

            return weather_data

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch weather data: {e}")

    def fetch_and_store_game_weather(self, season: int, week: int, home_team: str, game_time: Optional[datetime] = None) -> Optional[GameWeather]:
        """
        Fetch weather data for a game and store it in the database.

        For domed stadiums, creates a record with is_dome=True and null weather fields.

        Args:
            season: NFL season year
            week: Week number
            home_team: Home team abbreviation
            game_time: Optional scheduled game time

        Returns:
            Created GameWeather entity or None if team not found
        """
        stadium_info = self.get_stadium_info(home_team)
        if not stadium_info:
            print(f"No stadium info found for team: {home_team}")
            return None

        stadium_name, is_dome, lat, lon = stadium_info

        # For domed stadiums, just create a record without weather data
        if is_dome:
            dto = GameWeatherCreate(
                season=season,
                week=week,
                home_team=home_team,
                stadium=stadium_name,
                is_dome=True,
                game_time=game_time
            )
            return self.repo.upsert_game_weather(dto)

        # For outdoor stadiums, fetch weather data
        try:
            weather_data = self.fetch_weather_from_api(lat, lon, game_time)

            dto = GameWeatherCreate(
                season=season,
                week=week,
                home_team=home_team,
                stadium=stadium_name,
                is_dome=False,
                temperature=weather_data.get('temperature'),
                wind_speed=weather_data.get('wind_speed'),
                precipitation=weather_data.get('precipitation'),
                humidity=weather_data.get('humidity'),
                weather_condition=weather_data.get('weather_condition'),
                game_time=game_time
            )

            return self.repo.upsert_game_weather(dto)

        except Exception as e:
            print(f"Error fetching weather for {home_team}: {e}")
            # Create record with stadium info but no weather data
            dto = GameWeatherCreate(
                season=season,
                week=week,
                home_team=home_team,
                stadium=stadium_name,
                is_dome=False,
                game_time=game_time
            )
            return self.repo.upsert_game_weather(dto)

    def fetch_week_weather(self, season: int, week: int, home_teams: List[str]) -> List[GameWeather]:
        """
        Fetch weather data for multiple games in a week.

        Args:
            season: NFL season year
            week: Week number
            home_teams: List of home team abbreviations

        Returns:
            List of created GameWeather entities
        """
        results = []
        for team in home_teams:
            try:
                weather = self.fetch_and_store_game_weather(season, week, team)
                if weather:
                    results.append(weather)
            except Exception as e:
                print(f"Error processing weather for {team}: {e}")
                continue

        return results

    def get_week_weather(self, season: int, week: int) -> List[GameWeather]:
        """
        Get all weather data for a specific week.

        Args:
            season: NFL season year
            week: Week number

        Returns:
            List of GameWeather entities
        """
        return self.repo.get_by_week(season, week)

    def get_outdoor_games_weather(self, season: int, week: int) -> List[GameWeather]:
        """
        Get weather data for outdoor stadium games only.

        Args:
            season: NFL season year
            week: Week number

        Returns:
            List of GameWeather entities for outdoor games
        """
        return self.repo.get_outdoor_games(season, week)

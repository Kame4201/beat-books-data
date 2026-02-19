"""
Unit tests for team_offense_service.py

Tests cover:
- get_team_offense_dataframe: Mock HTTP request + BeautifulSoup parsing
- parse_team_offense: Verify DTOs are created from DataFrame
- scrape_and_store_team_offense: Verify repo.create is called for each record

Run with:
    pytest tests/test_unit/test_services/test_team_offense_service.py -v
"""

import pytest
import pandas as pd
from decimal import Decimal
from unittest.mock import patch, MagicMock

from src.services.team_offense_service import (
    clean_value,
    get_team_offense_dataframe,
    parse_team_offense,
    scrape_and_store_team_offense,
)
from src.dtos.team_offense_dto import TeamOffenseCreate
from src.entities.team_offense import TeamOffense


# ---- Sample HTML for mocking PFR responses ----
SAMPLE_PFR_HTML = """
<html>
<body>
<table id="team_stats">
  <thead>
    <tr><th>Rk</th><th>Tm</th><th>G</th><th>PF</th><th>Yds</th><th>Ply</th>
        <th>Y/P</th><th>TO</th><th>FL</th><th>1stD</th>
        <th>Cmp</th><th>Att</th><th>Yds</th><th>TD</th><th>Int</th>
        <th>NY/A</th><th>1stD</th>
        <th>Att</th><th>Yds</th><th>TD</th><th>Y/A</th><th>1stD</th>
        <th>Pen</th><th>Yds</th><th>1stPy</th>
        <th>Sc%</th><th>TO%</th><th>O/Pl</th></tr>
  </thead>
  <tbody>
    <tr>
      <th data-stat="ranker">1</th>
      <td data-stat="team"><a href="/teams/kan/2023.htm">Kansas City Chiefs</a></td>
      <td>17</td><td>450</td><td>6200</td><td>1050</td>
      <td>5.9</td><td>12</td><td>5</td><td>350</td>
      <td>380</td><td>580</td><td>4800</td><td>35</td><td>10</td>
      <td>7.2</td><td>200</td>
      <td>420</td><td>1400</td><td>15</td><td>4.5</td><td>100</td>
      <td>95</td><td>800</td><td>50</td>
      <td>42.5</td><td>10.2</td><td>125.5</td>
    </tr>
    <tr>
      <th data-stat="ranker">2</th>
      <td data-stat="team"><a href="/teams/sfo/2023.htm">San Francisco 49ers</a></td>
      <td>17</td><td>420</td><td>5900</td><td>1020</td>
      <td>5.8</td><td>14</td><td>6</td><td>330</td>
      <td>360</td><td>560</td><td>4500</td><td>30</td><td>12</td>
      <td>6.8</td><td>190</td>
      <td>400</td><td>1400</td><td>12</td><td>4.3</td><td>90</td>
      <td>100</td><td>850</td><td>45</td>
      <td>40.0</td><td>11.5</td><td>118.0</td>
    </tr>
  </tbody>
</table>
</body>
</html>
"""


class TestCleanValue:
    """Tests for the clean_value utility function."""

    def test_clean_none(self):
        """NaN-like values should return None."""
        import numpy as np

        assert clean_value(float("nan")) is None
        assert clean_value(np.nan) is None

    def test_clean_numpy_int(self):
        """numpy int64 should be converted to Python int."""
        import numpy as np

        result = clean_value(np.int64(42))
        assert result == 42
        assert isinstance(result, int)

    def test_clean_numpy_float(self):
        """numpy float64 should be converted to Python float."""
        import numpy as np

        result = clean_value(np.float64(3.14))
        assert isinstance(result, float)

    def test_clean_regular_value(self):
        """Regular Python values pass through unchanged."""
        assert clean_value("hello") == "hello"
        assert clean_value(42) == 42
        assert clean_value(None) is None


class TestGetTeamOffenseDataframe:
    """Tests for get_team_offense_dataframe with mocked HTTP."""

    @patch("requests.get")
    def test_returns_dataframe(self, mock_get):
        """Should return a DataFrame with team offense rows."""
        mock_response = MagicMock()
        mock_response.text = SAMPLE_PFR_HTML
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        df = get_team_offense_dataframe(2023)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        mock_get.assert_called_once_with(
            "https://www.pro-football-reference.com/years/2023/",
            timeout=30,
        )

    @patch("requests.get")
    def test_raises_on_missing_table(self, mock_get):
        """Should raise Exception when team_stats table is not found."""
        mock_response = MagicMock()
        mock_response.text = "<html><body><p>No tables here</p></body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with pytest.raises(Exception, match="Could not find team_stats table"):
            get_team_offense_dataframe(2023)


class TestParseTeamOffense:
    """Tests for parse_team_offense DataFrame -> dicts."""

    def test_parse_correct_fields(self):
        """Parsed records should contain expected keys and values."""
        data = {
            "Rk": [1],
            "Tm": ["Kansas City Chiefs"],
            "G": [17],
            "PF": [450],
            "Yds": [6200],
            "Ply": [1050],
            "Y/P": [5.9],
            "TO": [12],
            "FL": [5],
            "1stD": [350],
            "Cmp": [380],
            "Att": [580],
            "Yds.1": [4800],
            "TD": [35],
            "Int": [10],
            "NY/A": [7.2],
            "1stD.1": [200],
            "Att.1": [420],
            "Yds.2": [1400],
            "TD.1": [15],
            "Y/A": [4.5],
            "1stD.2": [100],
            "Pen": [95],
            "Yds.3": [800],
            "1stPy": [50],
            "Sc%": [42.5],
            "TO%": [10.2],
            "O/Pl": [125.5],
        }
        df = pd.DataFrame(data)

        result = parse_team_offense(df, 2023)

        assert len(result) == 1
        record = result[0]
        assert record["season"] == 2023
        assert record["tm"] == "Kansas City Chiefs"
        assert record["g"] == 17
        assert record["pf"] == 450
        assert record["yds"] == 6200
        assert record["td_pass"] == 35
        assert record["att_rush"] == 420

    def test_parse_creates_valid_dtos(self):
        """Parsed records should be valid for TeamOffenseCreate DTO."""
        data = {
            "Rk": [1],
            "Tm": ["KAN"],
            "G": [17],
            "PF": [450],
            "Yds": [6200],
            "Ply": [1050],
            "Y/P": [5.9],
            "TO": [12],
            "FL": [5],
            "1stD": [350],
            "Cmp": [380],
            "Att": [580],
            "Yds.1": [4800],
            "TD": [35],
            "Int": [10],
            "NY/A": [7.2],
            "1stD.1": [200],
            "Att.1": [420],
            "Yds.2": [1400],
            "TD.1": [15],
            "Y/A": [4.5],
            "1stD.2": [100],
            "Pen": [95],
            "Yds.3": [800],
            "1stPy": [50],
            "Sc%": [42.5],
            "TO%": [10.2],
            "O/Pl": [125.5],
        }
        df = pd.DataFrame(data)

        parsed = parse_team_offense(df, 2023)
        # Should not raise validation errors
        dto = TeamOffenseCreate(**parsed[0])
        assert dto.season == 2023
        assert dto.tm == "KAN"

    def test_parse_empty_dataframe(self):
        """Parsing an empty DataFrame should return an empty list."""
        df = pd.DataFrame()
        result = parse_team_offense(df, 2023)
        assert result == []


class TestScrapeAndStoreTeamOffense:
    """Tests for scrape_and_store_team_offense end-to-end with mocks."""

    @pytest.mark.asyncio
    @patch("src.services.team_offense_service.SessionLocal")
    @patch("src.services.team_offense_service.get_team_offense_dataframe")
    def test_calls_repo_create_for_each_record(self, mock_get_df, mock_session_local):
        """Should call repo.create for each parsed record."""
        # Set up mock DataFrame
        data = {
            "Rk": [1, 2],
            "Tm": ["KAN", "SFO"],
            "G": [17, 17],
            "PF": [450, 420],
            "Yds": [6200, 5900],
            "Ply": [1050, 1020],
            "Y/P": [5.9, 5.8],
            "TO": [12, 14],
            "FL": [5, 6],
            "1stD": [350, 330],
            "Cmp": [380, 360],
            "Att": [580, 560],
            "Yds.1": [4800, 4500],
            "TD": [35, 30],
            "Int": [10, 12],
            "NY/A": [7.2, 6.8],
            "1stD.1": [200, 190],
            "Att.1": [420, 400],
            "Yds.2": [1400, 1400],
            "TD.1": [15, 12],
            "Y/A": [4.5, 4.3],
            "1stD.2": [100, 90],
            "Pen": [95, 100],
            "Yds.3": [800, 850],
            "1stPy": [50, 45],
            "Sc%": [42.5, 40.0],
            "TO%": [10.2, 11.5],
            "O/Pl": [125.5, 118.0],
        }
        mock_get_df.return_value = pd.DataFrame(data)

        # Set up mock session
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session

        import asyncio

        result = asyncio.get_event_loop().run_until_complete(
            scrape_and_store_team_offense(2023)
        )

        # Should have added 2 objects to session
        assert mock_session.add.call_count == 2
        assert mock_session.commit.called
        assert len(result) == 2

    @pytest.mark.asyncio
    @patch("src.services.team_offense_service.SessionLocal")
    @patch("src.services.team_offense_service.get_team_offense_dataframe")
    def test_session_closed_on_success(self, mock_get_df, mock_session_local):
        """Session should be closed after successful scrape."""
        mock_get_df.return_value = pd.DataFrame()
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session

        import asyncio

        asyncio.get_event_loop().run_until_complete(
            scrape_and_store_team_offense(2023)
        )

        assert mock_session.close.called

    @pytest.mark.asyncio
    @patch("src.services.team_offense_service.SessionLocal")
    @patch("src.services.team_offense_service.get_team_offense_dataframe")
    def test_session_closed_on_failure(self, mock_get_df, mock_session_local):
        """Session should be closed even when scraping fails."""
        mock_get_df.side_effect = Exception("Network error")
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session

        import asyncio

        with pytest.raises(Exception, match="Network error"):
            asyncio.get_event_loop().run_until_complete(
                scrape_and_store_team_offense(2023)
            )

        assert mock_session.close.called

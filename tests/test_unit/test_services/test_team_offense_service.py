"""
Unit tests for team_offense_service.py

Tests cover:
- get_dataframe: Mock Selenium + BeautifulSoup parsing via retry_with_backoff
- scrape_and_store_team_offense: Verify repo.create is called for each record

Run with:
    pytest tests/test_unit/test_services/test_team_offense_service.py -v
"""

import pytest
import asyncio
from decimal import Decimal
from unittest.mock import patch, MagicMock

from src.services.team_offense_service import (
    get_dataframe,
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
    <tr><th>Rk</th><th>Tm</th><th>G</th></tr>
  </thead>
  <tbody>
    <tr>
      <td data-stat="team"><a href="/teams/kan/2023.htm">Kansas City Chiefs</a></td>
      <td data-stat="g">17</td>
      <td data-stat="points">450</td>
      <td data-stat="total_yards">6200</td>
      <td data-stat="plays_offense">1050</td>
      <td data-stat="yds_per_play_offense">5.9</td>
      <td data-stat="turnovers">12</td>
      <td data-stat="fumbles_lost">5</td>
      <td data-stat="first_down">350</td>
      <td data-stat="pass_cmp">380</td>
      <td data-stat="pass_att">580</td>
      <td data-stat="pass_yds">4800</td>
      <td data-stat="pass_td">35</td>
      <td data-stat="pass_int">10</td>
      <td data-stat="pass_net_yds_per_att">7.2</td>
      <td data-stat="pass_fd">200</td>
      <td data-stat="rush_att">420</td>
      <td data-stat="rush_yds">1400</td>
      <td data-stat="rush_td">15</td>
      <td data-stat="rush_yds_per_att">4.5</td>
      <td data-stat="rush_fd">100</td>
      <td data-stat="penalties">95</td>
      <td data-stat="penalties_yds">800</td>
      <td data-stat="pen_fd">50</td>
      <td data-stat="score_pct">42.5</td>
      <td data-stat="turnover_pct">10.2</td>
      <td data-stat="exp_pts_tot">125.5</td>
    </tr>
    <tr>
      <td data-stat="team"><a href="/teams/sfo/2023.htm">San Francisco 49ers</a></td>
      <td data-stat="g">17</td>
      <td data-stat="points">420</td>
      <td data-stat="total_yards">5900</td>
      <td data-stat="plays_offense">1020</td>
      <td data-stat="yds_per_play_offense">5.8</td>
      <td data-stat="turnovers">14</td>
      <td data-stat="fumbles_lost">6</td>
      <td data-stat="first_down">330</td>
      <td data-stat="pass_cmp">360</td>
      <td data-stat="pass_att">560</td>
      <td data-stat="pass_yds">4500</td>
      <td data-stat="pass_td">30</td>
      <td data-stat="pass_int">12</td>
      <td data-stat="pass_net_yds_per_att">6.8</td>
      <td data-stat="pass_fd">190</td>
      <td data-stat="rush_att">400</td>
      <td data-stat="rush_yds">1400</td>
      <td data-stat="rush_td">12</td>
      <td data-stat="rush_yds_per_att">4.3</td>
      <td data-stat="rush_fd">90</td>
      <td data-stat="penalties">100</td>
      <td data-stat="penalties_yds">850</td>
      <td data-stat="pen_fd">45</td>
      <td data-stat="score_pct">40.0</td>
      <td data-stat="turnover_pct">11.5</td>
      <td data-stat="exp_pts_tot">118.0</td>
    </tr>
  </tbody>
</table>
</body>
</html>
"""


class TestGetDataframe:
    """Tests for get_dataframe with mocked Selenium."""

    @patch("src.services.team_offense_service.find_pfr_table")
    @patch("src.services.team_offense_service.retry_with_backoff")
    def test_returns_parsed_rows(self, mock_retry, mock_find_table):
        """Should return a list of dicts with mapped column names."""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(SAMPLE_PFR_HTML, "lxml")
        table = soup.find("table", {"id": "team_stats"})
        mock_retry.return_value = SAMPLE_PFR_HTML
        mock_find_table.return_value = table

        result = get_dataframe(2023)

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["season"] == 2023
        assert result[0]["tm"] == "Kansas City Chiefs"
        assert result[0]["g"] == "17"
        assert result[0]["pf"] == "450"

    @patch("src.services.team_offense_service.find_pfr_table")
    @patch("src.services.team_offense_service.retry_with_backoff")
    def test_raises_on_missing_table(self, mock_retry, mock_find_table):
        """Should raise Exception when team_stats table is not found."""
        mock_retry.return_value = "<html><body></body></html>"
        mock_find_table.return_value = None

        with pytest.raises(Exception, match="Could not find team_stats table"):
            get_dataframe(2023)


class TestScrapeAndStoreTeamOffense:
    """Tests for scrape_and_store_team_offense end-to-end with mocks."""

    @pytest.mark.asyncio
    @patch("src.services.team_offense_service.SessionLocal")
    @patch("src.services.team_offense_service.get_dataframe")
    def test_calls_repo_create_for_each_record(self, mock_get_df, mock_session_local):
        """Should call repo.create for each parsed record."""
        mock_get_df.return_value = [
            {
                "season": 2023,
                "tm": "KAN",
                "g": 17,
                "pf": 450,
                "yds": 6200,
                "ply": 1050,
                "ypp": "5.9",
                "turnovers": 12,
                "fl": 5,
                "firstd_total": 350,
                "cmp": 380,
                "att_pass": 580,
                "yds_pass": 4800,
                "td_pass": 35,
                "ints": 10,
                "nypa": "7.2",
                "firstd_pass": 200,
                "att_rush": 420,
                "yds_rush": 1400,
                "td_rush": 15,
                "ypa": "4.5",
                "firstd_rush": 100,
                "pen": 95,
                "yds_pen": 800,
                "firstpy": 50,
                "sc_pct": "42.5",
                "to_pct": "10.2",
                "opea": "125.5",
            },
            {
                "season": 2023,
                "tm": "SFO",
                "g": 17,
                "pf": 420,
                "yds": 5900,
                "ply": 1020,
                "ypp": "5.8",
                "turnovers": 14,
                "fl": 6,
                "firstd_total": 330,
                "cmp": 360,
                "att_pass": 560,
                "yds_pass": 4500,
                "td_pass": 30,
                "ints": 12,
                "nypa": "6.8",
                "firstd_pass": 190,
                "att_rush": 400,
                "yds_rush": 1400,
                "td_rush": 12,
                "ypa": "4.3",
                "firstd_rush": 90,
                "pen": 100,
                "yds_pen": 850,
                "firstpy": 45,
                "sc_pct": "40.0",
                "to_pct": "11.5",
                "opea": "118.0",
            },
        ]

        mock_session = MagicMock()
        mock_session_local.return_value = mock_session

        result = asyncio.get_event_loop().run_until_complete(
            scrape_and_store_team_offense(2023)
        )

        assert mock_session.commit.called
        assert len(result) == 2

    @pytest.mark.asyncio
    @patch("src.services.team_offense_service.SessionLocal")
    @patch("src.services.team_offense_service.get_dataframe")
    def test_session_closed_on_success(self, mock_get_df, mock_session_local):
        """Session should be closed after successful scrape."""
        mock_get_df.return_value = []
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session

        asyncio.get_event_loop().run_until_complete(scrape_and_store_team_offense(2023))

        assert mock_session.close.called

    @pytest.mark.asyncio
    @patch("src.services.team_offense_service.SessionLocal")
    @patch("src.services.team_offense_service.get_dataframe")
    def test_session_closed_on_failure(self, mock_get_df, mock_session_local):
        """Session should be closed even when scraping fails."""
        mock_get_df.side_effect = Exception("Network error")
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session

        with pytest.raises(Exception, match="Network error"):
            asyncio.get_event_loop().run_until_complete(
                scrape_and_store_team_offense(2023)
            )

        assert mock_session.close.called

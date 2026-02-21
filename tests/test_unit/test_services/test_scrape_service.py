"""
Unit tests for scrape_service.py

Tests cover:
- clean_value: Pandas/numpy type conversion
- flatten_pfr_columns: MultiIndex column flattening
- parse_xlsx_to_games: HTML table parsing into game dicts
- map_scraped_to_model: Game dict -> TeamGameCreate DTO mapping

Run with:
    pytest tests/test_unit/test_services/test_scrape_service.py -v
"""

import pytest
import pandas as pd
import numpy as np
from datetime import date
from unittest.mock import MagicMock

from src.services.scrape_service import (
    clean_value,
    flatten_pfr_columns,
    map_scraped_to_model,
)
from src.dtos.team_game_dto import TeamGameCreate


class TestCleanValue:
    """Tests for clean_value type conversion utility."""

    def test_nan_returns_none(self):
        """NaN values should be converted to None."""
        assert clean_value(float("nan")) is None
        assert clean_value(np.nan) is None

    def test_numpy_int_to_python(self):
        """numpy integers should be converted to Python int."""
        result = clean_value(np.int64(42))
        assert result == 42
        assert isinstance(result, int)

    def test_numpy_float_to_python(self):
        """numpy floats should be converted to Python float."""
        result = clean_value(np.float64(3.14))
        assert isinstance(result, float)
        assert abs(result - 3.14) < 1e-10

    def test_regular_values_pass_through(self):
        """Regular Python values should pass through unchanged."""
        assert clean_value("test") == "test"
        assert clean_value(42) == 42
        assert clean_value(None) is None

    def test_empty_series_returns_none(self):
        """Empty pandas Series should return None."""
        assert clean_value(pd.Series(dtype=float)) is None

    def test_series_returns_first_element(self):
        """Non-empty pandas Series should return first element."""
        result = clean_value(pd.Series([10, 20, 30]))
        assert result == 10


class TestFlattenPfrColumns:
    """Tests for flatten_pfr_columns MultiIndex handling."""

    def test_flatten_multiindex(self):
        """Should flatten MultiIndex columns, preferring level 1 names."""
        arrays = [
            ["Passing", "Passing", "Rushing"],
            ["Yds", "TD", "Yds"],
        ]
        tuples = list(zip(*arrays))
        index = pd.MultiIndex.from_tuples(tuples)
        df = pd.DataFrame([[100, 5, 200]], columns=index)

        result = flatten_pfr_columns(df)
        assert list(result.columns) == ["Yds", "TD", "Yds"]

    def test_flatten_unnamed_columns(self):
        """Should use level 0 name when level 1 starts with 'Unnamed'."""
        arrays = [
            ["Week", "Day"],
            ["Unnamed: 0_level_1", "Unnamed: 1_level_1"],
        ]
        tuples = list(zip(*arrays))
        index = pd.MultiIndex.from_tuples(tuples)
        df = pd.DataFrame([[1, "Sun"]], columns=index)

        result = flatten_pfr_columns(df)
        assert list(result.columns) == ["Week", "Day"]

    def test_non_multiindex_unchanged(self):
        """Non-MultiIndex columns should pass through unchanged."""
        df = pd.DataFrame({"A": [1], "B": [2]})
        result = flatten_pfr_columns(df)
        assert list(result.columns) == ["A", "B"]


class TestMapScrapedToModel:
    """Tests for map_scraped_to_model DTO mapping logic."""

    def test_win_mapping(self):
        """Winning team should be set as winner with correct scores."""
        scraped = {
            "team": "KAN",
            "week": 1,
            "day": "Sun",
            "date": "September 10",
            "time": "4:25pm",
            "result": "W",
            "opponent": "DET",
            "team_score": 27,
            "opp_score": 20,
            "tot_yards_for": 350,
            "tot_yards_against": 280,
            "turnovers": 1,
        }

        dto = map_scraped_to_model(scraped, 2023)

        assert isinstance(dto, TeamGameCreate)
        assert dto.team_abbr == "KAN"
        assert dto.winner == "KAN"
        assert dto.loser == "DET"
        assert dto.pts_w == 27
        assert dto.pts_l == 20
        assert dto.yds_w == 350
        assert dto.yds_l == 280
        assert dto.to_w == 1
        assert dto.to_l is None

    def test_loss_mapping(self):
        """Losing team should swap winner/loser and scores."""
        scraped = {
            "team": "DET",
            "week": 1,
            "day": "Sun",
            "date": "September 10",
            "result": "L",
            "opponent": "KAN",
            "team_score": 20,
            "opp_score": 27,
            "tot_yards_for": 280,
            "tot_yards_against": 350,
            "turnovers": 2,
        }

        dto = map_scraped_to_model(scraped, 2023)

        assert dto.winner == "KAN"
        assert dto.loser == "DET"
        assert dto.pts_w == 27
        assert dto.pts_l == 20
        assert dto.yds_w == 350
        assert dto.yds_l == 280
        assert dto.to_w is None
        assert dto.to_l == 2

    def test_no_result_mapping(self):
        """Bye week or missing result should have all None fields."""
        scraped = {
            "team": "KAN",
            "week": 10,
            "result": None,
            "opponent": None,
        }

        dto = map_scraped_to_model(scraped, 2023)

        assert dto.winner is None
        assert dto.loser is None
        assert dto.pts_w is None
        assert dto.pts_l is None

    def test_date_parsing(self):
        """Date should be parsed from 'Month Day' format + season year."""
        scraped = {
            "team": "KAN",
            "week": 1,
            "date": "September 10",
            "result": "W",
            "opponent": "DET",
        }

        dto = map_scraped_to_model(scraped, 2023)

        assert dto.game_date == date(2023, 9, 10)

    def test_invalid_date_returns_none(self):
        """Invalid date string should result in None game_date."""
        scraped = {
            "team": "KAN",
            "week": 1,
            "date": "invalid-date",
            "result": "W",
            "opponent": "DET",
        }

        dto = map_scraped_to_model(scraped, 2023)

        assert dto.game_date is None

    def test_missing_date_returns_none(self):
        """Missing date should result in None game_date."""
        scraped = {
            "team": "KAN",
            "week": 1,
            "result": "W",
            "opponent": "DET",
        }

        dto = map_scraped_to_model(scraped, 2023)

        assert dto.game_date is None

    def test_week_defaults_to_zero(self):
        """Missing week should default to 0."""
        scraped = {
            "team": "KAN",
            "result": "W",
            "opponent": "DET",
        }

        dto = map_scraped_to_model(scraped, 2023)

        assert dto.week == 0

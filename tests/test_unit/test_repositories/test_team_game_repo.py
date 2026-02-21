"""
Unit tests for TeamGameRepository.

Tests cover:
- create_from_dto: Create entity from DTO
- find_by_unique_key: Lookup by (team_abbr, season, week)
- create_or_skip: Idempotent insert (skip duplicates)
- find_by_season_and_week: Filtered listing with sort/pagination
- count_by_season: Count with optional week filter

Run with:
    pytest tests/test_unit/test_repositories/test_team_game_repo.py -v
"""

import pytest
from datetime import date

from src.entities.team_game import TeamGame
from src.dtos.team_game_dto import TeamGameCreate
from src.repositories.team_game_repo import TeamGameRepository


class TestTeamGameRepository:
    """Tests for the refactored TeamGameRepository."""

    @pytest.fixture
    def repo(self, db_session):
        return TeamGameRepository(db_session)

    @pytest.fixture
    def sample_dto(self):
        return TeamGameCreate(
            team_abbr="KAN",
            season=2023,
            week=1,
            day="Sun",
            game_date=date(2023, 9, 10),
            game_time="4:25pm",
            winner="KAN",
            loser="DET",
            pts_w=27,
            pts_l=20,
            yds_w=350,
            to_w=1,
            yds_l=280,
            to_l=2,
        )

    def test_create_from_dto(self, repo, sample_dto):
        """Should create a TeamGame entity from a DTO."""
        result = repo.create_from_dto(sample_dto)

        assert result.id is not None
        assert result.team_abbr == "KAN"
        assert result.season == 2023
        assert result.week == 1
        assert result.winner == "KAN"
        assert result.pts_w == 27

    def test_find_by_unique_key(self, repo, sample_dto):
        """Should find a game by (team_abbr, season, week)."""
        repo.create_from_dto(sample_dto)

        found = repo.find_by_unique_key("KAN", 2023, 1)
        assert found is not None
        assert found.team_abbr == "KAN"

    def test_find_by_unique_key_not_found(self, repo):
        """Should return None when game doesn't exist."""
        found = repo.find_by_unique_key("KAN", 2023, 99)
        assert found is None

    def test_create_or_skip_new(self, repo, sample_dto):
        """Should create a new game when no duplicate exists."""
        result = repo.create_or_skip(sample_dto)
        assert result.id is not None
        assert result.team_abbr == "KAN"

    def test_create_or_skip_duplicate(self, repo, sample_dto):
        """Should return existing game when duplicate exists."""
        first = repo.create_or_skip(sample_dto)
        second = repo.create_or_skip(sample_dto)

        assert first.id == second.id  # Same record returned

    def test_find_by_season_and_week(self, repo):
        """Should filter games by season and optional week."""
        # Create games across different weeks
        for week in [1, 2, 3]:
            dto = TeamGameCreate(
                team_abbr="KAN", season=2023, week=week, winner="KAN", loser="DET"
            )
            repo.create_from_dto(dto)

        # Find all games in season
        all_games = repo.find_by_season_and_week(2023)
        assert len(all_games) == 3

        # Find games in week 2 only
        week2 = repo.find_by_season_and_week(2023, week=2)
        assert len(week2) == 1
        assert week2[0].week == 2

    def test_find_by_season_and_week_sorting(self, repo):
        """Should sort results by specified column and order."""
        for week in [3, 1, 2]:
            dto = TeamGameCreate(
                team_abbr="KAN", season=2023, week=week, winner="KAN", loser="DET"
            )
            repo.create_from_dto(dto)

        asc_games = repo.find_by_season_and_week(2023, sort_by="week", order="asc")
        assert [g.week for g in asc_games] == [1, 2, 3]

        desc_games = repo.find_by_season_and_week(2023, sort_by="week", order="desc")
        assert [g.week for g in desc_games] == [3, 2, 1]

    def test_find_by_season_and_week_pagination(self, repo):
        """Should support limit and offset for pagination."""
        for week in range(1, 6):
            dto = TeamGameCreate(
                team_abbr="KAN", season=2023, week=week, winner="KAN", loser="DET"
            )
            repo.create_from_dto(dto)

        page1 = repo.find_by_season_and_week(2023, limit=2, offset=0)
        assert len(page1) == 2

        page2 = repo.find_by_season_and_week(2023, limit=2, offset=2)
        assert len(page2) == 2

    def test_count_by_season(self, repo):
        """Should count games for a season."""
        for week in [1, 2, 3]:
            dto = TeamGameCreate(
                team_abbr="KAN", season=2023, week=week, winner="KAN", loser="DET"
            )
            repo.create_from_dto(dto)

        assert repo.count_by_season(2023) == 3
        assert repo.count_by_season(2023, week=1) == 1
        assert repo.count_by_season(2024) == 0

    def test_inherits_base_crud(self, repo, sample_dto):
        """Should inherit BaseRepository CRUD methods."""
        # create
        entity = TeamGame(**sample_dto.model_dump())
        saved = repo.create(entity)
        assert saved.id is not None

        # get_by_id
        found = repo.get_by_id(saved.id)
        assert found is not None
        assert found.team_abbr == "KAN"

        # list
        all_records = repo.list()
        assert len(all_records) == 1

        # delete
        repo.delete(saved)
        assert repo.get_by_id(saved.id) is None

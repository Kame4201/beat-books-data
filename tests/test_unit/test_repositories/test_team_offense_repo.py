"""
Unit tests for team_offense_repo.py (TeamOffenseRepository)

Tests verify that TeamOffenseRepository correctly inherits BaseRepository
and works with the TeamOffense entity using an in-memory SQLite database.

Run with:
    pytest tests/test_unit/test_repositories/test_team_offense_repo.py -v
"""

import pytest
from decimal import Decimal

from src.entities.team_offense import TeamOffense
from src.repositories.team_offense_repo import TeamOffenseRepository


class TestTeamOffenseRepository:
    """Integration tests for TeamOffenseRepository with in-memory DB."""

    def test_create_team_offense(self, db_session, sample_team_offense):
        """Should persist a TeamOffense entity."""
        repo = TeamOffenseRepository(db_session)

        result = repo.create(sample_team_offense)

        assert result.id is not None
        assert result.tm == "KAN"
        assert result.season == 2023

    def test_get_by_id(self, db_session, sample_team_offense):
        """Should retrieve a TeamOffense entity by ID."""
        repo = TeamOffenseRepository(db_session)
        created = repo.create(sample_team_offense)

        result = repo.get_by_id(created.id)

        assert result is not None
        assert result.tm == "KAN"
        assert result.pf == 450

    def test_list_team_offenses(self, db_session):
        """Should list multiple TeamOffense entities."""
        repo = TeamOffenseRepository(db_session)

        team1 = TeamOffense(season=2023, tm="KAN", g=17, pf=450)
        team2 = TeamOffense(season=2023, tm="SFO", g=17, pf=420)
        repo.create(team1)
        repo.create(team2)

        result = repo.list()

        assert len(result) == 2

    def test_update_team_offense(self, db_session, sample_team_offense):
        """Should update an existing TeamOffense entity."""
        repo = TeamOffenseRepository(db_session)
        created = repo.create(sample_team_offense)

        created.pf = 500
        updated = repo.update(created)

        assert updated.pf == 500
        fetched = repo.get_by_id(created.id)
        assert fetched.pf == 500

    def test_delete_team_offense(self, db_session, sample_team_offense):
        """Should delete a TeamOffense entity."""
        repo = TeamOffenseRepository(db_session)
        created = repo.create(sample_team_offense)
        entity_id = created.id

        repo.delete(created)

        assert repo.get_by_id(entity_id) is None

    def test_create_without_commit(self, db_session):
        """Create with commit=False should not persist on rollback."""
        repo = TeamOffenseRepository(db_session)
        entity = TeamOffense(season=2023, tm="BUF", g=17)

        repo.create(entity, commit=False)
        db_session.rollback()

        result = repo.list()
        assert len(result) == 0

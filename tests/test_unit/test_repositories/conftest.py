import pytest
from src.entities.team_offense import TeamOffense


@pytest.fixture
def sample_team_offense():
    """A TeamOffense entity with representative data for unit tests."""
    return TeamOffense(
        season=2023, rk=1, tm="KAN", g=17, pf=450,
    )

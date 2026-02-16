"""
Unit tests for DTO validation.
"""
import pytest
from decimal import Decimal
from datetime import date
from pydantic import ValidationError

from src.dtos.team_offense_dto import TeamOffenseCreate, TeamOffenseResponse
from src.dtos.team_defense_dto import TeamDefenseCreate, TeamDefenseResponse
from src.dtos.passing_stats_dto import PassingStatsCreate, PassingStatsResponse
from src.dtos.rushing_stats_dto import RushingStatsCreate, RushingStatsResponse
from src.dtos.receiving_stats_dto import ReceivingStatsCreate, ReceivingStatsResponse
from src.dtos.defense_stats_dto import DefenseStatsCreate, DefenseStatsResponse
from src.dtos.kicking_stats_dto import KickingStatsCreate, KickingStatsResponse
from src.dtos.punting_stats_dto import PuntingStatsCreate, PuntingStatsResponse
from src.dtos.return_stats_dto import ReturnStatsCreate, ReturnStatsResponse
from src.dtos.scoring_stats_dto import ScoringStatsCreate, ScoringStatsResponse
from src.dtos.standings_dto import StandingsCreate, StandingsResponse
from src.dtos.games_dto import GamesCreate, GamesResponse


class TestTeamOffenseDTO:
    """Tests for TeamOffense DTO validation."""

    def test_valid_create(self):
        """Test creating a valid TeamOffenseCreate DTO."""
        dto = TeamOffenseCreate(
            season=2023,
            tm="KAN",
            g=17,
            pf=450,
            yds=6000,
            sc_pct=Decimal("45.5")
        )
        assert dto.season == 2023
        assert dto.tm == "KAN"
        assert dto.g == 17

    def test_season_range_validation(self):
        """Test season must be between 1920-2100."""
        with pytest.raises(ValidationError):
            TeamOffenseCreate(season=1900, tm="KAN")

        with pytest.raises(ValidationError):
            TeamOffenseCreate(season=2150, tm="KAN")

    def test_negative_stats_rejected(self):
        """Test that negative stats are rejected."""
        with pytest.raises(ValidationError):
            TeamOffenseCreate(season=2023, tm="KAN", pf=-10)

        with pytest.raises(ValidationError):
            TeamOffenseCreate(season=2023, tm="KAN", yds=-100)

    def test_empty_team_name_rejected(self):
        """Test that empty team name is rejected."""
        with pytest.raises(ValidationError):
            TeamOffenseCreate(season=2023, tm="")

    def test_percentage_range(self):
        """Test percentage fields are in valid range."""
        with pytest.raises(ValidationError):
            TeamOffenseCreate(season=2023, tm="KAN", sc_pct=Decimal("150.0"))


class TestTeamDefenseDTO:
    """Tests for TeamDefense DTO validation."""

    def test_valid_create(self):
        """Test creating a valid TeamDefenseCreate DTO."""
        dto = TeamDefenseCreate(
            season=2023,
            tm="KAN",
            g=17,
            pa=250,
            yds=5000
        )
        assert dto.season == 2023
        assert dto.tm == "KAN"

    def test_negative_stats_rejected(self):
        """Test that negative defensive stats are rejected."""
        with pytest.raises(ValidationError):
            TeamDefenseCreate(season=2023, tm="KAN", pa=-10)


class TestPassingStatsDTO:
    """Tests for PassingStats DTO validation."""

    def test_valid_create(self):
        """Test creating a valid PassingStatsCreate DTO."""
        dto = PassingStatsCreate(
            season=2023,
            player_name="Patrick Mahomes",
            tm="KAN",
            cmp=400,
            att=600,
            yds=5000,
            td=40
        )
        assert dto.player_name == "Patrick Mahomes"
        assert dto.cmp == 400

    def test_empty_player_name_rejected(self):
        """Test that empty player name is rejected."""
        with pytest.raises(ValidationError):
            PassingStatsCreate(season=2023, player_name="", tm="KAN")

    def test_percentage_validation(self):
        """Test completion percentage in valid range."""
        with pytest.raises(ValidationError):
            PassingStatsCreate(
                season=2023,
                player_name="Test Player",
                tm="KAN",
                cmp_pct=Decimal("150.0")
            )


class TestRushingStatsDTO:
    """Tests for RushingStats DTO validation."""

    def test_valid_create(self):
        """Test creating a valid RushingStatsCreate DTO."""
        dto = RushingStatsCreate(
            season=2023,
            player_name="Christian McCaffrey",
            tm="SFO",
            att=250,
            yds=1200,
            td=14
        )
        assert dto.player_name == "Christian McCaffrey"
        assert dto.yds == 1200

    def test_negative_attempts_rejected(self):
        """Test that negative attempts are rejected."""
        with pytest.raises(ValidationError):
            RushingStatsCreate(
                season=2023,
                player_name="Test Player",
                tm="SFO",
                att=-10
            )


class TestReceivingStatsDTO:
    """Tests for ReceivingStats DTO validation."""

    def test_valid_create(self):
        """Test creating a valid ReceivingStatsCreate DTO."""
        dto = ReceivingStatsCreate(
            season=2023,
            player_name="Tyreek Hill",
            tm="MIA",
            tgt=150,
            rec=120,
            yds=1700,
            td=13
        )
        assert dto.player_name == "Tyreek Hill"
        assert dto.rec == 120


class TestDefenseStatsDTO:
    """Tests for DefenseStats DTO validation."""

    def test_valid_create(self):
        """Test creating a valid DefenseStatsCreate DTO."""
        dto = DefenseStatsCreate(
            season=2023,
            player_name="T.J. Watt",
            tm="PIT",
            sk=Decimal("19.0"),
            comb=64,
            solo=48
        )
        assert dto.player_name == "T.J. Watt"
        assert dto.sk == Decimal("19.0")

    def test_negative_sacks_rejected(self):
        """Test that negative sacks are rejected."""
        with pytest.raises(ValidationError):
            DefenseStatsCreate(
                season=2023,
                player_name="Test Player",
                tm="PIT",
                sk=Decimal("-5.0")
            )


class TestKickingStatsDTO:
    """Tests for KickingStats DTO validation."""

    def test_valid_create(self):
        """Test creating a valid KickingStatsCreate DTO."""
        dto = KickingStatsCreate(
            season=2023,
            player_name="Justin Tucker",
            tm="BAL",
            fga=35,
            fgm=32,
            fg_pct=Decimal("91.4")
        )
        assert dto.player_name == "Justin Tucker"
        assert dto.fgm == 32

    def test_percentage_validation(self):
        """Test FG percentage in valid range."""
        with pytest.raises(ValidationError):
            KickingStatsCreate(
                season=2023,
                player_name="Test Kicker",
                tm="BAL",
                fg_pct=Decimal("150.0")
            )


class TestPuntingStatsDTO:
    """Tests for PuntingStats DTO validation."""

    def test_valid_create(self):
        """Test creating a valid PuntingStatsCreate DTO."""
        dto = PuntingStatsCreate(
            season=2023,
            player_name="Johnny Hekker",
            tm="CAR",
            pnt=75,
            yds=3500,
            ypp=Decimal("46.7")
        )
        assert dto.player_name == "Johnny Hekker"
        assert dto.pnt == 75


class TestReturnStatsDTO:
    """Tests for ReturnStats DTO validation."""

    def test_valid_create(self):
        """Test creating a valid ReturnStatsCreate DTO."""
        dto = ReturnStatsCreate(
            season=2023,
            player_name="Devin Duvernay",
            tm="BAL",
            pr=25,
            pr_yds=250,
            kr=30,
            kr_yds=750
        )
        assert dto.player_name == "Devin Duvernay"
        assert dto.pr_yds == 250


class TestScoringStatsDTO:
    """Tests for ScoringStats DTO validation."""

    def test_valid_create(self):
        """Test creating a valid ScoringStatsCreate DTO."""
        dto = ScoringStatsCreate(
            season=2023,
            player_name="Austin Ekeler",
            tm="LAC",
            rush_td=12,
            rec_td=6,
            all_td=18,
            pts=108
        )
        assert dto.player_name == "Austin Ekeler"
        assert dto.all_td == 18

    def test_negative_touchdowns_rejected(self):
        """Test that negative touchdowns are rejected."""
        with pytest.raises(ValidationError):
            ScoringStatsCreate(
                season=2023,
                player_name="Test Player",
                tm="LAC",
                rush_td=-5
            )


class TestStandingsDTO:
    """Tests for Standings DTO validation."""

    def test_valid_create(self):
        """Test creating a valid StandingsCreate DTO."""
        dto = StandingsCreate(
            season=2023,
            tm="KAN",
            w=14,
            l=3,
            t=0,
            win_pct=Decimal("0.824"),
            pf=450,
            pa=320
        )
        assert dto.tm == "KAN"
        assert dto.w == 14

    def test_win_percentage_range(self):
        """Test win percentage must be between 0-1."""
        with pytest.raises(ValidationError):
            StandingsCreate(
                season=2023,
                tm="KAN",
                win_pct=Decimal("1.5")
            )

    def test_negative_wins_rejected(self):
        """Test that negative wins are rejected."""
        with pytest.raises(ValidationError):
            StandingsCreate(season=2023, tm="KAN", w=-1)


class TestGamesDTO:
    """Tests for Games DTO validation."""

    def test_valid_create(self):
        """Test creating a valid GamesCreate DTO."""
        dto = GamesCreate(
            season=2023,
            week=1,
            game_day="Sunday",
            game_date=date(2023, 9, 10),
            winner="KAN",
            loser="DET",
            pts_w=27,
            pts_l=20
        )
        assert dto.week == 1
        assert dto.winner == "KAN"
        assert dto.pts_w == 27

    def test_negative_points_rejected(self):
        """Test that negative points are rejected."""
        with pytest.raises(ValidationError):
            GamesCreate(season=2023, week=1, pts_w=-10)

    def test_season_range(self):
        """Test season must be in valid range."""
        with pytest.raises(ValidationError):
            GamesCreate(season=1800, week=1)


class TestDTOResponse:
    """Tests for Response DTOs."""

    def test_team_offense_response(self):
        """Test TeamOffenseResponse includes ID."""
        dto = TeamOffenseResponse(
            id=1,
            season=2023,
            tm="KAN",
            pf=450
        )
        assert dto.id == 1
        assert dto.season == 2023

    def test_passing_stats_response(self):
        """Test PassingStatsResponse includes ID."""
        dto = PassingStatsResponse(
            id=1,
            season=2023,
            player_name="Patrick Mahomes",
            tm="KAN"
        )
        assert dto.id == 1
        assert dto.player_name == "Patrick Mahomes"

from enum import Enum

from fastapi import FastAPI, HTTPException

from src.services import (
    scrape_service,
    team_offense_service,
    team_defense_service,
    standings_service,
    games_service,
    kicking_team_service,
    punting_team_service,
    returns_team_service,
    passing_stats_service,
    rushing_stats_service,
    receiving_stats_service,
    defense_stats_service,
    kicking_stats_service,
    punting_stats_service,
    return_stats_service,
    scoring_stats_service,
)

app = FastAPI()


class StatType(str, Enum):
    team_offense = "team_offense"
    team_defense = "team_defense"
    standings = "standings"
    games = "games"
    kicking = "kicking"
    punting = "punting"
    returns = "returns"
    passing_stats = "passing_stats"
    rushing_stats = "rushing_stats"
    receiving_stats = "receiving_stats"
    defense_stats = "defense_stats"
    kicking_stats = "kicking_stats"
    punting_stats = "punting_stats"
    return_stats = "return_stats"
    scoring_stats = "scoring_stats"


SCRAPE_DISPATCH = {
    StatType.team_offense: team_offense_service.scrape_and_store_team_offense,
    StatType.team_defense: team_defense_service.scrape_and_store,
    StatType.standings: standings_service.scrape_and_store,
    StatType.games: games_service.scrape_and_store,
    StatType.kicking: kicking_team_service.scrape_and_store,
    StatType.punting: punting_team_service.scrape_and_store,
    StatType.returns: returns_team_service.scrape_and_store,
    StatType.passing_stats: passing_stats_service.scrape_and_store,
    StatType.rushing_stats: rushing_stats_service.scrape_and_store,
    StatType.receiving_stats: receiving_stats_service.scrape_and_store,
    StatType.defense_stats: defense_stats_service.scrape_and_store,
    StatType.kicking_stats: kicking_stats_service.scrape_and_store,
    StatType.punting_stats: punting_stats_service.scrape_and_store,
    StatType.return_stats: return_stats_service.scrape_and_store,
    StatType.scoring_stats: scoring_stats_service.scrape_and_store,
}


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/scrape/team-gamelog/{team}/{year}")
async def scrape_team_gamelog(team: str, year: int):
    """
    Scrape team gamelog data for a specific team and year.

    Args:
        team: The team abbreviation to scrape data for.
        year: The season year to scrape data for.

    Returns:
        dict: A dictionary containing the scraping result.
    """
    data = await scrape_service.scrape_and_store(team, year)
    return data


@app.get("/scrape/{stat_type}/{season}")
async def scrape_stat(stat_type: StatType, season: int):
    """
    Scrape and store NFL stats from Pro-Football-Reference.

    Args:
        stat_type: Type of stat to scrape (see StatType enum for valid values).
        season: The NFL season year.

    Returns:
        List of saved records.
    """
    scrape_fn = SCRAPE_DISPATCH.get(stat_type)
    if scrape_fn is None:
        raise HTTPException(status_code=400, detail=f"Unknown stat type: {stat_type}")
    data = await scrape_fn(season)
    return data

from fastapi import APIRouter

from src.services import (
    team_offense_service,
    team_defense_service,
    standings_service,
    kicking_team_service,
    punting_team_service,
    returns_team_service,
)

router = APIRouter(prefix="/scrape/team", tags=["team-stats"])


@router.post("/offense/{season}")
async def scrape_team_offense(season: int):
    return await team_offense_service.scrape_and_store(season)


@router.post("/defense/{season}")
async def scrape_team_defense(season: int):
    return await team_defense_service.scrape_and_store(season)


@router.post("/standings/{season}")
async def scrape_standings(season: int):
    return await standings_service.scrape_and_store(season)


@router.post("/kicking/{season}")
async def scrape_team_kicking(season: int):
    return await kicking_team_service.scrape_and_store(season)


@router.post("/punting/{season}")
async def scrape_team_punting(season: int):
    return await punting_team_service.scrape_and_store(season)


@router.post("/returns/{season}")
async def scrape_team_returns(season: int):
    return await returns_team_service.scrape_and_store(season)

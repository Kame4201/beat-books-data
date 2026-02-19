from fastapi import APIRouter

from src.services import games_service, team_game_service

router = APIRouter(prefix="/scrape/games", tags=["games"])


@router.post("/{season}")
async def scrape_games(season: int):
    return await games_service.scrape_and_store(season)


@router.post("/{team}/{season}")
async def scrape_team_gamelog(team: str, season: int):
    return await team_game_service.scrape_and_store(team, season)

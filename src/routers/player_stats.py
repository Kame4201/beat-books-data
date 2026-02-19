from fastapi import APIRouter

from src.services import (
    passing_stats_service,
    rushing_stats_service,
    receiving_stats_service,
    defense_stats_service,
    kicking_stats_service,
    punting_stats_service,
    return_stats_service,
    scoring_stats_service,
)

router = APIRouter(prefix="/scrape/player", tags=["player-stats"])


@router.post("/passing/{season}")
async def scrape_passing_stats(season: int):
    return await passing_stats_service.scrape_and_store(season)


@router.post("/rushing/{season}")
async def scrape_rushing_stats(season: int):
    return await rushing_stats_service.scrape_and_store(season)


@router.post("/receiving/{season}")
async def scrape_receiving_stats(season: int):
    return await receiving_stats_service.scrape_and_store(season)


@router.post("/defense/{season}")
async def scrape_defense_stats(season: int):
    return await defense_stats_service.scrape_and_store(season)


@router.post("/kicking/{season}")
async def scrape_kicking_stats(season: int):
    return await kicking_stats_service.scrape_and_store(season)


@router.post("/punting/{season}")
async def scrape_punting_stats(season: int):
    return await punting_stats_service.scrape_and_store(season)


@router.post("/returns/{season}")
async def scrape_return_stats(season: int):
    return await return_stats_service.scrape_and_store(season)


@router.post("/scoring/{season}")
async def scrape_scoring_stats(season: int):
    return await scoring_stats_service.scrape_and_store(season)

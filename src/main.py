import logging
import uuid
from enum import StrEnum

from fastapi import Depends, FastAPI, HTTPException, Request, Security
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import ValidationError
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.database import get_db
from src.services import (
    defense_stats_service,
    games_service,
    kicking_stats_service,
    kicking_team_service,
    passing_stats_service,
    punting_stats_service,
    punting_team_service,
    receiving_stats_service,
    return_stats_service,
    returns_team_service,
    rushing_stats_service,
    scoring_stats_service,
    scrape_service,
    standings_service,
    team_defense_service,
    team_offense_service,
)
from src.services.stats_retrieval_service import StatsRetrievalService

logger = logging.getLogger(__name__)

app = FastAPI(title="beat-books-data", version="0.1.0")

# ---------------------------------------------------------------------------
# Middleware: request-id injection
# ---------------------------------------------------------------------------


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# ---------------------------------------------------------------------------
# Global exception handlers  (#53)
# ---------------------------------------------------------------------------


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Request validation failed",
            "detail": exc.errors(),
            "request_id": _request_id(request),
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "message": str(exc.detail),
            "detail": None,
            "request_id": _request_id(request),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception", extra={"request_id": _request_id(request)})
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "An unexpected error occurred",
            "detail": str(exc) if settings.DEBUG else None,
            "request_id": _request_id(request),
        },
    )


# ---------------------------------------------------------------------------
# Auth dependency  (#49)
# ---------------------------------------------------------------------------

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    api_key: str | None = Security(api_key_header),
):
    """Require X-API-Key header when API_KEY is configured."""
    if not settings.API_KEY:
        return  # auth disabled
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")


# ---------------------------------------------------------------------------
# Public endpoints (no auth)
# ---------------------------------------------------------------------------


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "beat-books-data", "version": "0.1.0"}


@app.get("/")
async def read_root():
    return {"Hello": "World"}


# ---------------------------------------------------------------------------
# Scrape endpoints (auth-protected)  (#49 auth, #38 DI, #51 async)
# ---------------------------------------------------------------------------


class StatType(StrEnum):
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


@app.get("/scrape/team-gamelog/{team}/{year}")
async def scrape_team_gamelog(
    team: str,
    year: int,
    db: Session = Depends(get_db),
    _: None = Depends(verify_api_key),
):
    data = await scrape_service.scrape_and_store(team, year, db=db)
    return data


@app.get("/scrape/{stat_type}/{season}")
async def scrape_stat(
    stat_type: StatType,
    season: int,
    db: Session = Depends(get_db),
    _: None = Depends(verify_api_key),
):
    scrape_fn = SCRAPE_DISPATCH.get(stat_type)
    if scrape_fn is None:
        raise HTTPException(status_code=400, detail=f"Unknown stat type: {stat_type}")
    data = await scrape_fn(season, db=db)
    return data


# ---------------------------------------------------------------------------
# Data-retrieval endpoints  (#50)
# ---------------------------------------------------------------------------


@app.get("/api/v1/stats/teams/{season}")
async def get_teams(
    season: int,
    offset: int = 0,
    limit: int = 50,
    sort_by: str = "pf",
    order: str = "desc",
    db: Session = Depends(get_db),
):
    svc = StatsRetrievalService(db)
    return svc.get_all_teams(
        season, offset=offset, limit=limit, sort_by=sort_by, order=order
    )


@app.get("/api/v1/stats/teams/{season}/{team}")
async def get_team_stats(
    season: int,
    team: str,
    db: Session = Depends(get_db),
):
    svc = StatsRetrievalService(db)
    result = svc.get_team_stats(team, season)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No stats for {team} in {season}")
    return result


@app.get("/api/v1/stats/players/{season}")
async def get_player_stats(
    season: int,
    name: str,
    db: Session = Depends(get_db),
):
    svc = StatsRetrievalService(db)
    return svc.get_player_stats(name, season)


@app.get("/api/v1/standings/{season}")
async def get_standings(
    season: int,
    offset: int = 0,
    limit: int = 50,
    sort_by: str = "win_pct",
    order: str = "desc",
    db: Session = Depends(get_db),
):
    svc = StatsRetrievalService(db)
    return svc.get_standings(
        season, offset=offset, limit=limit, sort_by=sort_by, order=order
    )


@app.get("/api/v1/games/{season}")
async def get_games(
    season: int,
    week: int | None = None,
    offset: int = 0,
    limit: int = 50,
    sort_by: str = "week",
    order: str = "asc",
    db: Session = Depends(get_db),
):
    svc = StatsRetrievalService(db)
    return svc.get_games(
        season, week=week, offset=offset, limit=limit, sort_by=sort_by, order=order
    )


@app.get("/api/v1/players/search")
async def search_players(
    name: str,
    season: int | None = None,
    offset: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    svc = StatsRetrievalService(db)
    return svc.search_players(name, season=season, offset=offset, limit=limit)

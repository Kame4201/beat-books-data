# CLAUDE.md — beat-books-data

## Project Overview
NFL data ingestion, storage, and retrieval service. Part of the BeatTheBooks platform.
This repo is the data backbone — it scrapes NFL stats, owns the database schema, and serves data to other services.

## Architecture
3-tier separation: Service → Repository → Database (PostgreSQL on Neon.tech)
- **Services** (`src/services/`): Business logic. NEVER contain raw SQL.
- **Repositories** (`src/repositories/`): Data access layer. ALL SQL lives here.
- **Entities** (`src/entities/`): SQLAlchemy ORM models. Single source of truth for schema.
- **DTOs** (`src/dtos/`): Pydantic validation models for input/output.

## This Repo OWNS
- ALL database schema and Alembic migrations — other repos have READ-ONLY DB access
- ALL SQLAlchemy entities (single source of truth)
- ALL data scraping logic (Selenium + BeautifulSoup, with optional Scrapling backend)
- ALL data retrieval queries

## Directory Structure
```
src/
├── core/          # Database connection, centralized config
├── entities/      # SQLAlchemy ORM models (14+ tables)
├── dtos/          # Pydantic validation models
├── repositories/  # Data access layer (ALL SQL here)
├── services/      # Business logic (NO SQL here)
└── main.py        # FastAPI application
migrations/        # Alembic database migrations
tests/             # Unit, integration, E2E tests
```

## Rules — ALWAYS Follow
- NEVER put SQL in services — use repositories
- NEVER put business logic in repositories — use services
- ALWAYS create DTOs for input validation before storing data
- ALWAYS create Alembic migrations for schema changes (never raw ALTER TABLE)
- ALWAYS follow rate limiting for scrapers (configurable via SCRAPE_DELAY_SECONDS)
- EVERY entity should have a corresponding DTO

## Rules — NEVER Do
- Never modify the database schema outside of Alembic migrations
- Never hardcode database URLs — use config.py / environment variables
- Never skip DTO validation when accepting external data
- Never import from beat-books-model or beat-books-api

## Common Commands

```bash
# Setup (first time or after dependency changes)
uv sync

# Run the data service
uv run uvicorn src.main:app --reload --port 8001

# Database migrations (Alembic)
uv run alembic upgrade head                                    # Apply all pending migrations
uv run alembic revision --autogenerate -m "description"        # Create new migration (auto-detect changes)
uv run alembic revision -m "description"                       # Create empty migration (manual)
uv run alembic downgrade -1                                    # Roll back one migration
uv run alembic current                                         # Show current revision
uv run alembic history                                         # Show migration history

# Testing
uv run pytest
uv run pytest --cov=src --cov-report=html
uv run pytest -m unit        # Only unit tests
uv run pytest -m integration # Only integration tests

# Linting & Type Checking
uv run ruff check src tests    # Run linter
uv run ruff format src tests   # Format code
uv run mypy src                # Type check
```

## Database
- PostgreSQL hosted on Neon.tech
- Connection via DATABASE_URL environment variable
- Schema managed via Alembic migrations (see `migrations/` directory)
- 14+ tables: team_offense, team_defense, passing_stats, rushing_stats, receiving_stats, defense_stats, kicking_stats, punting_stats, return_stats, scoring_stats, games, standings, returns, kicking, punting
- Tables.sql kept as reference only — DO NOT use for deployments

## Scrape Backend
- `SCRAPE_BACKEND` env var selects the fetch backend: `selenium` (default) or `scrapling`
- Selenium is always the default — omitting the var preserves existing behavior
- `scrape_service.py` (team gamelog) requires Selenium (JS interaction) — do NOT migrate it to Scrapling
- Backend selection lives in `src/core/scraper_utils.py:fetch_page()`, fetcher impl in `src/core/scrapling_fetcher.py`
- Rollback: set `SCRAPE_BACKEND=selenium` or remove the variable. No code change needed.

## Known Issues
- 403 errors from Pro-Football-Reference when URL contains hash fragments (e.g., #all_team_stats)
- SCRAPE_DELAY_SECONDS is hardcoded at 60s in some places — should use config.py
- Only 2 DTOs exist (team_game_dto, scraped_data_dto) — rest need to be created

## Related Repos
- beat-books-model: ML predictions (READ-ONLY DB access)
- beat-books-api: API gateway (routes to this service)
- beat-books-infra: CI/CD, docs, Docker

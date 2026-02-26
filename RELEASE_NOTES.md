# Release Notes — Dev → Main (PR #65)

## What Changed

### New Features
- **API Authentication** (#49): `X-API-Key` header auth via `verify_api_key` dependency. Disabled when `API_KEY` env var is empty.
- **6 Data Retrieval Endpoints** (#50): `/api/v1/stats/teams`, `/api/v1/standings`, `/api/v1/games`, `/api/v1/players/search`, `/api/v1/stats/players`
- **Structured Error Responses** (#53): Global exception handlers returning `{error, message, detail, request_id}` JSON. Request-ID middleware.
- **Injury Report & Weather Data** (#8): New entities, repos, services, DTOs, and Alembic migrations.
- **Batch Scraping with Job Tracking** (#9): `batch_scrape_service.py` with `scrape_job` entity.

### Architecture Improvements
- **Dependency Injection** (#38): All services accept optional `db: Session`; FastAPI `Depends(get_db)` for request-scoped sessions.
- **Async Thread Pooling** (#51): All 15 scraping services use `asyncio.to_thread()`.
- **BaseRepository Pattern** (#55): `TeamGameRepository` standardized to `BaseRepository[T]`.
- **Hardcoded Delays Consolidated** (#56): Selenium setup and delays moved to `config.py`.
- **uv Migration** (#58): `pyproject.toml` + `uv.lock` for dependency management.

### Test Coverage
- **221 total tests** (up from ~97), 70.44% code coverage (CI threshold: 30%).
- Fixed broken fixtures and incorrect mock targets (#64).

### Bug Fixes Applied During QA
- `pytest-asyncio` added to `pyproject.toml` dev deps (was missing — only in `requirements.txt`).
- `asyncio_mode = "auto"` added to `[tool.pytest.ini_options]` — fixes 12 async test failures.
- 921 ruff lint violations fixed (auto-fix + manual E501/UP042 fixes).
- `ruff format` applied to 27 files.

### Database Migrations Included
- `003_create_injury_reports_table.py`
- `004_create_game_weather_table.py`
- `005_create_scrape_jobs.py`

### Merged PRs
| PR | Title |
|----|-------|
| #55 | refactor: standardize TeamGameRepository to BaseRepository pattern |
| #56 | fix: consolidate hardcoded delays and Selenium setup into config |
| #54 | fix: conftest CI DATABASE_URL |
| #58 | chore: migrate to uv |
| #31 | fix: cross-cutting improvements (logging, test infra, DEVELOPMENT.md) |
| #17 | feat: add injury report and weather data sources |
| #18 | feat: add batch scraping with job tracking |
| #60 | feat: implement DI, auth, error handling, retrieval endpoints, async fix |
| #63 | fix: address PR #31 review comments (docs pip→uv) |
| #64 | fix: repair broken test fixtures and mock targets |

### Closed Issues
#4, #8, #9, #37, #38, #49, #50, #51, #53

---

## Test Plan

### Prerequisites
```bash
git checkout Dev
uv sync --all-extras
cp .env.example .env   # Set DATABASE_URL
```

### 1. Full CI Validation
```bash
# Lint (must pass with 0 errors)
uv run ruff check src/
uv run ruff format --check src/

# Type check (55 errors — pre-existing DI pattern, tracked for follow-up)
uv run mypy src/ --ignore-missing-imports

# Security scan
uv run bandit -r src/ -ll

# Tests + coverage
uv run pytest -m "not integration" --cov=src --cov-report=term --cov-fail-under=30
# Expected: 221 passed, 70%+ coverage
```

### 2. Test Individual Features

**Auth (#49):**
```bash
uv run pytest tests/test_api.py::TestAuth -v
```

**Retrieval endpoints (#50):**
```bash
uv run pytest tests/test_api.py::TestRetrievalEndpoints -v
```

**Error handling (#53):**
```bash
uv run pytest tests/test_api.py::TestErrorHandling -v
```

**Async thread pooling (#51):**
```bash
uv run pytest tests/test_api.py::TestAsyncThreadPool -v
```

**Dependency injection (#38):**
```bash
uv run pytest tests/test_api.py::TestDependencyInjection -v
```

**Batch scraping (#9):**
```bash
uv run pytest tests/test_batch_scrape_service.py -v
```

**Injury reports & weather (#8):**
```bash
uv run pytest tests/test_injury_report.py tests/test_game_weather.py -v
```

**Repository & service unit tests:**
```bash
uv run pytest tests/test_unit/ -v
```

### 3. Test Scrape → Store

**Option A — Full scrape via API (requires Chrome/Selenium on host):**
```bash
uv run uvicorn src.main:app --port 8001

# Scrape one stat type
curl http://localhost:8001/scrape/team_offense/2024
# Expected: {"status": "success", "records": 32}

# Verify stored data
curl http://localhost:8001/api/v1/stats/teams/2024
# Expected: {"data": [...32 teams...], "total": 32}
```

**Option B — Store path only (no Selenium needed):**
```python
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from src.entities.team_offense import TeamOffense
from src.repositories.team_offense_repo import TeamOffenseRepository

engine = create_engine("postgresql://...")  # your DATABASE_URL
session = Session(engine)
repo = TeamOffenseRepository(session)

# Insert
test = TeamOffense(season=9999, tm="TST", g=1, pf=21, yds=350)
saved = repo.create(test, commit=True)
# Read back
found = repo.find_by_season(9999)
assert len(found) == 1 and found[0].tm == "TST"
# API readback: curl http://localhost:8001/api/v1/stats/teams/9999
# Clean up
session.execute(text("DELETE FROM team_offense WHERE season = 9999"))
session.commit()
```

**Option C — Unit tests (mocked, no DB/Selenium):**
```bash
uv run pytest tests/test_unit/test_services/test_team_offense_service.py -v
uv run pytest tests/test_unit/test_services/test_scrape_service.py -v
```

### 4. Smoke Test (Local Server)
```bash
uv run uvicorn src.main:app --port 8001
curl http://localhost:8001/health
# Expected: {"status":"healthy","service":"beat-books-data","version":"0.1.0"}

curl http://localhost:8001/api/v1/stats/teams/2024
curl http://localhost:8001/api/v1/standings/2024
```

### 5. Alembic Migrations
```bash
uv run alembic upgrade head
uv run alembic current
# Expected: head at revision 005
```

### 6. End-to-End with API + Model via Infra Compose
```bash
# From beat-books-infra repo:
docker compose up -d

# Verify services:
curl http://localhost:8001/health   # beat-books-data
curl http://localhost:8000/health   # beat-books-api

# Scrape data:
curl http://localhost:8001/scrape/team_offense/2024

# Verify via API gateway:
curl http://localhost:8000/api/v1/stats/teams/2024

# (If model service wired) Request prediction:
curl http://localhost:8000/api/v1/predictions/2024/week/1
```

---

## Known Issues / Follow-Up Items

1. **mypy: 55 type errors** — All `Session | None` passed where `Session` expected in DI pattern. Functional but needs type narrowing.
2. **`BaseRepository.delete(id)`** calls `session.delete(id)` with int instead of fetching entity first — raises `UnmappedInstanceError`.
3. **`GET /api/v1/games/{season}`** returns 500 — query or serialization bug in `StatsRetrievalService.get_games()`.
4. **Batch scraping has no HTTP endpoint** — `BatchScrapeService` exists but is not route-exposed.
5. **No Chrome in CI/Docker** — Selenium scraping untestable in headless CI. Consider scrapling-only integration test.
6. **Missing DTOs** — Most entities lack corresponding DTOs (tracked in CLAUDE.md).
7. **New migrations (003-005)** need `uv run alembic upgrade head` on target DB before deployment.

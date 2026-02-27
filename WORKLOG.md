# WORKLOG — beat-books-data: Scrape→Store Production Readiness

## PRs Created (all target Dev)

| PR | Title | Status | Tests |
|----|-------|--------|-------|
| #67 | feat: use scrapling backend for scraping (no selenium) | Open | 3 pass |
| #68 | fix: /api/v1/games returns 200 + regression test | Open | 5 pass |
| #69 | feat: add batch scrape HTTP endpoint | Open | 4 pass |
| #70 | fix: repair alembic env + ensure upgrade head works | Open | alembic upgrade head ✅ |
| #71 | chore: mypy cleanup for DI typing (55 errors) | Issue filed | Not gating CI |

## Issues Created

| # | Title | Reason |
|---|-------|--------|
| #71 | chore: mypy cleanup for DI typing (55 errors) | mypy not a merge gate (only `lint` + `test` required) |

## What Was Done

### GAP 1: Scrapling Backend (PR #67)
- Added `SCRAPE_BACKEND`, `SCRAPLING_FETCHER_TYPE`, `SCRAPLING_TIMEOUT`, `SCRAPLING_IMPERSONATE` to `config.py`
- Default changed from `selenium` to `scrapling`
- Added `scrapling` to `pyproject.toml` dependencies
- Updated `.env.example`
- 3 unit tests for backend selection

### GAP 2: Games Endpoint 500 (PR #68)
- **Root cause**: `StatsRetrievalService.get_games()` used `TeamGameRepository` (queries `team_games` table) instead of `GamesRepository` (queries `games` table where data lives)
- Fixed to use `GamesRepository`
- Added week filter to `GamesRepository.find_by_season()` and `count_by_season()`
- 5 regression tests

### GAP 3: Batch Scrape Route (PR #69)
- Added `POST /scrape/batch/{season}` endpoint
- Body: `{"stats": ["team_offense", ...], "dry_run": false}`
- Dispatches to existing `SCRAPE_DISPATCH` map sequentially
- Auth-protected, continues on errors, defaults to all 15 stat types
- 4 unit tests

### GAP 4: Migrations Reliability (PR #70)
- Removed merge conflict markers from `migrations/env.py`
- Added missing entity imports: `InjuryReport`, `GameWeather`, `Odds`, `ScrapeJob`
- Fixed revision chain: `001_initial_schema → 002_performance_indexes → 002 → 003 → 004 → 005`
- Verified `alembic upgrade head` applies all 6 migrations on fresh DB

### GAP 5: Mypy (Issue #71)
- mypy is NOT a merge gate (branch protection requires only `lint` + `test`)
- Filed issue #71 with suggested fixes
- 55 errors, all `Session | None` type narrowing in DI pattern

## E2E Test Snippet

After merging all PRs to Dev:

```bash
# 1) Setup
git checkout Dev
uv sync --all-extras
cp .env.example .env  # Set DATABASE_URL

# 2) Apply migrations
uv run alembic upgrade head
uv run alembic current   # → 005 (head)

# 3) Start server
uv run uvicorn src.main:app --port 8001 &

# 4) Batch scrape (dry run first)
curl -X POST http://localhost:8001/scrape/batch/2024 \
  -H 'Content-Type: application/json' \
  -d '{"stats": ["team_offense", "standings"], "dry_run": true}'
# Expected: {"season": 2024, "results": [{"stat": "team_offense", "status": "skipped (dry_run)"}, ...]}

# 5) Real scrape (requires SCRAPE_BACKEND=scrapling in .env)
curl -X POST http://localhost:8001/scrape/batch/2024 \
  -H 'Content-Type: application/json' \
  -d '{"stats": ["team_offense", "standings", "games"]}'
# Expected: {"season": 2024, "results": [{"stat": "...", "status": "success"}, ...]}

# 6) Verify stored data
curl http://localhost:8001/api/v1/stats/teams/2024
# Expected: {"data": [...], "total": 32}

curl http://localhost:8001/api/v1/games/2024
# Expected: {"data": [...], "total": N}

curl http://localhost:8001/api/v1/standings/2024
# Expected: {"data": [...], "total": 32}

# 7) Run tests
uv run pytest -m "not integration" -q
# Expected: 233+ passed
```

## Full Test Suite Result
- **224 passed** on feat/scrapling-default branch (221 original + 3 new)
- Games endpoint: 5 new regression tests
- Batch scrape: 4 new tests
- Total after all PRs merged: ~233 tests

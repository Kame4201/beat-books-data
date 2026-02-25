# beat-books-data

NFL data ingestion, storage, and retrieval service for the BeatTheBooks platform.

## What This Does

- **Scrapes** NFL statistics from Pro-Football-Reference (Selenium + BeautifulSoup)
- **Stores** data in PostgreSQL (Neon.tech) via SQLAlchemy
- **Serves** data retrieval API for other BeatTheBooks services
- **Owns** the database schema and all migrations

## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy + Alembic
- PostgreSQL (Neon.tech)
- Selenium + BeautifulSoup + Pandas

## Quick Start

This project uses [uv](https://docs.astral.sh/uv/) for fast, reliable dependency management.

### Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Setup Project

```bash
# Clone and enter the project
git clone https://github.com/Kame4201/beat-books-data.git
cd beat-books-data

# Sync dependencies (creates venv automatically)
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL

# Run the service
uv run uvicorn src.main:app --reload --port 8001
```

### Development

```bash
# Install dev dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=html

# Run type checking
uv run mypy src

# Run linting
uv run ruff check src tests
```

## Why uv?

- **Fast**: 10-100x faster than pip for dependency resolution
- **Reproducible**: Lock file ensures consistent environments
- **Simple**: One command (`uv sync`) sets up everything
- **Modern**: Built-in support for Python version management

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/scrape/{team}/{year}` | Scrape single team stats |
| GET | `/scrape/{year}` | Scrape team offense stats |
| POST | `/scrape/excel` | Batch scrape from Excel URLs |

## Database

14+ tables covering team and player statistics, games, and standings. See `Tables.sql` for the full schema.

## Related Repos

- [beat-books-model](https://github.com/Kame4201/beat-books-model) — ML predictions & strategy
- [beat-books-api](https://github.com/Kame4201/beat-books-api) — API gateway
- [beat-books-infra](https://github.com/Kame4201/beat-books-infra) — CI/CD, docs, Docker

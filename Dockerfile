FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck, chromium deps for selenium, and uv
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Sync dependencies (production only, no dev extras)
RUN uv sync --frozen --no-dev

# Copy the rest of the application
COPY . .

EXPOSE 8001

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]

# Multi-Environment Migration Guide

This guide covers how to set up and manage Alembic database migrations across Dev, Stage, and Main (production) environments.

## Architecture

**One migration chain, different databases.** The same migration files run against every environment — the only thing that changes is the `DATABASE_URL` connection string.

| Environment | Purpose | Neon Account | Migrations |
|-------------|---------|-------------|------------|
| Local | Developer workstation | Personal Neon branch or Dev | Manual |
| Dev | Shared development, scrapers | Friend's Neon account | Auto on merge to `Dev` branch |
| Stage | Pre-production validation | Your Neon account | Manual |
| Main | Production, ML models read here | Your Neon account | Manual (requires safety override) |

## Initial Setup

### 1. Baseline the Dev Database

Dev already has tables but Alembic doesn't know about them yet. **Stamp** tells Alembic "this DB is already at this revision" without running any SQL.

```powershell
# PowerShell (Windows)
$env:DATABASE_URL = "postgresql://...your-dev-connection-string..."
$env:ENV = "dev"
alembic stamp 002_performance_indexes
```

Verify:
```powershell
alembic current
# Should output: 002_performance_indexes (head)
```

### 2. Create Stage and Main Databases (When Ready)

1. Create a Neon account/project
2. Create two databases (or two projects) for Stage and Main
3. Copy the connection strings from the Neon dashboard

### 3. Bootstrap Stage and Main

These are fresh databases — run the full migration chain to create all tables from scratch:

```powershell
# Stage
$env:DATABASE_URL = "postgresql://...your-stage-connection-string..."
$env:ENV = "stage"
alembic upgrade head

# Main (requires safety override)
$env:DATABASE_URL = "postgresql://...your-main-connection-string..."
$env:ENV = "main"
$env:ALLOW_PRODUCTION_MIGRATE = "true"
alembic upgrade head
```

### 4. Add GitHub Secrets

In your repo: Settings > Secrets and variables > Actions, add:

- `DATABASE_URL_DEV` — Dev connection string
- `DATABASE_URL_STAGE` — Stage connection string
- `DATABASE_URL_MAIN` — Main connection string

## Developer Workflow

### Creating a New Migration

```powershell
# 1. Make changes to entity files in src/entities/
#    Example: add a column to standings.py

# 2. Auto-generate the migration
alembic revision --autogenerate -m "add win_streak to standings"

# 3. ALWAYS review the generated file in migrations/versions/
#    Alembic autogenerate is imperfect — check upgrade() and downgrade()

# 4. Test the migration
alembic upgrade head

# 5. Test the rollback
alembic downgrade -1

# 6. Re-apply
alembic upgrade head

# 7. Commit BOTH the entity change and migration file
git add src/entities/standings.py migrations/versions/xxx_add_win_streak_to_standings.py
git commit -m "feat: add win_streak to standings"
```

### Promoting Schema Changes

```
feature branch
    |
    | PR to Dev (code review)
    v
Dev branch ── merge triggers auto-migration on Dev DB
    |
    | PR from Dev → stage (code review)
    v
stage branch ── developer manually runs: alembic upgrade head (against Stage DB)
    |
    | PR from stage → main (requires approval)
    v
main branch ── developer manually runs: alembic upgrade head (against Main DB, needs ALLOW_PRODUCTION_MIGRATE=true)
```

**Step by step:**

1. **Develop** — Work on a feature branch, create migration, push
2. **PR to Dev** — CI runs tests. On merge, Dev DB auto-migrates
3. **PR from Dev to Stage** — After merge, manually migrate Stage:
   ```powershell
   $env:DATABASE_URL = "postgresql://...stage..."
   $env:ENV = "stage"
   alembic upgrade head
   ```
4. **PR from Stage to Main** — After merge and approval, manually migrate Main:
   ```powershell
   $env:DATABASE_URL = "postgresql://...main..."
   $env:ENV = "main"
   $env:ALLOW_PRODUCTION_MIGRATE = "true"
   alembic upgrade head
   ```

## Safety Guardrails

### Production Protection

Running `alembic upgrade head` against Main (`ENV=main`) without setting `ALLOW_PRODUCTION_MIGRATE=true` will raise an error:

```
RuntimeError: Refusing to migrate production database. Set ALLOW_PRODUCTION_MIGRATE=true to proceed.
```

This prevents accidental production migrations from a developer's terminal.

### Environment Banner

Every migration run logs which environment is being targeted:

```
=======================================
  ALEMBIC MIGRATION TARGET: DEV
=======================================
```

For Main, an extra warning is shown:
```
*** PRODUCTION DATABASE -- Proceed with caution ***
```

## Rollback Procedures

### Roll back one migration

```powershell
$env:DATABASE_URL = "postgresql://...target-db..."
alembic downgrade -1
```

### Roll back to a specific revision

```powershell
alembic history --verbose   # find the revision ID
alembic downgrade <revision_id>
```

### Production rollback (emergency)

```powershell
$env:DATABASE_URL = "postgresql://...main..."
$env:ENV = "main"
$env:ALLOW_PRODUCTION_MIGRATE = "true"
alembic downgrade -1
```

Preferred approach: create a new forward migration that reverses the change and promote it through the normal pipeline.

### If a migration fails mid-execution

PostgreSQL runs each migration in a transaction. If it fails:
- The transaction is rolled back automatically
- `alembic_version` still points to the previous revision
- Fix the migration file and re-run `alembic upgrade head`

## Quick Reference

| Command | What it does |
|---------|-------------|
| `alembic current` | Show current revision |
| `alembic history` | Show migration chain |
| `alembic upgrade head` | Apply all pending migrations |
| `alembic downgrade -1` | Roll back one migration |
| `alembic revision --autogenerate -m "msg"` | Create migration from entity changes |
| `alembic revision -m "msg"` | Create empty migration (manual SQL) |
| `alembic stamp <revision>` | Mark a revision as applied without running it |

## .env Configuration

```bash
# Point to the target database
DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require

# Set the environment (controls safety guardrails)
ENV=dev   # local | dev | stage | main

# Only needed for Main migrations
ALLOW_PRODUCTION_MIGRATE=true
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `DuplicateTable: relation "x" already exists` | Tables exist but Alembic doesn't know. Run `alembic stamp <revision>` |
| `Can't locate revision` | Check `alembic history` for chain breaks |
| `Refusing to migrate production database` | Set `$env:ALLOW_PRODUCTION_MIGRATE = "true"` (only for intentional Main migrations) |
| Migration works on Dev but fails on Stage | Check for data-dependent migrations or column type mismatches |
| `ImportError` in env.py | New entity added but not imported in `migrations/env.py` |

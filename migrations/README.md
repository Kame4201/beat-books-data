# Database Migrations

This directory contains Alembic database migrations for the beat-books-data service.

## Setup

Alembic is already configured. The configuration reads the `DATABASE_URL` from your environment or `.env` file.

## Common Commands

### Apply all pending migrations
```bash
alembic upgrade head
```

### Create a new migration (auto-generate from model changes)
```bash
alembic revision --autogenerate -m "description of changes"
```

### Create a blank migration
```bash
alembic revision -m "description of changes"
```

### Downgrade one migration
```bash
alembic downgrade -1
```

### View current migration version
```bash
alembic current
```

### View migration history
```bash
alembic history
```

## Migration Chain

Migrations must be applied in order. The chain is:

1. `001_initial_schema_from_tables_sql.py` -- Creates all NFL stats tables (team_offense, team_defense, returns, kicking, punting, passing_stats, rushing_stats, receiving_stats, defense_stats, kicking_stats, punting_stats, return_stats, scoring_stats, standings, games).
2. `001_add_performance_indexes.py` -- Adds performance indexes on frequently queried columns.

## Migration 002: Performance Indexes

The second migration (`001_add_performance_indexes.py`) adds recommended database indexes for common query patterns:

### Indexes Added

1. **passing_stats**
   - `idx_passing_stats_season`: Index on `season` column
   - `idx_passing_stats_player`: Index on `player_name` column
   - `idx_passing_stats_team`: Index on `tm` (team) column

2. **team_offense**
   - `idx_team_offense_season`: Index on `season` column

3. **rushing_stats**
   - `idx_rushing_stats_season`: Index on `season` column

4. **receiving_stats**
   - `idx_receiving_stats_season`: Index on `season` column

5. **games**
   - `idx_games_season_week`: Composite index on `(season, week)` columns

6. **standings**
   - `idx_standings_season`: Index on `season` column

### Benchmarking

To measure the performance impact of these indexes, you should benchmark queries before and after applying the migration.

#### Example Benchmarking Process

1. **Before applying migration**, run a test query and measure execution time:
```sql
EXPLAIN ANALYZE
SELECT * FROM passing_stats WHERE season = 2024;
```

2. **Apply the migration**:
```bash
alembic upgrade head
```

3. **After migration**, run the same query and compare:
```sql
EXPLAIN ANALYZE
SELECT * FROM passing_stats WHERE season = 2024;
```

#### What to Look For

- **Execution time**: Should be significantly reduced for filtered queries
- **Query plan**: Should show "Index Scan" instead of "Seq Scan" (sequential scan)
- **Rows scanned**: Should be closer to the actual result count

#### Suggested Queries for Benchmarking

```sql
-- Season filtering (should benefit from season indexes)
EXPLAIN ANALYZE SELECT * FROM passing_stats WHERE season = 2024;
EXPLAIN ANALYZE SELECT * FROM rushing_stats WHERE season = 2024;
EXPLAIN ANALYZE SELECT * FROM receiving_stats WHERE season = 2024;

-- Player lookup (should benefit from player_name index)
EXPLAIN ANALYZE SELECT * FROM passing_stats WHERE player_name = 'Patrick Mahomes';

-- Team filtering (should benefit from team index)
EXPLAIN ANALYZE SELECT * FROM passing_stats WHERE tm = 'Kansas City Chiefs';

-- Composite index for games
EXPLAIN ANALYZE SELECT * FROM games WHERE season = 2024 AND week = 1;

-- Standings by season
EXPLAIN ANALYZE SELECT * FROM standings WHERE season = 2024;
```

## Best Practices

1. **Always review auto-generated migrations** - Alembic's autogenerate is helpful but not perfect
2. **Test migrations on a copy of production data** before applying to production
3. **Never modify existing migrations** that have been applied - create a new migration instead
4. **Include descriptive comments** in migration files
5. **Keep migrations small and focused** - one logical change per migration
6. **Document any manual SQL** that can't be auto-generated

## Troubleshooting

### Migration fails to apply
- Check the database connection string in your `.env` file
- Ensure the database user has necessary permissions (CREATE INDEX, etc.)
- Review the migration file for syntax errors

### Autogenerate doesn't detect changes
- Make sure all entity models are imported in `migrations/env.py`
- Verify that entity models inherit from the correct `Base`
- Check that `__tablename__` matches the actual database table name

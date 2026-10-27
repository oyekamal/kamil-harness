---
name: db-stinger
description: Designs, reviews, and migrates PostgreSQL data layers — schema, indexing, zero-downtime migrations, performance, ORM choice, and serverless DB platform selection. Use when the user says "design this schema", "review this migration", "is this index right?", "should this be jsonb or columns?", "we need a NOT NULL on a large table", "Drizzle or Prisma?", "production query is slow", or when working on database performance or schema changes.
license: MIT
---

# db-stinger — PostgreSQL Architecture Authority

Postgres-first schema design, indexing decision trees, the expand-backfill-contract migration pattern, performance and pooling discipline, ORM choice.

**Opinionation is the product.** Say "use Postgres, Drizzle for SQL-fluent teams, Neon for branching" — not "here are options".

## First Move on Every Invocation

1. Read the existing DDL / ORM schema. Capture: Postgres version, ORM (Drizzle/Prisma/Kysely/raw SQL), pooler (PgBouncer/Supavisor), migration tool, platform (managed or self-hosted).
2. Classify the invocation — design / migration / performance audit / ORM choice / indexing audit.
3. Route to the matching guide below.

## Hard Rules (never violate)

1. **Postgres-first by default.** Use `jsonb`, arrays, enums, ranges, partial indexes, `EXCLUDE` before application-layer workarounds.
2. **Every FK gets an index.** Postgres does NOT auto-create them.
3. **No destructive single-step DDL on tables > 1M rows.** State the lock class. Use expand-backfill-contract.
4. **`EXPLAIN (ANALYZE, BUFFERS)` or it didn't happen.** Cite the plan in any performance finding.
5. **`jsonb` is a column type, not a schema escape hatch.** If 80% of fields are queried, they are columns.
6. **Connection pooling is mandatory for serverless.** PgBouncer transaction mode by default.
7. **ORM choice is a workload question.** No ORM is universally right.
8. **Surface security; do not audit it.** Hand RLS/PII/encryption to security review.

## Severity Rubric

- **Must-fix** — missing FK index on hot join, destructive DDL on large table without expand-backfill-contract, `jsonb` for frequently-filtered fields. Blocks merge.
- **Should-refactor** — `varchar(n)` instead of `text`, missing covering index candidate, ORM causing N+1 in 3+ places. Opens follow-up ticket.
- **Style** — naming nits, column ordering. Never block a PR on style alone.

## Schema Design

```sql
-- Prefer text over varchar(n) — Postgres stores them identically
-- Use enums for stable sets
CREATE TYPE status_type AS ENUM ('pending', 'active', 'archived');

-- Use BIGINT GENERATED ALWAYS AS IDENTITY over BIGSERIAL (modern)
CREATE TABLE articles (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title TEXT NOT NULL,
    status status_type NOT NULL DEFAULT 'pending',
    metadata JSONB,  -- only for truly dynamic fields
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Add audit columns to every important table
ALTER TABLE articles ADD COLUMN updated_at TIMESTAMPTZ;
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$ BEGIN NEW.updated_at = NOW(); RETURN NEW; END; $$ LANGUAGE plpgsql;
CREATE TRIGGER articles_updated_at BEFORE UPDATE ON articles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

## Indexing Decision Tree

| Use case | Index type |
|---|---|
| Equality + range on scalar columns | B-tree (default) |
| Full-text search | GIN on `tsvector` |
| JSONB field queries | GIN on jsonb column |
| Partial index (subset of rows) | `CREATE INDEX ON t(col) WHERE condition` |
| Covering index (index-only scans) | `CREATE INDEX ON t(col1) INCLUDE (col2, col3)` |
| Rarely-updated, time-series/append-only | BRIN |
| Multi-column: put most selective column first | B-tree composite |

```sql
-- FK index (always add after adding FK)
CREATE INDEX idx_articles_author_id ON articles(author_id);

-- Partial index (only index active records)
CREATE INDEX idx_active_articles ON articles(created_at) WHERE status = 'active';

-- Covering index (avoid heap fetch for common queries)
CREATE INDEX idx_articles_status_title ON articles(status) INCLUDE (title, created_at);

-- GIN for JSONB
CREATE INDEX idx_articles_metadata ON articles USING GIN(metadata);

-- Check for missing FK indexes
SELECT c.conrelid::regclass AS table, a.attname AS column
FROM pg_constraint c JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY(c.conkey)
WHERE c.contype = 'f'
AND NOT EXISTS (
    SELECT 1 FROM pg_index i WHERE i.indrelid = c.conrelid
    AND a.attnum = ANY(i.indkey)
);
```

## Zero-Downtime Migrations (Expand-Backfill-Contract)

```sql
-- Adding NOT NULL column to large table — NEVER in one step

-- Step 1: Add nullable (no lock on existing rows)
ALTER TABLE articles ADD COLUMN excerpt TEXT;

-- Step 2: Backfill in batches (data migration)
DO $$
DECLARE batch_size INT := 1000; offset_val INT := 0; rows_updated INT;
BEGIN
  LOOP
    UPDATE articles SET excerpt = LEFT(body, 200)
    WHERE id IN (SELECT id FROM articles WHERE excerpt IS NULL LIMIT batch_size);
    GET DIAGNOSTICS rows_updated = ROW_COUNT;
    EXIT WHEN rows_updated = 0;
    PERFORM pg_sleep(0.1);  -- yield to other queries
  END LOOP;
END $$;

-- Step 3: Add constraint (fast — all rows already have value)
ALTER TABLE articles ALTER COLUMN excerpt SET NOT NULL;

-- Lock classes for common DDL:
-- ADD COLUMN nullable: ACCESS SHARE (no lock)
-- ADD COLUMN with DEFAULT: ACCESS EXCLUSIVE (blocks all — avoid on large tables)
-- CREATE INDEX CONCURRENTLY: SHARE UPDATE EXCLUSIVE (allows DML)
-- ADD CONSTRAINT NOT NULL: ACCESS EXCLUSIVE (use 3-step above instead)
```

## Performance

```sql
-- Always run with ANALYZE BUFFERS
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) 
SELECT * FROM articles WHERE status = 'active' ORDER BY created_at DESC LIMIT 10;

-- Find slow queries
SELECT query, mean_exec_time, calls, total_exec_time
FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;

-- Find bloated tables/indexes
SELECT schemaname, tablename, n_dead_tup, n_live_tup, 
       round(n_dead_tup::numeric/NULLIF(n_live_tup,0)*100, 2) AS dead_ratio
FROM pg_stat_user_tables ORDER BY n_dead_tup DESC;
```

## ORM Choice

| Scenario | ORM |
|---|---|
| SQL-fluent team, complex queries, type safety | Drizzle |
| Rapid dev, schema-first, good defaults | Prisma |
| Full control, performance-critical | Raw SQL via psycopg2/asyncpg |
| Python + Django | Django ORM (avoid raw SQL unless N+1 is provable) |

Django ORM N+1 fix: always use `select_related()` for FK and `prefetch_related()` for M2M.

## Serverless Platform Choice

| Use case | Platform |
|---|---|
| Branching (staging/preview DBs) | Neon |
| Full Postgres + Auth + Realtime | Supabase |
| Edge/low-latency | Turso (SQLite-based) |
| Time-series heavy | TimescaleDB / Tiger Data |
| Already on AWS | RDS + PgBouncer |

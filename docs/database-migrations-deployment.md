# Database migration deployment

The FastAPI service uses Alembic as the schema source of truth. Do not create
application tables manually in the Supabase SQL editor or by starting Uvicorn.

## Render deployment

The backend Docker image includes `app/`, `alembic/`, and `alembic.ini`.
Both Render services run this pre-deploy command before starting the new web
process:

```sh
alembic upgrade head
```

Render supports `preDeployCommand` on paid web-service instance types. Free
web services do not support it. Keep the command in place only when the
corresponding Render service is on a paid compute plan; do not work around a
Free-plan limitation by running migrations in every Uvicorn worker at startup.
For a Free service, migrate through a separately approved one-off process
before deploying the application.

The Blueprint currently maps staging to `develop` and production to `main`.
A change merged only into another branch does not deploy either service.

## First migration of the Elevra Supabase project

The connected project was inspected read-only on 2026-11-10. At that time:

- The `public` schema contained no application tables.
- There was no `public.alembic_version` table and no Supabase CLI migration
  history table.
- `auth.users` contained zero records.
- The `vector` extension was available (default version 0.8.2) but not yet
  installed.

The Alembic chain includes a revision that runs
`CREATE EXTENSION IF NOT EXISTS vector`, followed by the reconciled schema
revisions. The latest public-schema security revision enables RLS on every
application table in `public` (leaving the Alembic ledger alone). Because
FastAPI is the intended database access layer, no anon/authenticated table
policies are added; direct Data API access remains deny-by-default. The backend
connects with its server-side database role, which must be the intended
privileged service role.

The PostgreSQL/pgvector integration test in CI creates a disposable empty
database, runs the full Alembic chain, compares tables/columns/types/indexes/
foreign keys with the active ORM, checks `vector`, and verifies RLS on all
application tables. This validates a fresh install only; it does not prove
compatibility with unknown historical schemas or identify the Render service's
actual database target.

Before the first production deployment, confirm a current Supabase backup,
confirm the Render `DATABASE_URL` secret points to the intended Elevra
project, and verify the migration test is green on the exact commit being
released. The pre-deploy command applies schema DDL; it does not seed demo
users or content. Admin users must be provisioned through the approved
authentication/admin workflow, not inserted as plaintext or hard-coded data.

## Recovery policy

These migrations are forward-only where existing account/session data could
be at risk. Do not run `alembic downgrade` as a routine rollback. Recover by
rolling the application back while preserving the schema, then apply a reviewed
forward migration or restore a verified database backup.

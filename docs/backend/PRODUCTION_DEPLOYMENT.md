# Elevra Backend Production Deployment

This document describes the repository's Render service contract. It does not
verify current dashboard values and does not authorize a deployment or database
migration.

## Runtime

- Render manifest: `/render.yaml`; production service is `elevra-api`, branch
  `main`, root directory `services/backend`, Docker runtime.
- Docker image uses Python 3.12 slim and installs `services/backend/requirements.txt`.
- ASGI import: `app.main:app`.
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`.
- Render liveness path: `/api/v1/health` (process-only).
- Dependency readiness path: `/api/v1/health/ready` (PostgreSQL and Redis;
  returns a generic 503 without connection details when either is unavailable).
- The image does not run Alembic. Schema changes require the reviewed,
  environment-gated migration workflow; never use startup-time automatic DDL.

## Required environment variable names

Set values in the Render service dashboard or approved secret manager. Do not
copy values into source control, client-visible variables, logs, or support
reports.

| Variable       | Purpose                                                                                                                             |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `ENVIRONMENT`  | Must be `production`; selects secure cookie behavior and production policy.                                                         |
| `DATABASE_URL` | Synchronous PostgreSQL URL. SQLAlchemy normalizes provider `postgres://`/`postgresql://` URLs to the installed Psycopg 3 driver.    |
| `REDIS_URL`    | Redis/Upstash shared cache and production rate-limit store. Production rate limiting fails closed with 503 if Redis is unavailable. |
| `JWT_SECRET`   | Signing key; must be a non-placeholder secret of at least 32 characters outside development/test.                                   |
| `CORS_ORIGINS` | Comma-separated exact frontend origins, with scheme and host only; no wildcard. Include verified student and admin origins.         |

Operational/tuning variables supported by code include `JWT_ISSUER`,
`JWT_AUDIENCE`, `ACCESS_TOKEN_TTL_SECONDS`, `REFRESH_TOKEN_TTL_SECONDS`,
`RATE_LIMIT_DEFAULT`, `RATE_LIMIT_LOGIN`, `RATE_LIMIT_REGISTER`,
`RATE_LIMIT_REFRESH`, `RATE_LIMIT_PASSWORD_RESET`, `DB_POOL_SIZE`,
`DB_MAX_OVERFLOW`, `DB_POOL_TIMEOUT`, and `DB_CONNECT_TIMEOUT`. Keep pool
capacity within the database connection limit after accounting for the number
of Render workers and other services.

`SUPABASE_DB_HOST`, `SUPABASE_DB_PORT`, `SUPABASE_DB_NAME`,
`SUPABASE_DB_USER`, `SUPABASE_DB_PASSWORD`, and `SUPABASE_SSLMODE` are a
fallback for composing local/provider-specific database URLs when `DATABASE_URL`
is absent. `ALEMBIC_DATABASE_URL` can override the migration URL in the
migration job. `DATABASE_URL_ASYNC` and the async session module are not used by
the current request path; the async driver is not in `requirements.txt`, so do
not treat it as a supported production path until it is deliberately completed.

`ENABLE_DOCS` appears in the example environment file but is not consumed by
the current settings or FastAPI construction. Verify the desired OpenAPI policy
before relying on it.

## CORS and cookies

- `allow_credentials=True`; wildcard origins are rejected at startup.
- `CORS_ORIGINS` must contain each verified frontend origin exactly. A new
  origin requires a reviewed Render config update and backend restart/redeploy.
- The refresh cookie is HttpOnly; in production it is Secure and SameSite=None,
  scoped to `/api/v1/auth`, and has no explicit Domain. Frontend requests must
  use `credentials: "include"`.
- Do not set a cookie Domain for a different registrable domain. With Vercel
  frontend domains calling an `onrender.com` API, browser third-party-cookie
  restrictions may affect refresh restoration. Validate in supported browsers;
  do not weaken cookie policy to make one browser pass.
- CORS preflight and credentialed error responses must be verified for every
  frontend origin after a release.

## Database and migration release gate

The current Alembic graph has a single head and has passed the fresh-install
PostgreSQL 16 + pgvector integration test, including active ORM parity and
public-table RLS checks. Evidence is in [CI run #15](https://github.com/arpitkumar28/elevra/actions/runs/42863342677)
and [CI run #27](https://github.com/arpitkumar28/elevra/actions/runs/42868755051).
This does not prove the starting state of an existing production database.

Before staging:

1. Verify which database the live Render service targets without copying or
   exposing its connection string. The linked Supabase project inventory is
   not proof of Render's target until the URL is checked.
2. Confirm a current backup/PITR point and a recovery procedure.
3. Dispatch the environment-gated migration workflow against staging only
   after checking the exact target and approval.
4. Verify the final Alembic revision, complete ORM schema, vector extension,
   RLS on every application table, `/api/v1/health/ready`, CORS, student
   registration/login, refresh rotation, ownership isolation and admin roles.
5. Review staging evidence and authorize production as a separate release.

The production Render service is shown as a Free instance. Render's
`preDeployCommand` is a paid-service feature, so do not assume the manifest's
pre-deploy Alembic command ran during the successful app deployment. Use the
reviewed migration workflow rather than running migrations in every Uvicorn
worker or at application startup.

The linked Supabase project was inspected read-only on 2026-11-10: zero public
application tables, no Alembic history, zero Auth users, and vector not
installed. No live migration, bootstrap admin or data write has been executed.
Do not use destructive Alembic downgrades as routine rollback; use a reviewed
forward fix or provider backup/PITR only under an explicit recovery decision.

## Operational checks

- Liveness: `GET /api/v1/health` should return 200 while the process is running.
- Readiness: `GET /api/v1/health/ready` should return 200 only when PostgreSQL
  and Redis are reachable; failure responses contain status only, no URLs.
- Inspect Render logs using request IDs. Current JSON request logs include
  method, path, status, duration, and request ID; request bodies and credentials
  must not be logged.
- Verify rate limiting is shared through Redis before increasing worker count.
- Confirm logs/alerts and the provider's rollback procedure before release.

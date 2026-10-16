# Environments

Elevra has three isolated environments. Docker Compose is local-development
infrastructure only; it is never a production dependency.

| Environment | Git branch       | Web and Admin                   | API                         | Data                                                         |
| ----------- | ---------------- | ------------------------------- | --------------------------- | ------------------------------------------------------------ |
| Development | feature branches | local Next.js                   | local FastAPI               | local PostgreSQL and Redis via Docker Compose                |
| Staging     | `develop`        | Vercel preview/staging projects | Render `elevra-api-staging` | dedicated Supabase project and Upstash Redis database        |
| Production  | `main`           | Vercel production projects      | Render `elevra-api`         | Supabase `elevraElevra` and dedicated Upstash Redis database |

Cloudflare owns public DNS, CDN, TLS and WAF in staging and production. Both
Next.js applications call FastAPI only: neither browser application receives a
database or Redis credential.

## Public Next.js configuration

Set `NEXT_PUBLIC_API_BASE_URL` per Vercel environment. Its value includes the
API version, for example `http://localhost:8000/api/v1` locally and
`https://api.<domain>/api/v1` in production. Only `NEXT_PUBLIC_*` values are
sent to the browser. Do not put `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`,
`SUPABASE_SERVICE_ROLE_KEY`, or private API keys in Vercel public variables.

## FastAPI configuration

Render reads its service definitions from [`render.yaml`](../../render.yaml).
Configure `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`, and `CORS_ORIGINS` as
secret Render environment variables. `CORS_ORIGINS` must be the comma-separated
Vercel origins for that environment; wildcard origins are not used.

`GET /api/v1/health` is a process health check. `GET /api/v1/health/ready`
checks PostgreSQL and Redis and returns `503` without connection details when a
dependency is unavailable. Public cache failures should be treated as cache
misses where the endpoint can safely continue.

## Migrations and releases

Alembic is the only migration authority. The deployment workflow runs
`alembic upgrade head` against the GitHub `staging` or `production`
environment after branch protection and any environment approval. Staging
migrations require a manual workflow dispatch on `develop` with the
`migration_history_reviewed` confirmation enabled; production uses the same
gate on `main`. This confirms the migration history has passed a fresh
PostgreSQL upgrade test and review. Pushes cannot run migrations automatically.
Add the corresponding `DATABASE_URL` GitHub environment secret before enabling
releases. Render deploys from GitHub only after CI succeeds; it does not run
migrations.
The `20260821_merge_deployment_heads` migration establishes one Alembic head
without changing either existing branch.

Verify the Supabase `vector` extension using a read-only query before features
depend on semantic search; the existing Alembic pgvector migration enables it.

# Elevra Backend Implementation Plan

## Audit scope and decision

Audited the FastAPI application, database configuration, models, schemas, API
routers, authentication/authorization, Redis rate limiting, deployment files,
Alembic history, and existing tests on branch
`codex/website-design-transformation`. The active SQLAlchemy metadata contains
21 tables. Alembic reports one head, `20260821_core_platform_domains`, but the
history still has two independent roots and overlapping table creation. There
is no successful disposable PostgreSQL/pgvector upgrade evidence in this
checkout. **Production readiness is NO-GO.**

## Prioritized work

| Priority | Finding / work                                                            | Current evidence                                                                                                                                                                                                                                                                                             | Status / acceptance                                                                                                                                                                                                       |
| -------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| P0       | Reconcile migration roots and prove a fresh PostgreSQL + pgvector upgrade | `20260718_0001` and `20260812_initial_tables` are independent roots; both create `users`; later revisions overlap legacy `opportunities`, `courses`, `bookmarks`, `applications`, `notifications`, and `audit_logs`. ORM also requires `account_tokens` and `refresh_tokens`, absent from Alembic revisions. | **Blocked.** Keep migration files unchanged until a disposable PostgreSQL runner passes and all deployed starting states are inventoried. Require schema comparison for all 21 tables and exactly one final revision row. |
| P0       | Ensure credentialed CORS headers on server errors                         | Reproduced: allowed-origin `OPTIONS` returned 200 with CORS headers, while an uncaught endpoint failure returned 500 without them.                                                                                                                                                                           | **Fixed locally.** Outer CORS middleware now wraps the error response path; regression test covers 500. Require preflight and error tests for verified student/admin origins in CI.                                       |
| P0       | Protect request values in validation errors                               | Pydantic validation errors contain the original submitted input; the previous handler returned those values.                                                                                                                                                                                                 | **Fixed locally.** Handler returns only `loc`, `msg`, and `type`; regression test confirms a rejected password is not echoed.                                                                                             |
| P1       | Deliver password-reset and verification messages                          | Auth routes create hashed, expiring account tokens but no mail provider or background worker exists. Current success messages say an email was sent although delivery is not implemented.                                                                                                                    | **Blocked on approved provider/configuration and delivery contract.** Add provider integration, outbox/retry behavior, and delivery tests before advertising these flows.                                                 |
| P1       | Make registration/session creation atomic                                 | Registration commits the user before creating the refresh-session record; token/session failure can leave an account without a completed registration response.                                                                                                                                              | Add transaction-failure regression, then move to one transaction and verify rollback before changing behavior.                                                                                                            |
| P1       | Bound Redis operations                                                    | Production rate limiting uses Redis and returns 503 on Redis failure, which fails closed. The synchronous Redis client currently has no explicit socket/connect timeout and is called from an async dependency.                                                                                              | Add bounded client timeouts and avoid blocking the event loop; test timeout/failure behavior with a fake client. Keep the fail-closed policy.                                                                             |
| P1       | Keep private data ownership enforced                                      | Profile, bookmark, application, notification, and test-attempt routes resolve records by authenticated user ID. Admin operations depend on database-backed roles. Existing tests cover several cross-user and role cases.                                                                                    | Expand route-by-route unauthorized/cross-user tests and keep authorization at the API boundary.                                                                                                                           |
| P1       | Make live operational endpoints truthful                                  | `/api/v1/health` is liveness; `/api/v1/health/ready` checks PostgreSQL and Redis with a generic degraded response. Render currently probes liveness.                                                                                                                                                         | Keep liveness independent from dependencies; confirm ready behavior with injected DB/Redis failures. Add explicit `/health/live` only if platform contract needs it.                                                      |
| P1       | Complete API and workflow gaps                                            | Admin overview returns 501. Password/email account recovery lacks delivery. Core content and student account APIs exist; tests are database-backed through isolated SQLite fixtures, not a replacement for PostgreSQL integration.                                                                           | Complete by endpoint contract and add tests before frontend labels imply working behavior.                                                                                                                                |
| P2       | Reduce duplicate/dead database and router code                            | `infrastructure/database/session.py` defines an unused async engine; the runtime uses synchronous `app.db.session`. The async URL path needs `asyncpg`, which is absent from requirements. A sample opportunities router contains demo records but is not mounted.                                           | Inventory references, then remove or finish these only in a separate reviewed change. Do not route demo data into public APIs.                                                                                            |
| P2       | Improve database pool/transaction observability                           | Sync engine has `pool_pre_ping`, bounded pool settings and connect timeout; `get_db` rolls back on request exceptions. Readiness suppresses infrastructure details.                                                                                                                                          | Add tests for pool/session cleanup and safe DB-unavailable responses; tune capacity to the actual Render worker count.                                                                                                    |
| P2       | Expand test scoring and API contract checks                               | Server computes test scores and scopes attempts to the user; no PostgreSQL schema test has passed.                                                                                                                                                                                                           | Test expiry, duplicate submissions/answers, concurrent attempts, score boundaries, and ORM/schema parity on disposable PostgreSQL.                                                                                        |
| P3       | Background jobs and verified content ingestion                            | No task queue, scheduler, email provider, or production content ingestion worker was found.                                                                                                                                                                                                                  | Add only when product/provider requirements are confirmed; jobs must be retryable and idempotent.                                                                                                                         |

## Current architecture snapshot

- Runtime: `services/backend/app/main.py`, ASGI target `app.main:app`.
- Mounted router: `services/backend/app/api/v1/router.py`, prefixed with
  `/api/v1`.
- Active API modules include auth, profile, account/bookmarks/applications/
  notifications, exams, opportunities, courses/current affairs, tests, and
  admin content. `/admin/overview` currently returns 501.
- Database: synchronous SQLAlchemy engine in `app.db.session`; request sessions
  roll back on exceptions and close in `finally`.
- Cache/rate limiting: Redis/Upstash client; production limiter uses an atomic
  Redis Lua increment with TTL and returns 503 when Redis fails.
- Authentication: bcrypt password hashes, short-lived JWT access tokens,
  persisted hashed refresh tokens with rotation/revocation, and an HttpOnly
  refresh cookie. Public registration explicitly assigns the student role.
- Authorization: backend loads the active user for each access token and
  checks admin role/flag; student-private resource handlers filter by user ID.
- Deployment: Render Docker service runs Uvicorn and does not run migrations.

## Safe implementation sequence

1. Keep the current migration state no-go. Provision an isolated PostgreSQL 16
   - pgvector runner, reproduce fresh-upgrade failure, and collect read-only
     revision/schema inventories for any environment claimed as deployed.
2. Review and test a forward-only migration repair against an empty database
   and every confirmed starting state. Never stamp or use destructive downgrade
   as recovery.
3. Add database/Redis fault-injection tests and fix transaction/timeout issues
   that do not depend on changing schema.
4. Complete auth delivery only after selecting and configuring an email
   provider; do not report reset/verification email as delivered without provider
   confirmation.
5. Audit each student/admin endpoint for validation, pagination, publication
   visibility, role requirements, and owner scoping; add a regression for each
   confirmed defect.
6. Run the full unit suite, PostgreSQL/pgvector integration suite, lint/type
   checks, and deployment smoke checks in CI. Stage only after review and backup
   verification; production requires separate approval.

## Commands and current limitations

From the repository root:

```bash
services/backend/.venv/bin/python -m pytest services/backend/tests -q -m 'not integration'
services/backend/.venv/bin/python -m pytest services/backend/tests/test_migrations_postgres.py -q -m integration
```

The first command can run against the test fixture. The second requires the
dedicated local `elevra_migration_test` PostgreSQL database with pgvector and a
local-only `ELEVRA_MIGRATION_TEST_DATABASE_URL`; it must fail rather than skip
when that runner is absent. No migration repair or production database access
is authorized by this plan.

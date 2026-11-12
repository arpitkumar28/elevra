# Elevra Backend Implementation Plan

## Audit scope and release decision

Reviewed the FastAPI application, database configuration, models, schemas, API
routers, authentication/authorization, Redis rate limiting, deployment files,
Alembic history, and CI tests on `codex/website-design-transformation`.

The active migration head is `20261111_opportunity_work_mode`. CI exercises a
fresh PostgreSQL + pgvector upgrade and checks ORM/schema/RLS parity. That
proves the disposable empty-database path; it does **not** establish the
starting revision or backup state of a deployed staging/production database.

**Production data migrations remain gated** until the exact live target is
identified read-only, a current backup/PITR point is confirmed, and recovery
steps are reviewed.

## Prioritized work

| Priority | Work | Current evidence | Status / acceptance |
| --- | --- | --- | --- |
| P0 | Verify live staging/production database targets and recovery gates | CI proves a fresh PostgreSQL + pgvector migration. It cannot prove which database the deployed Render service targets or its current revision. | **Release gate.** Identify target without exposing credentials, verify provider backup/PITR and a tested recovery path, then run staging verification under explicit approval. No production migration is authorized by this plan. |
| P0 | Keep credentialed CORS headers on server errors | Outer CORS middleware wraps the error response path; tests cover failed requests and preflight behavior. | **Implemented.** Keep regression coverage for all verified student/admin origins. |
| P0 | Avoid echoing sensitive input in validation errors | Validation handler returns safe error fields and has a regression proving rejected passwords are not reflected. | **Implemented.** |
| P1 | Make registration/session creation atomic | Registration flushes the user and creates its refresh-session row before token-pair creation commits. PR #32 added a regression asserting one commit and a linked refresh session. | **Merged in PR #32.** Keep rollback and one-commit regression tests. |
| P1 | Bound Redis operations | Redis now has explicit connect/socket timeouts; the synchronous Lua counter runs in a worker thread and still fails closed with 503 when Redis is unavailable. | **Implemented in PR pending review.** Tests cover timeout configuration, event-loop responsiveness, atomic counters, and failure behavior. Validate timeout values against the selected Redis provider. |
| P1 | Deliver password-reset and verification messages | Account tokens are stored hashed and expire, but no mail provider, verified sender, persistent outbox, or delivery worker is configured. Current public success text must not be interpreted as proof of delivery. | **Blocked on provider setup.** Select provider, verify sender/domain, add secrets, idempotent delivery/outbox + retry behavior, and verify acceptance before claiming an email was sent. |
| P1 | Audit private-resource ownership and admin permissions | Student handlers generally filter by authenticated user ID; admin endpoints use backend permission checks. Existing tests cover key cross-user and role cases. | **In progress.** Maintain a route-by-route matrix for authentication, ownership, role, and negative cases; add regressions for every uncovered endpoint. |
| P1 | Make operational health endpoints truthful | `/api/v1/health` is process liveness; `/api/v1/health/ready` checks PostgreSQL and Redis and returns a generic failure without infrastructure details. | **Implemented.** Verify injected database/Redis failures and keep platform probes on liveness. |
| P1 | Complete the admin overview and opportunity workflow | Admin overview now returns live opportunity/application/student counts and recent audit events. Opportunity lifecycle, work-mode filters, application status history, follow-up dates, and private notes are implemented. | **Implemented in current feature set.** Keep API/UI contract tests and avoid stale 501 expectations in documentation. |
| P2 | Improve database pool and transaction observability | Sync SQLAlchemy engine uses pre-ping, bounded pool configuration, connection timeout, rollback on request exceptions, and session close in `finally`. | Add pool/session cleanup tests and tune limits to actual Render worker count and provider connection limits. |
| P2 | Expand test scoring and API-contract checks | Test attempts are scoped to the authenticated user and server-side scoring exists. | Add expiry, duplicate submissions/answers, concurrent attempts, score-boundary, and ORM/schema parity tests. |
| P2 | Remove dead/duplicate infrastructure code | An unused async engine/session module and unmounted demo router have been identified. | Inventory all references first; remove or complete them in a separate reviewed change. Never expose demo data through mounted APIs. |
| P3 | Background jobs and verified content ingestion | No production task queue, scheduler, or trusted ingestion worker is configured. | Add only after product and provider requirements are approved; jobs must be idempotent, retryable, and observable. |

## Current architecture snapshot

- Runtime: `services/backend/app/main.py`, ASGI target `app.main:app`.
- Versioned API router: `services/backend/app/api/v1/router.py`, prefix
  `/api/v1`.
- Active modules include auth, profile, bookmarks, applications, notifications,
  exams, opportunities, courses/current affairs, tests, and admin content.
- `GET /api/v1/admin/overview` returns live metrics and recent audit activity.
- Database runtime uses the synchronous SQLAlchemy engine in
  `app.db.session`; request sessions roll back on exceptions and always close.
- Production rate limiting uses an atomic Redis Lua counter. Redis failures
  fail closed with 503; network calls are bounded and run off the ASGI event
  loop.
- Authentication uses bcrypt password hashes, short-lived JWT access tokens,
  persisted hashed refresh tokens with rotation/revocation, and an HttpOnly
  refresh cookie. Public registration assigns the student role.
- Authorization is enforced by the backend; student-private resources filter
  by authenticated user ID and administrative routes require permissions.
- Render runs the Dockerized Uvicorn service. The backend image does not run
  Alembic automatically; migrations use the reviewed workflow.

## Safe implementation sequence

1. Finish CI verification for the atomic-registration and Redis-reliability
   changes; merge only after required checks pass.
2. Expand authorization/ownership coverage for each student and admin route.
3. Select and configure an email provider and verified sender. Implement a
   durable outbox/worker with retries and idempotency; do not claim delivery
   before provider acceptance is confirmed.
4. Add database pool/session and test-scoring regression coverage.
5. Verify exact staging database target and backup/PITR state read-only.
   Execute the staging migration workflow only after review and approval.
6. Review staging smoke tests, then request separate production release
   approval. Never run a production migration as an incidental code change.

## Commands

From the repository root:

```bash
services/backend/.venv/bin/python -m pytest services/backend/tests -q -m 'not integration'
services/backend/.venv/bin/python -m pytest services/backend/tests/test_migrations_postgres.py -q -m integration
```

The integration command requires the dedicated local `elevra_migration_test`
PostgreSQL database with pgvector and a local-only
`ELEVRA_MIGRATION_TEST_DATABASE_URL`. It must fail rather than skip when that
runner is absent. Never point it at staging or production.

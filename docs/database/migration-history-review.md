# Alembic migration history review

> **Current status (2026-11-10):** This document was refreshed after the migration
> graph repair in PR #7 and the public-schema RLS revision in PR #15. The older
> collision notes in the prior revision of this document are historical and no
> longer describe the current fresh-install path. GitHub Actions run #15 passed
> the PostgreSQL 16 + pgvector fresh-upgrade/ORM parity test; run #27 passed the
> same integration test with the RLS assertions. This proves a fresh disposable
> database path, not compatibility with every previously deployed database.
> No live Supabase migration has been executed.

## Current migration graph

| Revision | Parent(s) | Current responsibility |
|---|---|---|
| `20260718_0001` | base | Legacy RBAC/reference/analytics tables: users (when absent), roles, permissions, user_roles, role_permissions, organizations, mock_tests, ai_chats, study_plans, settings, analytics_events |
| `20260812_initial_tables` | base | Creates student_profiles and creates users only when absent; adds supporting indexes |
| `20260812_add_exams_opportunities` | `20260812_initial_tables` | Exam/opportunity enum types and tables: exams, exam_syllabi, exam_patterns, exam_dates, exam_faqs, opportunities |
| `20260813_enable_pgvector` | `20260812_add_exams_opportunities` | Installs the PostgreSQL `vector` extension |
| `20260821_merge_deployment_heads` | `20260718_0001`, `20260813_enable_pgvector` | Merge-only revision joining the two roots |
| `20260821_core_platform_domains` | merge revision | Creates courses, current_affairs, tests, questions, question_options, test_attempts, test_answers, bookmarks, applications, notifications, audit_logs |
| `20261110_align_active_orm` | `20260821_core_platform_domains` | Reconciles users/profile fields, adds account_tokens and refresh_tokens, and completes ORM indexes |
| `20261110_enable_public_rls` | `20261110_align_active_orm` | Enables Row Level Security on every public application table, leaving the Alembic ledger alone |

The repository still has two historical roots which converge at the merge
revision. The current bodies were reconciled for a fresh install and the CI
integration test verifies the resulting schema against SQLAlchemy metadata.
Do not infer compatibility with a database that has already run an older or
different migration sequence without inspecting that database first.

## Baseline SQL comparison

`supabase/migrations/20260815000000_initial_elevra_backend.sql` is an older,
incomplete baseline. It creates some account, exam, opportunity and token
objects, but it does not initialize all current ORM domains. It is not the
selected fresh-install path; use the current Alembic graph. Repository history
does not prove the baseline SQL was applied to any particular project.

## Fresh-install verification

The opt-in integration test uses `docker-compose.migration-test.yml` and
`services/backend/tests/test_migrations_postgres.py`. It accepts only the
dedicated local PostgreSQL database `elevra_migration_test`, requires an empty
public schema, runs `alembic upgrade head`, then checks:

- expected ORM tables, columns, nullability, types and server defaults;
- foreign keys, indexes and uniqueness;
- the installed `vector` extension and final Alembic revision;
- RLS enabled on every public application table.

Verification evidence:

- [CI run #15 — fresh PostgreSQL/pgvector schema verification](https://github.com/arpitkumar28/elevra/actions/runs/42863342677)
- [CI run #27 — RLS-enabled PostgreSQL/pgvector schema verification](https://github.com/arpitkumar28/elevra/actions/runs/42868755051)

Example local command sequence (the generated password stays in the shell
environment):

```bash
export ELEVRA_MIGRATION_TEST_PASSWORD="$(python3 -c 'import secrets; print(secrets.token_urlsafe(24))')"
docker compose -f docker-compose.migration-test.yml up --wait -d
export ELEVRA_MIGRATION_TEST_DATABASE_URL="postgresql+psycopg://elevra_test:${ELEVRA_MIGRATION_TEST_PASSWORD}@localhost:55432/elevra_migration_test"
services/backend/.venv/bin/python -m pytest services/backend/tests/test_migrations_postgres.py -q -m integration
docker compose -f docker-compose.migration-test.yml down
```

Run only against the dedicated disposable test service. The test intentionally
rejects remote hosts and any database other than `elevra_migration_test`.

## Current Supabase inventory (read-only)

The linked Supabase project was inspected on 2026-11-10:

- `public` contained zero application tables;
- there was no `public.alembic_version` history;
- `auth.users` contained zero accounts;
- the `vector` extension was available but not installed.

This is an inventory of the linked Supabase project only. It does not prove
that the Render production service's `DATABASE_URL` points to that project.
No DDL, migration, seed data, user creation or other database write was made.
Verify the Render target before treating this inventory as the service's
actual database starting state.

## RLS and database access model

The backend uses its server-side database connection as the application data
access layer. The RLS revision enables RLS for public application tables but
does not add `anon` or `authenticated` policies. Keep direct Data API access
deny-by-default unless a separate reviewed feature explicitly requires it.
The FastAPI service must connect using the intended privileged server-side
database role; never place that credential in a `NEXT_PUBLIC_*` variable.

## First deployment and recovery gate

1. Verify which Supabase project the production Render `DATABASE_URL` targets,
   without copying or sharing its value.
2. Confirm a current backup/PITR point and verify recovery instructions.
3. Run the reviewed migration workflow against staging first; this repository's
   Render service is Free, so do not assume the Render `preDeployCommand` ran.
4. Verify the final revision, tables, RLS, vector extension, API readiness,
   authentication, refresh rotation, student ownership and admin authorization.
5. Approve production separately after staging evidence and target verification.

The migration workflow in `.github/workflows/deploy-migrations.yml` is manually
dispatched and environment-gated. Do not run it as a discovery step or against
an unverified target. Do not use destructive Alembic downgrades as routine
rollback; use a reviewed forward fix or an explicitly approved backup restore.

## Initial administrator

The first administrator is created only after the target environment's schema
is migrated and verified. PR #14 adds an interactive, guarded command:
`python -m app.commands.bootstrap_admin`. It requires a TTY, hidden password
input, strong registration-compliant password, refuses existing admins and
existing student accounts, and is not a public HTTP endpoint. The command has
not been run in any environment.

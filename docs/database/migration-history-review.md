# Alembic migration history review

## Current graph and affected tables

| Revision                           | Parent(s)                                   | Tables or objects affected                                                                                                                                                                                                                                                                                             | Compatibility notes                                                                                                                                                                                                                               |
| ---------------------------------- | ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `20260718_0001`                    | base                                        | `users`, `roles`, `permissions`, `user_roles`, `role_permissions`, `organizations`, `opportunities`, `courses`, `lessons`, `notes`, `mock_tests`, `bookmarks`, `notifications`, `ai_chats`, `study_plans`, `applications`, `audit_logs`, `settings`, `analytics_events`; indexes on opportunities and analytics events | `users`, `opportunities`, `courses`, `bookmarks`, `applications`, `notifications`, and `audit_logs` use legacy shapes. `CREATE TABLE IF NOT EXISTS` does not reconcile an existing incompatible table. Downgrade drops this group with `CASCADE`. |
| `20260812_initial_tables`          | base                                        | `users`, `student_profiles`; indexes on email and profile user id                                                                                                                                                                                                                                                      | Creates `users` unconditionally. `student_profiles` is missing most active profile fields, and its user id has no FK/unique constraint.                                                                                                           |
| `20260812_add_exams_opportunities` | `20260812_initial_tables`                   | adds `users.is_admin`; creates exam/opportunity enum types; creates `exams`, `exam_syllabi`, `exam_patterns`, `exam_dates`, `exam_faqs`, and `opportunities`; related indexes                                                                                                                                          | `opportunities` is unconditional and collides with the legacy root if both are upgraded. Enum creation is check-first, but the table operations are not. Several active model indexes are missing.                                                |
| `20260813_enable_pgvector`         | `20260812_add_exams_opportunities`          | creates extension `vector`                                                                                                                                                                                                                                                                                             | Downgrade drops the extension, which may be shared by other objects.                                                                                                                                                                              |
| `20260821_merge_deployment_heads`  | `20260718_0001`, `20260813_enable_pgvector` | no schema objects                                                                                                                                                                                                                                                                                                      | Merge-only revision. It produces one head but retains both independent bases.                                                                                                                                                                     |
| `20260821_core_platform_domains`   | merge revision                              | `courses`, `current_affairs`, `tests`, `questions`, `question_options`, `test_attempts`, `test_answers`, `bookmarks`, `applications`, `notifications`, `audit_logs`                                                                                                                                                    | Unconditionally creates tables overlapping the legacy root. The active tables are mostly represented, but many ORM indexes are absent. Downgrade drops its tables.                                                                                |

The graph has a single head but two roots. A fresh `upgrade head` traverses both roots and reaches duplicate table operations. The active ORM contract is documented in [active-orm-schema.md](active-orm-schema.md).

## Baseline comparison

`supabase/migrations/20260815000000_initial_elevra_backend.sql` creates `vector`, the four exam/opportunity enum types, users, student profiles, refresh/account tokens, exams and detail tables, and opportunities; it enables RLS on those tables. It does not create current-affairs, course, test/question/attempt, bookmark, application, notification, or audit-log tables. It is therefore not a complete initializer for current ORM metadata.

The baseline's `users` shape is close to the active ORM model. It includes `refresh_tokens` and `account_tokens`, which no Alembic revision creates. The ORM uses SQLAlchemy `JSON`; the baseline uses `jsonb` for profile JSON. The baseline's email and token indexes include redundant explicit indexes alongside unique constraints. Exam and opportunity enum labels align with the ORM enums, but index coverage differs. No evidence in this repository proves the baseline was executed or is recorded by Supabase migration history.

## Safe correction boundary

Do not delete or rename historical revision identifiers, stamp a database, or use destructive downgrades. A fresh-database correction and a deployed-database correction are different requirements: changed historical migration bodies affect only databases that have not applied those revisions; a new forward revision is needed for already-recorded histories. The two legacy table families require explicit data-preserving transformations, not `IF NOT EXISTS` alone.

Before authoring a compatibility migration, inventory the actual Render target and each maintained environment read-only: schemas/tables/columns/constraints/indexes/enums/extensions, `public.alembic_version` rows, and whether the separate Supabase SQL baseline was applied. Until then, compatibility for any historical state is unverified. The supplied empty-public-schema result is not enough to establish the live Render mapping.

## Disposable PostgreSQL/pgvector fresh-upgrade test

The opt-in test uses `docker-compose.migration-test.yml` and `services/backend/tests/test_migrations_postgres.py`. It accepts only local PostgreSQL database `elevra_migration_test`, requires an initially empty public schema, runs `alembic upgrade head`, and checks active ORM columns, nullability, types, foreign keys, indexes, uniqueness, `vector`, and the final revision.

Example local commands (the generated test password stays in the shell environment):

```bash
export ELEVRA_MIGRATION_TEST_PASSWORD="$(python3 -c 'import secrets; print(secrets.token_urlsafe(24))')"
docker compose -f docker-compose.migration-test.yml up --wait -d
export ELEVRA_MIGRATION_TEST_DATABASE_URL="postgresql+psycopg://elevra_test:${ELEVRA_MIGRATION_TEST_PASSWORD}@localhost:55432/elevra_migration_test"
services/backend/.venv/bin/python -m pytest services/backend/tests/test_migrations_postgres.py -q -m integration
docker compose -f docker-compose.migration-test.yml down
```

The integration test is intentionally opt-in and does not drop or recreate a database. Run it only against the dedicated disposable service. The current migration graph is expected to fail the fresh-upgrade assertion; no successful PostgreSQL/pgvector run is claimed. Historical starting-state tests should be added only for states confirmed by database inventory.

## Admin bootstrap boundary

An admin bootstrap command is separate from schema initialization and must wait until the canonical schema passes the disposable PostgreSQL test. It should prompt for email and a hidden password, reuse the existing Pydantic registration password validation and bcrypt `hash_password`, lock/check for any existing active admin inside one transaction, abort on duplicates or an existing admin, and require operator identity verification before promoting an existing student. It must not be exposed over HTTP or log credentials. No bootstrap command is implemented or run by this review.

## Staging and rollback gate

1. Verify the Render service's database target in the dashboard without copying the connection string.
2. Collect the read-only schema and Alembic revision inventory; identify whether the baseline SQL was applied.
3. Review the forward migration and test an empty database plus every confirmed starting state on disposable PostgreSQL with pgvector.
4. Take and verify a staging backup/PITR point, apply the reviewed migration only to staging, then check revision rows, expected schema, readiness, login, and account-token flows.
5. Production requires a separate review/approval after staging evidence. Never run the migration workflow against production as a discovery step.

Use a reviewed forward fix for migration failure. Restore a provider backup/PITR point only under an explicit recovery decision. Existing downgrade functions drop data and are not a recommended rollback procedure.

# Phase 2 Migration Verification

**Repository:** `arpitkumar28/elevra`  
**Verification date:** 2026-11-10  
**Decision:** **NO-GO for production database migration**

## Executive result

The Phase 1 pull request is already merged. The GitHub Actions workflow executed the PostgreSQL migration integration test against its disposable PostgreSQL service and reproduced a real migration failure. This is stronger evidence than the previous offline SQL review, but it is not a passing migration.

- Phase 1 PR: https://github.com/arpitkumar28/elevra/pull/1
- PR state: merged
- PR head: `9e495f43e3847c4df8715e63e435bf1028a5f0e8`
- Merge commit: `ee306f29c87ed8e0e5ff35394f8bdc843539e002`
- CI run: https://github.com/arpitkumar28/elevra/actions/runs/42854413034
- CI run ID: `42854413034`

No production Supabase or Render database was accessed. No production migration or data write was performed.

## CI environment and job results

The workflow used the configured `pgvector/pgvector:pg16` service image and a dedicated `elevra_migration_test` database. The PostgreSQL service log reports PostgreSQL **16.15** and a successful readiness check. The integration test verified that the public schema was empty before starting the upgrade.

| Job / check                      | Result     | Evidence                                                                            |
| -------------------------------- | ---------- | ----------------------------------------------------------------------------------- |
| Web                              | Passed     | `pnpm lint`, `pnpm typecheck`, `pnpm test`, and `pnpm build` completed successfully |
| Mobile                           | Passed     | `flutter analyze` and `flutter test` completed successfully                         |
| Backend dependencies             | Passed     | `pip check` passed                                                                  |
| Backend non-integration tests    | Passed     | 58 passed, 1 deselected, 1 warning                                                  |
| PostgreSQL migration integration | **Failed** | `alembic upgrade head` exited 1                                                     |
| Dependency security audit        | **Failed** | `pnpm audit --prod --audit-level high` found 49 vulnerabilities                     |

The dependency security result is separate from the database migration failure. The audit output reports 4 low, 19 moderate, 19 high, and 7 critical findings. Examples in the log include Next.js versions in the admin/web/marketing workspaces, sharp, source-map-js, and zod. The Python `pip-audit` step was skipped because the preceding pnpm audit command failed. These findings require package-level triage; the summary count alone does not establish exploitability in each deployed path.

## Reproduced migration failure

**Failing test:** `services/backend/tests/test_migrations_postgres.py::test_fresh_postgres_pgvector_upgrade_matches_active_orm`

**Failure:**

```text
psycopg.errors.UndefinedColumn:
column "deadline_at" does not exist

sqlalchemy.exc.ProgrammingError:
(psycopg.errors.UndefinedColumn) column "deadline_at" does not exist
```

**Migration location in the traceback:**

`services/backend/alembic/versions/20260718_0001_initial_schema.py:19`

The traceback identifies the `op.execute(...)` block. The failing SQL in that block includes:

```sql
CREATE INDEX IF NOT EXISTS ix_opportunities_type_status_deadline
  ON opportunities(type, status, deadline_at);
```

## Root cause analysis

The migration graph has two independent roots which later converge:

1. `20260718_0001_initial_schema`
2. `20260812_initial_tables` → `20260812_add_exams_opportunities` → `20260813_enable_pgvector`

The merge revision `20260821_merge_deployment_heads` joins those branches, and `20260821_core_platform_domains` follows the merge.

The two branches define incompatible versions of the `opportunities` table:

- `20260812_add_exams_opportunities.py` creates `opportunities.deadline` as a nullable PostgreSQL DATE column.
- `20260718_0001_initial_schema.py` contains `CREATE TABLE IF NOT EXISTS opportunities` with a `deadline_at` varchar column, then creates an index on `(type, status, deadline_at)`.

The error proves that, when the legacy root's index statement ran, an `opportunities` table already existed without `deadline_at`. The earlier branch's table definition is the matching conflict: its column is named `deadline`, not `deadline_at`.

Because `CREATE TABLE IF NOT EXISTS` leaves an existing table unchanged, it does not reconcile the two definitions. The subsequent index statement therefore fails. This is a reproduced schema collision, not merely a suspected duplicate-table risk.

The active ORM model `services/backend/app/models/opportunity.py` also defines `deadline` as a nullable SQLAlchemy Date column. This is evidence that the `deadline` form matches the current application model, but it does not by itself establish the correct strategy for every database that may already exist.

## What the run did not establish

- The migration did not reach the final ORM/schema parity assertions.
- The post-failure database schema and Alembic revision rows were not captured by the test.
- The exact pgvector extension version was not recorded.
- The final Alembic revision state after failure is unknown.
- No existing deployed database starting state was inventoried.
- No production database connection was attempted.

Do not infer a successful extension installation or schema upgrade from the PostgreSQL service startup alone.

## Additional migration risks to review after the first conflict

Static inspection shows that the legacy root also creates `courses`, `bookmarks`, `applications`, `notifications`, and `audit_logs` using `CREATE TABLE IF NOT EXISTS`. The later `20260821_core_platform_domains.py` revision creates several of those table names with unconditional `op.create_table(...)` calls. Those are likely subsequent duplicate-table or schema-shape conflicts once the current failure is addressed. They have **not** yet been reproduced in the integration run because execution stops earlier.

The graph's single Alembic head does not remove the two-root history or prove upgrade safety.

## Recommended repair strategy — review required

1. Treat the active ORM as the target schema contract, then compare every migration definition against it. For `opportunities`, the current model uses `deadline DATE`.
2. Map the exact execution order and object ownership across both roots; identify which revision is responsible for each table, enum, and index.
3. Design one consistent fresh-install path so a table has one canonical definition and later revisions add only explicit, compatible changes.
4. Preserve historical revision identifiers and avoid editing already-applied migration bodies until every supported deployed starting state is inventoried. Since the fresh path currently fails before head, a forward-only repair must be designed carefully; a new head-only migration cannot fix a fresh upgrade that never reaches the head.
5. Test the candidate repair against a fresh disposable PostgreSQL 16 + pgvector database and each confirmed non-production starting-state fixture. Assert all 21 ORM tables, columns, foreign keys, indexes, constraints, enums, extension state, and the final Alembic revision.
6. Do not use `IF NOT EXISTS` as a blanket workaround, stamp the database to head, or use destructive downgrades as recovery.
7. Only after CI migration validation passes should a separate, approved read-only inventory of the real target database and a backup/recovery plan be considered. Production migration remains a separate approval.

## Files and resources inspected

- `.github/workflows/ci.yml`
- `services/backend/tests/test_migrations_postgres.py`
- `services/backend/alembic/versions/20260718_0001_initial_schema.py`
- `services/backend/alembic/versions/20260812_initial_tables.py`
- `services/backend/alembic/versions/20260812_add_exams_opportunities.py`
- `services/backend/alembic/versions/20260813_enable_pgvector.py`
- `services/backend/alembic/versions/20260821_merge_deployment_heads.py`
- `services/backend/alembic/versions/20260821_core_platform_domains.py`
- `services/backend/app/models/opportunity.py`

## Final decision

**NO-GO.** The disposable PostgreSQL integration test reproduced a concrete migration failure at the `deadline_at` index. More overlapping table definitions remain to be reviewed, the final ORM/schema parity test was not reached, the actual deployed database state is unknown, and the dependency-security job is failing. No production database access, migration, data change, or deployment was performed.

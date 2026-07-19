# Elevra

Elevra is an AI-powered Student Operating System for opportunity discovery, smarter learning,
exam preparation, and career readiness.

This repository is a production-oriented monorepo for:

- Marketing website: `apps/marketing`
- Student web app: `apps/web`
- Admin dashboard: `apps/admin`
- Flutter mobile app: `apps/mobile`
- FastAPI backend: `services/backend`
- Crawlers: `services/crawler`
- AI orchestration: `services/ai-engine`
- Scheduled jobs: `services/scheduler`
- Search orchestration: `services/search`
- Shared TypeScript packages: `packages/*`
- Infrastructure, scripts, and documentation

## Architecture

The repository separates deployable applications from reusable packages and backend services.
Python services are split by business capability so they can scale independently. The backend uses
clean architecture folders:

- `api`: versioned HTTP routes and transport DTOs
- `domain`: entities, value objects, and policies
- `application`: use cases and orchestration
- `infrastructure`: adapters for PostgreSQL, Redis, S3, OAuth, and search
- `core`: configuration, security, logging, and observability primitives

## Requirements

- Node.js 22+
- pnpm 9+
- Python 3.12+
- Flutter stable channel
- Docker and Docker Compose

## Quick Start

```bash
cp .env.example .env
pnpm install
docker compose --env-file .env up -d postgres redis meilisearch minio
pnpm dev
```

Service health checks:

- Backend: `http://localhost:8000/api/v1/health`
- Crawler: `http://localhost:8010/health`
- AI engine: `http://localhost:8020/health`
- Scheduler: `http://localhost:8030/health`
- Search: `http://localhost:8040/health`

Web apps:

- Marketing: `http://localhost:3000`
- Student app: `http://localhost:3001`
- Admin: `http://localhost:3002`

## Root Files

- `package.json`: root workspace scripts, tool versions, Husky, Commitlint, and lint-staged config.
- `pnpm-workspace.yaml`: tells pnpm which app and package folders belong to the workspace.
- `turbo.json`: defines cacheable build, lint, test, and typecheck tasks.
- `tsconfig.base.json`: strict TypeScript baseline shared by apps and packages.
- `eslint.config.mjs`: root ESLint flat config for modern TypeScript.
- `.prettierrc`: formatting standard used by CI and pre-commit hooks.
- `.editorconfig`: editor-neutral whitespace and newline rules.
- `.gitignore`: excludes dependencies, build outputs, caches, secrets, and local artifacts.
- `.dockerignore`: keeps Docker build contexts small and secret-free.
- `.env.example`: application and service environment variable template.
- `.env.docker.example`: local Docker infrastructure environment template.
- `commitlint.config.cjs`: Conventional Commit enforcement.
- `pyproject.toml`: shared Ruff and pytest configuration for Python services.
- `docker-compose.yml`: local PostgreSQL, Redis, Meilisearch, MinIO, and service orchestration.

## Apps

- `apps/marketing`: Next.js 15 public website for positioning, waitlist, and growth pages.
- `apps/web`: Next.js 15 student workspace for learning, discovery, planning, and alerts.
- `apps/admin`: Next.js 15 internal operations, approval, system health, and super-admin dashboard.
- `apps/mobile`: Flutter mobile app with feature-first student workflows.

Each Next.js app includes:

- `package.json`: isolated app scripts and dependencies.
- `next.config.ts`: strict React mode and workspace package transpilation.
- `postcss.config.mjs`: Tailwind CSS v4 PostCSS integration.
- `tsconfig.json`: app TypeScript configuration.
- `src/app/layout.tsx`: App Router root layout and metadata.
- `src/app/page.tsx`: first production-shaped screen.
- `src/app/globals.css`: design tokens and global styles.

## Packages

- `packages/ui`: shadcn/ui-style shared React primitives.
- `packages/shared`: cross-platform schemas and domain types.
- `packages/api-client`: typed browser API client.
- `packages/config`: shared ESLint, TypeScript, and Tailwind configuration.

## Services

Each service has a `requirements.txt`, `Dockerfile`, `app/main.py`, and `tests/test_health.py`.
The health test ensures every service is importable and exposes a basic operational endpoint.

- `services/backend`: FastAPI API gateway with JWT auth, RBAC dependencies, rate limiting,
  structured logging, SQLAlchemy models, Alembic migrations, and versioned route groups.
- `services/crawler`: crawler job API for opportunity/content ingestion.
- `services/ai-engine`: AI agent registry and recommendation preview API.
- `services/scheduler`: scheduled workflow and notification dispatch API.
- `services/search`: search request/response API designed for Meilisearch-backed discovery.

## Backend Files

- `services/backend/app/main.py`: FastAPI composition root, CORS, rate limits, and router mounting.
- `services/backend/app/api/dependencies/auth.py`: JWT bearer authentication and permission guards.
- `services/backend/app/api/v1/endpoints/*`: versioned route modules for system, auth,
  opportunities, and admin operations.
- `services/backend/app/core/*`: runtime configuration, pagination contracts, and logging.
- `services/backend/app/domain/models/*`: database-backed domain entities and enums.
- `services/backend/app/domain/repositories/*`: repository boundaries for clean architecture.
- `services/backend/app/infrastructure/*`: database session, JWT, and rate-limit adapters.
- `services/backend/app/schemas/*`: Pydantic API request/response models.
- `services/backend/alembic/*`: migration environment and initial production schema.

## Mobile Files

- `apps/mobile/lib/main.dart`: Flutter app composition root with Riverpod and Go Router.
- `apps/mobile/lib/core/config`: environment-derived app configuration.
- `apps/mobile/lib/core/constants`: stable product constants and storage keys.
- `apps/mobile/lib/core/theme`: Material 3 light/dark themes and theme state.
- `apps/mobile/lib/core/services`: app bootstrap, push notification, and biometric services.
- `apps/mobile/lib/core/network`: Dio API client provider.
- `apps/mobile/lib/core/storage`: Hive-backed offline storage.
- `apps/mobile/lib/core/router`: deep-linkable route table.
- `apps/mobile/lib/features/*`: authentication, dashboard, opportunities, notifications, AI,
  planner, profile, and settings screens.
- `apps/mobile/lib/shared/*`: shared mobile widgets and models.

## Admin Files

- `apps/admin/src/app/page.tsx`: enterprise operations overview.
- `apps/admin/src/app/opportunities/page.tsx`: approval and moderation queue.
- `apps/admin/src/app/system/page.tsx`: service health and telemetry dashboard.
- `apps/admin/src/app/super-admin/page.tsx`: governance, RBAC, OAuth, and audit controls.

## Documentation

- `docs/prd`: product requirements and roadmap.
- `docs/architecture`: system architecture, service boundaries, and decision records.
- `docs/database`: database schema, migrations, and data modeling notes.
- `docs/api`: API contracts and integration conventions.
- `docs/ui-ux`: product design system, flows, and accessibility guidance.
- `docs/ai`: AI safety, evaluation, prompts, and model operations.
- `docs/deployment`: deployment, observability, and incident response.

## Common Commands

```bash
pnpm build
pnpm lint
pnpm typecheck
pnpm test
pnpm format:check
dart analyze apps/mobile/lib apps/mobile/test
./scripts/test-python-services.sh
```

## Development Standards

- Use clean architecture boundaries in backend services.
- Keep shared domain contracts in `packages/shared`.
- Generate API clients from OpenAPI before expanding browser client surface area.
- Store secrets outside Git and rotate all local defaults before production.
- Prefer small, independently deployable services with explicit ownership.
- Require CI, code review, typed contracts, and test coverage for production changes.

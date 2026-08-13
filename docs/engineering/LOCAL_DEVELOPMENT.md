# Local Development

## Prerequisites

- Node.js and pnpm
- Python 3.13
- Docker Desktop

## Environment

Copy the safe example file and adjust local-only values as needed:

```bash
cp .env.example .env
```

Do not commit `.env` or real credentials.

## Infrastructure

Start the local PostgreSQL and Redis services:

```bash
docker compose up -d postgres redis
docker compose ps
```

PostgreSQL runs on `localhost:5432` by default. Redis runs on `localhost:6379` by default.

## Backend

Install backend dependencies and run migrations:

```bash
cd services/backend
source .venv/bin/activate
alembic current
alembic upgrade head
```

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

Verify the API:

```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/health/ready
curl http://localhost:8000/api/v1/exams
curl http://localhost:8000/api/v1/opportunities
```

## Tests And Checks

Run backend tests from the repository root:

```bash
pytest services/backend/tests -q
```

Run workspace checks:

```bash
pnpm lint
pnpm typecheck
pnpm build
```

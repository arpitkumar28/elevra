# Elevra

Elevra is a modern career and exam companion platform for students. The foundation here includes a monorepo structure with web, admin, mobile, backend, infrastructure, and documentation scaffolding for future product growth.

## Architecture

- Web app: Next.js App Router
- Admin app: Next.js admin shell
- Mobile app: Flutter
- Backend: FastAPI + SQLAlchemy + Alembic
- Data: PostgreSQL + Redis
- Tooling: pnpm + Turborepo + Docker Compose

## Prerequisites

- Node.js 22+
- pnpm 9+
- Python 3.13+
- Docker Desktop
- Flutter SDK (for mobile app)

## Installation

```bash
pnpm install
```

## Development

```bash
pnpm dev
```

## Backend

```bash
cd services/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Docker

```bash
docker compose up -d
```

## Testing

```bash
pnpm test
cd services/backend && pytest
```

## Environment Variables

Copy [.env.example](.env.example) to .env and adjust values.

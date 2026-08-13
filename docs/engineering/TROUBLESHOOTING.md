# Troubleshooting

## Docker Services

List configured services:

```bash
docker compose config --services
```

Expected services are `postgres` and `redis`.

Start them:

```bash
docker compose up -d postgres redis
docker compose ps
```

## PostgreSQL

If migrations fail, first verify the database container is running and `DATABASE_URL` points to the local PostgreSQL service:

```bash
cd services/backend
source .venv/bin/activate
alembic current
alembic upgrade head
```

Do not drop tables, delete volumes, reset migrations, or downgrade to base while diagnosing connectivity.

## Redis

Verify Redis from the container:

```bash
docker compose exec redis redis-cli ping
docker compose exec redis redis-cli set elevra:health ok ex 60
docker compose exec redis redis-cli get elevra:health
docker compose exec redis redis-cli ttl elevra:health
```

The backend readiness endpoint reports Redis as unavailable if Redis cannot be reached, without exposing credentials.

## Backend Health

Check API liveness:

```bash
curl http://localhost:8000/api/v1/health
```

Check dependency readiness:

```bash
curl http://localhost:8000/api/v1/health/ready
```

The readiness response only reports dependency status and does not expose hosts, usernames, passwords, or URLs.

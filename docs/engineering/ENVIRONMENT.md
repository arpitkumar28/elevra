# Environment

Elevra uses PostgreSQL as the source of truth, Redis for cache, and pgvector inside PostgreSQL for future vector capability.

## Required Variables

- `DATABASE_URL`: SQLAlchemy PostgreSQL URL for the backend and Alembic.
- `POSTGRES_HOST`: local PostgreSQL host, normally `localhost`.
- `POSTGRES_PORT`: local PostgreSQL port, normally `5432`.
- `POSTGRES_DB`: local database name.
- `POSTGRES_USER`: local database user.
- `POSTGRES_PASSWORD`: local development password.
- `REDIS_URL`: Redis connection URL, normally `redis://localhost:6379/0`.
- `JWT_SECRET`: local signing secret. Use a long random value outside examples.
- `ALLOWED_ORIGINS`: comma-separated browser origins allowed by CORS.

## Pooling And Timeouts

- `DB_POOL_SIZE`: number of persistent SQLAlchemy connections.
- `DB_MAX_OVERFLOW`: temporary connections above the pool size.
- `DB_POOL_TIMEOUT`: seconds to wait for a pooled connection.
- `DB_CONNECT_TIMEOUT`: seconds to wait while opening a database connection.

## Secret Handling

`.env.example` contains safe development examples only. Real `.env` files, production credentials, JWT secrets, API keys, and database passwords must stay out of Git.

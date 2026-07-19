# Environments

Elevra is designed for local Docker Compose, then Kubernetes or ECS in production.

## Local

- PostgreSQL, Redis, Meilisearch, and MinIO run from `docker-compose.yml`.
- Python services run as separate containers with independent health checks.
- Next.js apps run on ports `3000`, `3001`, and `3002`.

## Production

- Build each app and service as an independently versioned image.
- Use managed PostgreSQL with point-in-time recovery.
- Use Redis with persistence and multi-AZ failover.
- Use object storage with server-side encryption.
- Use Kubernetes manifests or Terraform modules under `infrastructure/` as the deployment surface evolves.

# Docker Operations

This directory holds Docker-specific operational notes and future deployment assets.

- `docker-compose.yml` at the repository root starts local platform dependencies and Python services.
- Service Dockerfiles live beside each service to keep runtime ownership local.
- Production orchestration should promote these images into Kubernetes, ECS, or another managed runtime.

#!/usr/bin/env bash
# Starts local infrastructure and all JavaScript apps.
set -euo pipefail

docker compose --env-file .env up -d postgres redis meilisearch minio
pnpm dev

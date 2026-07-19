#!/usr/bin/env bash
# Installs workspace dependencies for local development.
set -euo pipefail

pnpm install
echo "Bootstrap complete. Copy .env.example to .env before running Docker Compose."

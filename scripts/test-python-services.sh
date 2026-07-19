#!/usr/bin/env bash
# Runs Python service tests with isolated import paths.
set -euo pipefail

for service in backend crawler ai-engine scheduler search; do
  PYTHONPATH="services/${service}" pytest "services/${service}/tests"
done

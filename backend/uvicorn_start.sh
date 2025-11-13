#!/usr/bin/env bash
set -euo pipefail
uvicorn app.main:app --host 0.0.0.0 --port "${API_PORT:-8080}"

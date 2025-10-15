#!/usr/bin/env bash
set -euo pipefail
export $(grep -v '^#' .env 2>/dev/null | xargs -d '\n' -I {} echo {}) 2>/dev/null || true
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001

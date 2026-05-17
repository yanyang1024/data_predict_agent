#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[dev] starting MariaDB"
docker compose up -d mariadb

echo "[dev] backend: http://127.0.0.1:8000"
(
  cd "$ROOT_DIR"
  export PYTHONPATH="$ROOT_DIR"
  if [ ! -d backend/.venv ]; then python -m venv backend/.venv; fi
  . backend/.venv/bin/activate
  pip install -r backend/requirements.txt
  cp -n backend/.env.example backend/.env || true
  uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
) &
BACKEND_PID=$!

echo "[dev] frontend: http://127.0.0.1:5173"
(
  cd "$ROOT_DIR/frontend"
  npm install
  npm run dev
) &
FRONTEND_PID=$!

trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true' INT TERM EXIT
wait

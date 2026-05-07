#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOST_NAME="${HOST_NAME:-127.0.0.1}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [ -f "$ROOT/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
fi

export BOOKCIRCLE_DB="${BOOKCIRCLE_DB:-sqlite}"

mkdir -p "$ROOT/.pids"

ensure_node_modules() {
  local dir="$1"
  if [ ! -d "$dir/node_modules" ]; then
    (cd "$dir" && npm install)
  fi
}

if [ ! -d "$ROOT/backend/.venv" ]; then
  "$PYTHON_BIN" -m venv "$ROOT/backend/.venv"
fi

REQ_FILE="$ROOT/backend/requirements.txt"
if [ "${BOOKCIRCLE_DB}" = "sqlite" ] && [ -f "$ROOT/backend/requirements-sqlite.txt" ]; then
  REQ_FILE="$ROOT/backend/requirements-sqlite.txt"
fi

"$ROOT/backend/.venv/bin/python" -m pip install -r "$REQ_FILE"

(cd "$ROOT/backend" && ./.venv/bin/python manage.py migrate)

ensure_node_modules "$ROOT/frontend-user"
ensure_node_modules "$ROOT/frontend-admin"

(cd "$ROOT/backend" && ./.venv/bin/python manage.py runserver "$HOST_NAME:8000" > runserver-8000.log 2> runserver-8000.err.log & echo $! > "$ROOT/.pids/django-api.pid")
(cd "$ROOT/backend" && ./.venv/bin/daphne -b "$HOST_NAME" -p 8001 config.asgi:application > daphne-8001.log 2> daphne-8001.err.log & echo $! > "$ROOT/.pids/daphne.pid")
(cd "$ROOT/frontend-user" && npm run dev -- --host "$HOST_NAME" --port 5173 > vite-5173.log 2> vite-5173.err.log & echo $! > "$ROOT/.pids/frontend-user.pid")
(cd "$ROOT/frontend-admin" && npm run dev -- --host "$HOST_NAME" --port 5174 > vite-5174.log 2> vite-5174.err.log & echo $! > "$ROOT/.pids/frontend-admin.pid")

echo ""
echo "BookCircle is running:"
echo "  User:  http://localhost:5173/"
echo "  Admin: http://localhost:5174/login"
echo "  API:   http://$HOST_NAME:8000"
echo "  WS:    ws://$HOST_NAME:8001"
echo ""
echo "Stop with: ./Stop-BookCircle-Mac.sh"

#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_DIR="$ROOT/.pids"

if [ ! -d "$PID_DIR" ]; then
  echo "No BookCircle PID directory found."
  exit 0
fi

for file in "$PID_DIR"/*.pid; do
  [ -e "$file" ] || continue
  pid="$(cat "$file")"
  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
    echo "Stopping PID $pid"
    kill "$pid" 2>/dev/null || true
  fi
done

echo "BookCircle stop signal sent."

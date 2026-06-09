#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# shellcheck source=scripts/lib.sh
. scripts/lib.sh
load_env
PAPERCLIP_DIR="$(expand_path "${PAPERCLIP_DIR:-$HOME/paperclip}")"

pkill -f "paperclip" 2>/dev/null || true
pkill -f "tsx.*src/index" 2>/dev/null || true
sleep 1

cd "$PAPERCLIP_DIR"
echo "Starting Paperclip on http://0.0.0.0:3100 ..."
nohup pnpm dev:once > "$HOME/paperclip-home.log" 2>&1 &

for i in $(seq 1 60); do
  if curl -fsS http://localhost:3100/api/health >/dev/null 2>&1; then
    echo "Paperclip is healthy:"
    curl -sS http://localhost:3100/api/health | jq .
    exit 0
  fi
  sleep 2
done

echo "Paperclip did not become healthy. Last log lines:" >&2
tail -80 "$HOME/paperclip-home.log" >&2 || true
exit 1

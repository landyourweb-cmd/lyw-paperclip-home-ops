#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# shellcheck source=scripts/lib.sh
. scripts/lib.sh
load_env

PAPERCLIP_REPO="${PAPERCLIP_REPO:-https://github.com/landyourweb-cmd/paperclip.git}"
PAPERCLIP_DIR="$(expand_path "${PAPERCLIP_DIR:-$HOME/paperclip}")"

mkdir -p "$(dirname "$PAPERCLIP_DIR")"
if [ ! -d "$PAPERCLIP_DIR/.git" ]; then
  git clone "$PAPERCLIP_REPO" "$PAPERCLIP_DIR"
else
  git -C "$PAPERCLIP_DIR" pull --ff-only || true
fi

cd "$PAPERCLIP_DIR"
corepack enable
pnpm install

CONFIG_FILE="$HOME/.paperclip/instances/default/config.json"
mkdir -p "$(dirname "$CONFIG_FILE")"
cat > "$CONFIG_FILE" <<JSON
{
  "\$meta": { "version": 1, "updatedAt": "$(date -Iseconds)", "source": "lyw-paperclip-home-ops" },
  "database": {
    "mode": "embedded-postgres",
    "backup": { "enabled": true, "intervalMinutes": 60, "retentionDays": 14, "dir": "$HOME/.paperclip/instances/default/data/backups" }
  },
  "logging": { "mode": "file", "logDir": "$HOME/.paperclip/instances/default/logs" },
  "server": {
    "deploymentMode": "local_trusted",
    "exposure": "private",
    "bind": "lan",
    "host": "0.0.0.0",
    "port": 3100,
    "serveUi": true,
    "allowedHostnames": []
  },
  "auth": { "baseUrlMode": "auto", "disableSignUp": true },
  "storage": { "provider": "local_disk", "localDisk": { "baseDir": "$HOME/.paperclip/instances/default/data/storage" } },
  "telemetry": { "enabled": true },
  "secrets": { "provider": "local_encrypted", "strictMode": false, "localEncrypted": { "keyFilePath": "$HOME/.paperclip/instances/default/secrets/master.key" } }
}
JSON

mkdir -p "$HOME/.paperclip/instances/default/secrets" "$HOME/.paperclip/instances/default/logs"
echo "Paperclip installed at $PAPERCLIP_DIR"
echo "Config written to $CONFIG_FILE"

#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update
sudo apt-get install -y \
  ca-certificates curl git jq build-essential python3 python3-venv python3-pip \
  openssh-client openssh-server sqlite3

if ! command -v node >/dev/null 2>&1; then
  curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
  sudo apt-get install -y nodejs
fi

corepack enable
corepack prepare pnpm@9.15.4 --activate

sudo systemctl enable --now ssh || true

echo "Prereqs ready: node=$(node -v), pnpm=$(pnpm -v)"

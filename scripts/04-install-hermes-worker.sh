#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# shellcheck source=scripts/lib.sh
. scripts/lib.sh
load_env

sudo apt-get update
sudo apt-get install -y ca-certificates curl git python3 python3-venv python3-pip openssh-server build-essential
sudo systemctl enable --now ssh

if ! command -v hermes >/dev/null 2>&1; then
  echo "Installing Hermes Agent runtime..."
  curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
else
  echo "Hermes already installed: $(command -v hermes)"
fi

WORKSPACE="$(expand_path "${WORK_REMOTE_WORKSPACE:-$HOME/lyw-workspace}")"
mkdir -p "$WORKSPACE"

cat <<INFO
Worker prepared.

Next steps:
1. Ensure this machine is reachable from the home PC over LAN or Tailscale.
2. Add the home PC SSH public key to:
   $HOME/.ssh/authorized_keys
3. From the home PC, test SSH and run:
   python3 scripts/05-register-work-ceo-env.py

Local checks:
- SSH: systemctl status ssh --no-pager
- Hermes: hermes doctor
- Workspace: $WORKSPACE
INFO

# Land Your Web Paperclip Home Ops

Minimal Paperclip deployment for the **Land Your Web** agent company.

## Target topology

```text
HOME PC
├─ Paperclip control plane: http://0.0.0.0:3100
├─ Land Your Web company
├─ MERCURY agent runtime/default environment: home-local
└─ Database/storage: local Paperclip instance data

WORK CELERON
└─ OVERLORD / CEO runtime exposed to the home Paperclip control plane over SSH/Tailscale
```

Railway is intentionally out. This is designed for cheap, private, operator-owned infrastructure.

## Assumptions

- Home PC runs Ubuntu 24.04 or WSL2 Ubuntu 24.04.
- Work Celeron runs Ubuntu 24.04.
- Machines see each other over LAN or Tailscale.
- Paperclip source repo is `https://github.com/landyourweb-cmd/paperclip.git`.
- Do **not** expose `local_trusted` Paperclip to the public internet. Use LAN/Tailscale only.

## Fast path on the home PC

```bash
git clone https://github.com/landyourweb-cmd/lyw-paperclip-home-ops.git
cd lyw-paperclip-home-ops
cp .env.example .env
nano .env
bash scripts/00-install-prereqs.sh
bash scripts/01-install-paperclip-home.sh
bash scripts/02-start-paperclip-home.sh
python3 scripts/03-seed-basic-company.py
```

Then open:

```text
http://localhost:3100
```

## Fast path on the work Celeron

```bash
git clone https://github.com/landyourweb-cmd/lyw-paperclip-home-ops.git
cd lyw-paperclip-home-ops
cp .env.example .env
nano .env
bash scripts/04-install-hermes-worker.sh
```

After SSH/Tailscale is reachable from home PC, run this on the **home PC**:

```bash
python3 scripts/05-register-work-ceo-env.py
```

## What gets seeded

Company:

- `Land Your Web LLC`
- budget: `$0/month` until we deliberately activate spend

Agents:

- `OVERLORD` — CEO, intended to run on the work Celeron
- `MERCURY` — CMO, intended to run on the home PC

## Safety model

- `local_trusted` mode is okay only on private networks.
- Prefer Tailscale for home↔work connectivity.
- Keep monthly budget at zero until the board explicitly activates work.
- No API keys or private SSH keys belong in this repo.

#!/usr/bin/env python3
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE = os.getenv("PAPERCLIP_URL", "http://localhost:3100").rstrip("/")
COMPANY_NAME = os.getenv("PAPERCLIP_COMPANY_NAME", "Land Your Web LLC")
WORK_ENV_NAME = os.getenv("WORK_ENV_NAME", "work-celeron-ceo")
WORK_SSH_HOST = os.getenv("WORK_SSH_HOST", "").strip()
WORK_SSH_PORT = int(os.getenv("WORK_SSH_PORT", "22"))
WORK_SSH_USER = os.getenv("WORK_SSH_USER", "automation")
WORK_REMOTE_WORKSPACE = os.getenv("WORK_REMOTE_WORKSPACE", "/home/automation/lyw-workspace")
WORK_SSH_KEY_PATH = os.path.expandvars(os.path.expanduser(os.getenv("WORK_SSH_KEY_PATH", "~/.ssh/lyw_paperclip_ceo")))

if not WORK_SSH_HOST or WORK_SSH_HOST.startswith("CHANGE_ME"):
    raise SystemExit("Set WORK_SSH_HOST in .env first. Use the Celeron's Tailscale IP/DNS or LAN IP.")


def req(method, path, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    r = urllib.request.Request(BASE + path, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            body = resp.read().decode()
            return json.loads(body) if body else None
    except urllib.error.HTTPError as e:
        print(e.read().decode(), file=sys.stderr)
        raise


def main():
    key_path = Path(WORK_SSH_KEY_PATH)
    pub_path = Path(str(key_path) + ".pub")
    if not key_path.exists():
        raise SystemExit(f"SSH private key not found: {key_path}\nGenerate one with: ssh-keygen -t ed25519 -f {key_path} -C lyw-paperclip-ceo")
    if not pub_path.exists():
        raise SystemExit(f"SSH public key not found: {pub_path}")

    companies = req("GET", "/api/companies")
    company = next((c for c in companies if c["name"] == COMPANY_NAME), None)
    if not company:
        raise SystemExit(f"Company not found: {COMPANY_NAME}. Run scripts/03-seed-basic-company.py first.")
    company_id = company["id"]

    envs = req("GET", f"/api/companies/{company_id}/environments")
    existing = next((e for e in envs if e["name"] == WORK_ENV_NAME), None)
    payload = {
        "name": WORK_ENV_NAME,
        "description": "Work Celeron SSH runtime for OVERLORD / CEO.",
        "driver": "ssh",
        "status": "active",
        "config": {
            "host": WORK_SSH_HOST,
            "port": WORK_SSH_PORT,
            "username": WORK_SSH_USER,
            "remoteWorkspacePath": WORK_REMOTE_WORKSPACE,
            "privateKey": key_path.read_text(),
            "knownHosts": None,
            "strictHostKeyChecking": False
        },
        "metadata": {"role": "work-ceo-worker", "managedBy": "lyw-paperclip-home-ops"},
    }
    if existing:
        env = req("PATCH", f"/api/environments/{existing['id']}", payload)
    else:
        env = req("POST", f"/api/companies/{company_id}/environments", payload)

    agents = req("GET", f"/api/companies/{company_id}/agents")
    overlord = next((a for a in agents if a["name"] == "OVERLORD"), None)
    if not overlord:
        raise SystemExit("OVERLORD agent not found. Run seed script first.")
    req("PATCH", f"/api/agents/{overlord['id']}", {"defaultEnvironmentId": env["id"]})

    print(json.dumps({
        "companyId": company_id,
        "workEnvironment": {"id": env["id"], "name": env["name"], "host": WORK_SSH_HOST},
        "overlord": {"id": overlord["id"], "defaultEnvironmentId": env["id"]},
        "publicKeyToAuthorizeOnCeleron": pub_path.read_text().strip(),
    }, indent=2))

if __name__ == "__main__":
    main()

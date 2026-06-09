#!/usr/bin/env python3
import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.getenv("PAPERCLIP_URL", "http://localhost:3100").rstrip("/")
COMPANY_NAME = os.getenv("PAPERCLIP_COMPANY_NAME", "Land Your Web LLC")
ISSUE_PREFIX = os.getenv("PAPERCLIP_ISSUE_PREFIX", "LAN")
HOME_ENV_NAME = os.getenv("HOME_ENV_NAME", "home-pc-local")
HOME_WORKSPACE_PATH = os.path.expandvars(os.path.expanduser(os.getenv("HOME_WORKSPACE_PATH", "~/lyw-workspace")))


def req(method, path, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    r = urllib.request.Request(
        BASE + path,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            body = resp.read().decode()
            return json.loads(body) if body else None
    except urllib.error.HTTPError as e:
        print(e.read().decode(), file=sys.stderr)
        raise


def get_or_create_company():
    companies = req("GET", "/api/companies")
    for c in companies:
        if c["name"] == COMPANY_NAME:
            return c
    return req("POST", "/api/companies", {
        "name": COMPANY_NAME,
        "issuePrefix": ISSUE_PREFIX,
        "budgetMonthlyCents": 0,
        "status": "active",
    })


def get_or_create_env(company_id):
    envs = req("GET", f"/api/companies/{company_id}/environments")
    for e in envs:
        if e["name"] == HOME_ENV_NAME:
            return e
    # Paperclip currently allows only one local environment per company.
    # Reuse the built-in local environment if it already exists under another name.
    for e in envs:
        if e.get("driver") == "local" and e.get("status") != "archived":
            return e
    return req("POST", f"/api/companies/{company_id}/environments", {
        "name": HOME_ENV_NAME,
        "description": "Home PC local runtime for MERCURY and board-side tasks.",
        "driver": "local",
        "status": "active",
        "config": {},
        "metadata": {"role": "home-control-plane"},
    })


def get_or_create_agent(company_id, name, role, title, reports_to=None, default_environment_id=None):
    agents = req("GET", f"/api/companies/{company_id}/agents")
    for a in agents:
        if a["name"] == name:
            patch = {}
            if default_environment_id and a.get("defaultEnvironmentId") != default_environment_id:
                patch["defaultEnvironmentId"] = default_environment_id
            if reports_to is not None and a.get("reportsTo") != reports_to:
                patch["reportsTo"] = reports_to
            if patch:
                return req("PATCH", f"/api/agents/{a['id']}", patch)
            return a
    payload = {
        "name": name,
        "role": role,
        "title": title,
        "adapterType": "hermes_local",
        "adapterConfig": {},
        "reportsTo": reports_to,
        "defaultEnvironmentId": default_environment_id,
        "budgetMonthlyCents": 0,
        "capabilities": ["strategy", "execution", "operations"] if role == "ceo" else ["gtm", "outreach", "pipeline"],
        "metadata": {"seededBy": "lyw-paperclip-home-ops"},
    }
    return req("POST", f"/api/companies/{company_id}/agents", payload)


def main():
    print(f"Using Paperclip: {BASE}")
    health = req("GET", "/api/health")
    print("Health:", health.get("status"), health.get("version"), health.get("deploymentMode"))
    os.makedirs(HOME_WORKSPACE_PATH, exist_ok=True)
    company = get_or_create_company()
    env = get_or_create_env(company["id"])
    overlord = get_or_create_agent(company["id"], "OVERLORD", "ceo", "CEO / Operator", None, None)
    mercury = get_or_create_agent(company["id"], "MERCURY", "cmo", "CMO / Pipeline Operator", overlord["id"], env["id"])
    org = req("GET", f"/api/companies/{company['id']}/org")
    print(json.dumps({
        "company": {"id": company["id"], "name": company["name"]},
        "homeEnvironment": {"id": env["id"], "name": env["name"]},
        "agents": {"OVERLORD": overlord["id"], "MERCURY": mercury["id"]},
        "org": org,
    }, indent=2))

if __name__ == "__main__":
    main()

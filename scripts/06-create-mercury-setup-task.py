#!/usr/bin/env python3
"""Create the MERCURY setup mission in Paperclip.

Run from the Paperclip control-plane machine:

    cd lyw-paperclip-home-ops
    python3 scripts/06-create-mercury-setup-task.py

The script is intentionally idempotent-ish: if an issue with the same exact title
already exists, it reuses it instead of creating duplicates.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = os.getenv("PAPERCLIP_URL", "http://localhost:3100").rstrip("/")
COMPANY_NAME = os.getenv("PAPERCLIP_COMPANY_NAME", "Land Your Web LLC")
OVERLORD_NAME = os.getenv("OVERLORD_AGENT_NAME", "OVERLORD")
MERCURY_NAME = os.getenv("MERCURY_AGENT_NAME", "MERCURY")
WORK_ENV_NAME = os.getenv("WORK_ENV_NAME", "work-celeron-ceo")
WORK_REMOTE_WORKSPACE = os.getenv("WORK_REMOTE_WORKSPACE", "/home/automation/lyw-workspace")


def req(method, path, payload=None, timeout=30):
    data = None if payload is None else json.dumps(payload).encode()
    r = urllib.request.Request(
        BASE + path,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            body = resp.read().decode()
            return json.loads(body) if body else None
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} {method} {path}", file=sys.stderr)
        print(e.read().decode(), file=sys.stderr)
        raise


def find_company():
    companies = req("GET", "/api/companies")
    company = next((c for c in companies if c.get("name") == COMPANY_NAME), None)
    if not company:
        raise SystemExit(f"Company not found: {COMPANY_NAME}. Run scripts/03-seed-basic-company.py first.")
    return company


def list_all_issues(company_id):
    qs = urllib.parse.urlencode({"limit": 200})
    result = req("GET", f"/api/companies/{company_id}/issues?{qs}")
    if isinstance(result, dict):
        for key in ("issues", "items", "data", "results"):
            if isinstance(result.get(key), list):
                return result[key]
    if isinstance(result, list):
        return result
    return []


def find_issue_by_title(company_id, title):
    return next((i for i in list_all_issues(company_id) if i.get("title") == title), None)


def create_issue(company_id, payload):
    existing = find_issue_by_title(company_id, payload["title"])
    if existing:
        return existing
    return req("POST", f"/api/companies/{company_id}/issues", payload)


def main():
    print(f"Using Paperclip: {BASE}")
    health = req("GET", "/api/health")
    print("Health:", health.get("status"), health.get("version"), health.get("deploymentMode"))

    company = find_company()
    company_id = company["id"]

    agents = req("GET", f"/api/companies/{company_id}/agents")
    overlord = next((a for a in agents if a.get("name") == OVERLORD_NAME), None)
    mercury = next((a for a in agents if a.get("name") == MERCURY_NAME), None)
    if not overlord:
        raise SystemExit(f"Agent not found: {OVERLORD_NAME}. Run seed scripts first.")
    if not mercury:
        raise SystemExit(f"Agent not found: {MERCURY_NAME}. Run seed scripts first.")

    envs = req("GET", f"/api/companies/{company_id}/environments")
    work_env = next((e for e in envs if e.get("name") == WORK_ENV_NAME), None)

    common = {
        "assigneeAgentId": overlord["id"],
        "priority": "high",
        "status": "todo",
        "workMode": "standard",
        "requestDepth": 0,
    }
    if work_env:
        common.update({
            "executionWorkspacePreference": "reuse_existing",
            "executionWorkspaceSettings": {
                "mode": "reuse_existing",
                "environmentId": work_env["id"],
                "cwd": WORK_REMOTE_WORKSPACE,
            },
        })

    parent_title = "Setup MERCURY as LYW GTM operator"
    parent_description = f"""# Mission
Set up MERCURY as Land Your Web's GTM operator inside Paperclip so it can produce one qualified US-market client opportunity per month minimum, with a realistic path to one client/week later.

# Context
- Company: Land Your Web LLC
- Budget constraint: $200/month external tooling budget
- Market: USA
- Sales assumption: Stefan closes ~20% of qualified calls for planning purposes
- Current architecture: Home PC Paperclip control plane, Celeron worker node over Tailscale, OVERLORD assigned to `{WORK_ENV_NAME}`
- MERCURY exists as the pipeline/GTM agent and should report to OVERLORD

# Required output artifacts
Create these files under `{WORK_REMOTE_WORKSPACE}/mercury-setup/`:
1. `MERCURY_AGENTS.md` — final operating instructions for MERCURY
2. `prompt-pack.md` — reusable prompts for sourcing, enrichment, scoring, outreach, follow-up, objections, and weekly reporting
3. `gtm-operating-system.md` — full GTM workflow: ICP → sourcing → enrichment → scoring → outreach → follow-up → CRM hygiene → reporting
4. `lead-schema.csv` — CSV header/template for MERCURY lead tracking
5. `weekly-runbook.md` — exact Monday-Friday execution cadence
6. `qa-checklist.md` — Reality Checker gate for MERCURY output quality
7. `handoff-to-stefan.md` — what Stefan sees daily/weekly and when he must intervene

# Prompting techniques MERCURY must use
MERCURY's instructions must explicitly use:
- Role + mission framing: who MERCURY is, what winning means, what it must never do
- Context packing: include company, ICP, offer, constraints, and prior results before every task
- Decomposition: split every GTM run into sourcing, enrichment, scoring, personalization, sending, follow-up, and reporting
- Chain-of-verification: verify website, relevance, decision-maker role, pain signal, and contact quality before scoring a lead
- Rubric scoring: use a 100-point lead score with clear thresholds
- Few-shot examples: include at least 3 good lead examples and 3 reject examples
- Critic pass: after drafting any outbound copy, run a brutal self-review for generic claims, weak personalization, compliance risk, and unclear CTA
- Output contracts: every prompt must specify exact JSON/CSV/Markdown shape
- Stop conditions: do not invent emails, do not contact poor-fit companies, do not exceed budget/tools, escalate blocked data access
- Memory discipline: retain durable ICP/offer lessons; do not retain stale per-lead task state as long-term memory

# Definition of done
- MERCURY has a clear role, permissions, operating cadence, prompt pack, and QA checklist
- The workflow can run with $200/month or less
- The plan can source at least 25 qualified leads/month, aiming for 5 sales calls/month and 1 close/month at 20% close rate
- Every artifact is concrete enough that another agent can execute without asking Stefan vague questions
- OVERLORD leaves a final summary comment on this issue with paths to all created artifacts
"""

    parent = create_issue(company_id, {
        **common,
        "title": parent_title,
        "description": parent_description,
    })

    child_specs = [
        (
            "MERCURY setup 01 — Audit current Paperclip GTM org and runtime",
            """Inspect current Paperclip company state: agents, environments, workspaces, MERCURY record, OVERLORD record, and runtime constraints. Verify whether MERCURY is assigned to the correct home/local environment and whether OVERLORD can supervise from the Celeron. Output `01-runtime-audit.md` with facts, gaps, and fixes. Do not guess IDs; inspect live state.

Prompting technique: begin with a context inventory prompt. List knowns, unknowns, retrieval actions, and verification commands before proposing changes.""",
        ),
        (
            "MERCURY setup 02 — Define ICP and reject criteria",
            """Create `02-icp-and-rejects.md`. Define the initial US ICP for LYW with concrete filters: company type, size, geography, buying triggers, current site symptoms, tech signals, budget likelihood, urgency, and disqualifiers. Include 3 strong-fit examples and 3 bad-fit examples.

Prompting technique: use contrastive few-shot prompting. For every fit criterion, include what good looks like and what a false positive looks like.""",
        ),
        (
            "MERCURY setup 03 — Package the offer and angle matrix",
            """Create `03-offer-angle-matrix.md`. Translate LYW's packages into outbound-ready hooks. Include Foundation/Growth/Dominance positioning, pain-specific angles, proof points, CTAs, objection handling, and what NOT to promise.

Prompting technique: use audience-angle-message decomposition. For each ICP segment produce: pain, trigger, message, proof, CTA, risk, and compliance notes.""",
        ),
        (
            "MERCURY setup 04 — Build lead sourcing workflow under $200/month",
            """Create `04-lead-sourcing-workflow.md`. Specify exact lead sources, queries, search strings, weekly quotas, dedupe rules, and free/cheap tools. Must work within $200/month. Include manual fallback and automation path.

Prompting technique: use source triangulation. A lead is not qualified from one source alone; require website + business directory/social profile + contact source where possible.""",
        ),
        (
            "MERCURY setup 05 — Build enrichment and verification workflow",
            """Create `05-enrichment-verification.md`. Define what data MERCURY must collect, how to verify it, how to avoid hallucinated contacts, and how to record confidence. Include a CSV schema and data quality statuses.

Prompting technique: use chain-of-verification. Every enriched field gets evidence_url, confidence, and verification_note.""",
        ),
        (
            "MERCURY setup 06 — Build 100-point lead scoring rubric",
            """Create `06-lead-scoring-rubric.md`. Build a 100-point rubric with categories for fit, pain, urgency, budget, accessibility, personalization potential, and timing. Define thresholds: reject, nurture, outbound, priority outbound.

Prompting technique: use rubric-first prompting. MERCURY must score before writing outreach, and every score requires a one-sentence evidence-backed justification.""",
        ),
        (
            "MERCURY setup 07 — Create outbound prompt pack",
            """Create `07-outbound-prompt-pack.md`. Include reusable prompts for first email, follow-ups, LinkedIn DM, website roast teaser, loom/script outline, objection reply, breakup email, and daily report. Each prompt must have strict output format and critic pass.

Prompting technique: use draft → critique → rewrite. Require MERCURY to reject generic copy and regenerate until it includes a specific observed trigger.""",
        ),
        (
            "MERCURY setup 08 — Create weekly operating cadence and Stefan handoff",
            """Create `08-weekly-cadence-handoff.md`. Define Monday-Friday cadence, daily numbers, weekly report, escalation triggers, and when Stefan must review/call/close. Include a dashboard-style status format.

Prompting technique: use management-by-exception prompting. MERCURY should only escalate decisions that require human judgment: offer exceptions, high-value accounts, unclear compliance, or booked-call prep.""",
        ),
        (
            "MERCURY setup 09 — Assemble final MERCURY_AGENTS.md and QA gate",
            """Create final `MERCURY_AGENTS.md`, `prompt-pack.md`, `gtm-operating-system.md`, `weekly-runbook.md`, `lead-schema.csv`, `qa-checklist.md`, and `handoff-to-stefan.md`. Run a self-QA pass against the parent definition of done and leave a final issue comment with artifact paths and remaining risks.

Prompting technique: use contract verification. Before completion, compare every required artifact against the issue's output contract and mark PASS/FAIL with evidence.""",
        ),
    ]

    children = []
    previous = None
    for title, description in child_specs:
        payload = {
            **common,
            "title": title,
            "description": description,
            "parentId": parent["id"],
        }
        if previous:
            payload["blockedByIssueIds"] = [previous["id"]]
        issue = create_issue(company_id, payload)
        children.append(issue)
        previous = issue

    print(json.dumps({
        "company": {"id": company_id, "name": company["name"]},
        "assignee": {"id": overlord["id"], "name": overlord["name"]},
        "mercury": {"id": mercury["id"], "name": mercury["name"]},
        "environment": {"id": work_env["id"], "name": work_env["name"]} if work_env else None,
        "parent": {"id": parent["id"], "identifier": parent.get("identifier"), "title": parent["title"]},
        "children": [
            {"id": c["id"], "identifier": c.get("identifier"), "title": c["title"]}
            for c in children
        ],
    }, indent=2))


if __name__ == "__main__":
    main()

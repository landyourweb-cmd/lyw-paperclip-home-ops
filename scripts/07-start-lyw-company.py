#!/usr/bin/env python3
"""Start Land Your Web's Paperclip company with a concrete 30-day GTM goal.

This script is idempotent-ish: it reuses existing goals/issues by exact title and
only creates missing launch work. It also raises Paperclip budgets to the user's
approved $200/month cap so the org is no longer just "hot but paused".
"""

from __future__ import annotations

import os
import sys
from typing import Any

import requests

PAPERCLIP_URL = os.environ.get("PAPERCLIP_URL", "http://localhost:3100").rstrip("/")
API = f"{PAPERCLIP_URL}/api"
COMPANY_ID = os.environ.get("PAPERCLIP_COMPANY_ID", "5ed6c76b-39a8-46ca-b0b3-127326fe887c")
COMPANY_BUDGET_CENTS = int(os.environ.get("LYW_COMPANY_BUDGET_CENTS", "20000"))
AGENT_BUDGET_CENTS = int(os.environ.get("LYW_AGENT_BUDGET_CENTS", "10000"))

GOAL_TITLE = "Win at least 1 new USA client for Land Your Web every month"


def req(method: str, path: str, **kwargs: Any) -> Any:
    url = f"{API}{path}"
    r = requests.request(method, url, timeout=20, **kwargs)
    if r.status_code >= 400:
        raise SystemExit(f"{method} {url} failed {r.status_code}: {r.text}")
    if not r.text:
        return None
    return r.json()


def find_agent(name: str) -> dict[str, Any]:
    agents = req("GET", f"/companies/{COMPANY_ID}/agents")
    for agent in agents:
        if agent.get("name", "").lower() == name.lower():
            return agent
    raise SystemExit(f"Agent not found: {name}")


def get_or_create_goal(overlord_id: str) -> dict[str, Any]:
    goals = req("GET", f"/companies/{COMPANY_ID}/goals")
    for goal in goals:
        if goal.get("title") == GOAL_TITLE:
            return goal
    return req(
        "POST",
        f"/companies/{COMPANY_ID}/goals",
        json={
            "title": GOAL_TITLE,
            "level": "company",
            "status": "active",
            "ownerAgentId": overlord_id,
            "description": "30-day GTM command goal: use a $200/month budget cap to create enough qualified USA pipeline to close at least 1 new LYW client/month at a 20% close-rate assumption. Required operating math: 5 qualified sales calls/month, 25+ qualified leads/month minimum, daily growth execution by MERCURY, command/QA/org decisions by OVERLORD.",
        },
    )


def list_issues() -> list[dict[str, Any]]:
    data = req("GET", f"/companies/{COMPANY_ID}/issues")
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("items", "issues", "data"):
            if isinstance(data.get(key), list):
                return data[key]
    return []


def issue_exists(title: str) -> dict[str, Any] | None:
    for issue in list_issues():
        if issue.get("title") == title:
            return issue
    return None


def create_issue(title: str, description: str, assignee: str, goal_id: str, priority: str = "high") -> dict[str, Any]:
    existing = issue_exists(title)
    if existing:
        return existing
    return req(
        "POST",
        f"/companies/{COMPANY_ID}/issues",
        json={
            "title": title,
            "description": description,
            "goalId": goal_id,
            "priority": priority,
            "assigneeAgentId": assignee,
            "workMode": "standard",
            "billingCode": "LYW-GTM-30D",
        },
    )


def main() -> None:
    health = req("GET", "/health")
    print(f"Paperclip: {health.get('status')} v{health.get('version')} @ {PAPERCLIP_URL}")

    overlord = find_agent("OVERLORD")
    mercury = find_agent("MERCURY")
    print(f"OVERLORD: {overlord['id']} ({overlord.get('adapterType')})")
    print(f"MERCURY:   {mercury['id']} ({mercury.get('adapterType')})")

    company = req("PATCH", f"/companies/{COMPANY_ID}", json={"budgetMonthlyCents": COMPANY_BUDGET_CENTS})
    print(f"Company budget cap: ${company.get('budgetMonthlyCents', 0) / 100:.2f}/month")

    for agent in (overlord, mercury):
        patched = req("PATCH", f"/agents/{agent['id']}", json={"budgetMonthlyCents": AGENT_BUDGET_CENTS})
        print(f"Agent budget cap: {patched['name']} = ${patched.get('budgetMonthlyCents', 0) / 100:.2f}/month")

    goal = get_or_create_goal(overlord["id"])
    print(f"Goal: {goal.get('title')} [{goal.get('status')}] {goal.get('id')}")

    issues = []

    issues.append(create_issue(
        "OVERLORD command: start LYW 30-day GTM operating cadence",
        """Mission: activate the company around the 30-day revenue goal.

Objective:
- Coordinate MERCURY and any needed specialist agents to produce at least 5 qualified USA sales calls/month and close at least 1 client/month at the assumed 20% close rate.

Your first output must include:
1. Command summary: Win / Bottleneck / Decision / Next Moves.
2. Cost-benefit read on the $200/month cap.
3. Daily operating cadence for OVERLORD + MERCURY.
4. Marketing specialist hiring/firing decision framework for the first 30 days.
5. The specific metrics MERCURY must report daily and weekly.
6. Any blockers that require Stefan.

Operating style:
- Act autonomously on reversible low-risk actions.
- Escalate only for self-destruction, human harm, irreversible catastrophes, illegal/unethical actions, or spend outside budget.
- Be ruthless with vague work and weak agent output.
""".strip(),
        overlord["id"],
        goal["id"],
        "critical",
    ))

    issues.append(create_issue(
        "MERCURY sprint: create first 100-lead USA GTM target list",
        """Mission: create the first qualified USA pipeline sprint for Land Your Web.

Budget constraint:
- Assume total company budget cap is $200/month.
- Prefer free/cheap sources first.

Required output:
1. Define 2-3 sharp ICP slices for fastest close probability.
2. Source 100 potential USA leads/prospects or, if tooling is unavailable, produce the exact lead-source queries and spreadsheet schema to generate them.
3. Enrich each lead with company URL, decision-maker role, trigger/event, personalization angle, and source URL.
4. Score leads with a 100-point rubric.
5. Select top 25 for first outreach.
6. Produce first-touch + 3 follow-up sequence.
7. Report expected reply/call math needed for 1 client/month.

Daily question:
- How can we do this more, better, or cheaper?

Reminder:
- No fake data. No fake proof. No high-volume outreach before deliverability and message QA.
""".strip(),
        mercury["id"],
        goal["id"],
        "critical",
    ))

    issues.append(create_issue(
        "MERCURY sprint: build proof and case-study content engine",
        """Mission: turn every Land Your Web proof asset into pipeline fuel.

Required output:
1. Inventory available proof: LYW site rebuild, before/after visuals, speed of delivery, packages, internal SOPs, Stefan's referral close-rate story if approved.
2. Produce 10 case-study/content angles.
3. Draft 5 LinkedIn posts.
4. Draft 3 cold-outreach proof snippets.
5. Draft 3 landing-page proof sections.
6. Create 5 GPT Image 2-ready creative briefs/prompts for visuals.
7. Mark which claims need Stefan approval or more evidence before publishing.

Doctrine:
- Be bubbly with the market, brutal with the metrics.
- Every proof asset should become content, trust, calls, cash, and louder proof.
""".strip(),
        mercury["id"],
        goal["id"],
        "high",
    ))

    issues.append(create_issue(
        "MERCURY experiment: propose 7 cheap growth plays under $200/month",
        """Mission: design the first growth experiment backlog.

Required output:
Create 7 experiments across content, outbound, inbound, paid acquisition, influencers, referrals, and affiliates.

Each experiment must include:
- Channel
- Audience
- Hypothesis
- Creative/message
- Cost
- Expected upside
- Risk
- Success metric
- Minimum test size
- Kill / iterate / scale rule
- Owner
- Deadline

Prioritize cheap experiments closest to booked calls.
Discuss any recommended specialist agent hire/fire decisions with OVERLORD before execution.
""".strip(),
        mercury["id"],
        goal["id"],
        "high",
    ))

    print("\nSeeded / reused issues:")
    for issue in issues:
        print(f"- {issue.get('identifier', issue.get('id'))}: {issue.get('title')} → {issue.get('status')} assigned={issue.get('assigneeAgentId')}")

    print("\nActivation complete. Creating assigned issues should queue agent wakeups in Paperclip.")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.RequestException as exc:
        print(f"Network/API error: {exc}", file=sys.stderr)
        sys.exit(1)

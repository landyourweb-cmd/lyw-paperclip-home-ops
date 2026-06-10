#!/usr/bin/env python3
"""Pivot Land Your Web Paperclip company from agency-client GTM to AI SaaS venture creation.

Constraints from Stefan:
- $0 cash budget inside Paperclip.
- Use only existing Codex Pro plan tokens / compute already paid for.
- Land Your Web is the legal structure, not the thing being sold as web-dev services.
- Avoid products that require Stefan to sit on sales calls.
- Identify, validate, build, and market an AI-first SaaS with healthy gross margins.
"""

from __future__ import annotations

import os
import sys
from typing import Any

import requests

BASE_URL = os.environ.get("PAPERCLIP_URL", "http://localhost:3100/api").rstrip("/")
COMPANY_ID = os.environ.get("PAPERCLIP_COMPANY_ID", "5ed6c76b-39a8-46ca-b0b3-127326fe887c")
OVERLORD_ID = os.environ.get("PAPERCLIP_OVERLORD_ID", "6157f129-806c-4eb7-a18b-6ba34af1eeb4")
MERCURY_ID = os.environ.get("PAPERCLIP_MERCURY_ID", "334ae144-cd5f-4216-b10f-3fbd0b207f3b")
ZERO_BUDGET = 0

OLD_GTM_TITLES = {
    "OVERLORD command: start LYW 30-day GTM operating cadence",
    "MERCURY sprint: create first 100-lead USA GTM target list",
    "MERCURY sprint: build proof and case-study content engine",
    "MERCURY experiment: propose 7 cheap growth plays under $200/month",
}

ROOT_GOAL_TITLE = "Create and launch a profitable AI-first SaaS company under Land Your Web"


def req(method: str, path: str, **kwargs: Any) -> Any:
    url = f"{BASE_URL}{path}"
    response = requests.request(method, url, timeout=30, **kwargs)
    if not response.ok:
        print(f"{method} {url} failed: {response.status_code}\n{response.text}", file=sys.stderr)
        response.raise_for_status()
    if response.text:
        return response.json()
    return None


def existing_goal() -> dict[str, Any] | None:
    goals = req("GET", f"/companies/{COMPANY_ID}/goals")
    for goal in goals:
        if goal.get("title") == ROOT_GOAL_TITLE:
            return goal
    return None


def get_or_create_goal() -> dict[str, Any]:
    found = existing_goal()
    payload = {
        "title": ROOT_GOAL_TITLE,
        "description": "\n".join([
            "Board mandate: Land Your Web becomes the legal shell and operating company for an AI-first SaaS venture, not an agency-client sales machine.",
            "Primary objective: identify, validate, build, and market a SaaS opportunity with high gross margins and low/no sales-call dependency.",
            "Cash budget: $0/month. Use only existing Codex Pro plan tokens, local machines, owned domains/repos/tools, and free distribution channels unless Stefan explicitly approves spend.",
            "Revenue model target: self-serve, product-led, API-first, usage-based or simple subscription, healthy gross margins, minimal support burden.",
            "Avoid: custom web-dev client work, agency retainers, products requiring Stefan on sales calls, high-support consulting, ideas needing paid ads before validation, or anything with fragile data/legal risk.",
            "Preference: GTM/revops/marketing automation pain where agents can scrape/enrich/score/compose/monitor/reconcile repetitive workflows and customers can buy without a call.",
            "First milestone: within 7 days produce a validated opportunity brief, MVP spec, landing page copy, pricing hypothesis, and first distribution loop. Within 30 days ship a smoke-testable MVP.",
        ]),
        "status": "active",
        "ownerAgentId": OVERLORD_ID,
    }
    if found:
        return req("PATCH", f"/goals/{found['id']}", json=payload)
    return req("POST", f"/companies/{COMPANY_ID}/goals", json=payload)


def issue_by_title() -> dict[str, dict[str, Any]]:
    issues = req("GET", f"/companies/{COMPANY_ID}/issues")
    return {issue.get("title"): issue for issue in issues}


def create_or_update_issue(goal_id: str, title: str, description: str, assignee_id: str, priority: str = "high") -> dict[str, Any]:
    by_title = issue_by_title()
    existing = by_title.get(title)
    payload = {
        "title": title,
        "description": description,
        "status": "todo",
        "priority": priority,
        "assigneeAgentId": assignee_id,
        "goalId": goal_id,
        "workMode": "standard",
    }
    if existing:
        return req("PATCH", f"/issues/{existing['id']}", json=payload)
    return req("POST", f"/companies/{COMPANY_ID}/issues", json=payload)


def cancel_old_agency_gtm() -> None:
    issues = req("GET", f"/companies/{COMPANY_ID}/issues")
    for issue in issues:
        if issue.get("title") in OLD_GTM_TITLES and issue.get("status") != "cancelled":
            req("PATCH", f"/issues/{issue['id']}", json={
                "status": "cancelled",
                "description": (issue.get("description") or "") + "\n\nCancelled by board pivot: LYW is now focused on creating an AI-first SaaS venture, not selling web-dev/client-service packages.",
            })
            print(f"Cancelled old agency-GTM task: {issue.get('identifier')} {issue.get('title')}")


def configure_zero_budget() -> None:
    company = req("PATCH", f"/companies/{COMPANY_ID}", json={
        "budgetMonthlyCents": ZERO_BUDGET,
        "metadata": {
            "cashBudgetMonthlyCents": ZERO_BUDGET,
            "allowedSpend": "Existing Codex Pro plan tokens/usage only; no extra cash spend without Stefan approval.",
            "ventureMode": "AI-first SaaS creation under LYW legal structure",
        },
    })
    print(f"Company cash budget set to ${company.get('budgetMonthlyCents', 0) / 100:.2f}/month")
    for agent_id in (OVERLORD_ID, MERCURY_ID):
        agent = req("PATCH", f"/agents/{agent_id}", json={
            "budgetMonthlyCents": ZERO_BUDGET,
            "adapterType": "codex_local",
            "adapterConfig": {},
            "replaceAdapterConfig": True,
            "status": "idle",
        })
        print(f"Agent budget set to $0/month: {agent.get('name')} using {agent.get('adapterType')}")


def seed_tasks(goal_id: str) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    tasks.append(create_or_update_issue(
        goal_id,
        "OVERLORD mandate: pivot LYW into a self-serve AI SaaS venture",
        """
You are OVERLORD. Execute the board pivot.

Mission:
- Stop thinking like a web-dev agency selling clients.
- Land Your Web is the legal/operator structure for a new AI-first SaaS company.
- Identify the best opportunity, choose one, and drive execution toward a marketable product.

Hard constraints:
- $0 incremental cash spend. Existing Codex Pro usage is allowed. Local machines are allowed. Free APIs/tools only unless Stefan approves spend.
- Avoid sales-call-dependent offers. Stefan should not be required on calls to make the business work.
- Target healthy software margins: low compute per customer, clear pricing metric, low support burden, automated onboarding.
- Avoid custom services disguised as SaaS.

Deliverables in /home/automation/lyw-workspace/ai-saas-company/:
1. CEO_DECISION.md — selected opportunity, why now, why us, why this beats alternatives.
2. KILL_LIST.md — ideas rejected and exactly why.
3. 30_DAY_EXECUTION_PLAN.md — week-by-week build/market/validate plan.
4. RISKS_AND_GATES.md — hard gates that kill/pivot the idea.
5. TASKS_FOR_MERCURY.md — specific growth/research tasks for MERCURY.

Decision frame:
- Pain urgency
- Buyer accessibility without sales calls
- Ability to validate with public data / cold audience / communities
- Gross margin and compute cost
- MVP complexity
- Distribution advantage
- Pricing power
- Time-to-first-dollar

Be savage. Pick one opportunity. Do not make a cute list and hide from decision-making.
""".strip(),
        OVERLORD_ID,
        "critical",
    ))

    tasks.append(create_or_update_issue(
        goal_id,
        "MERCURY research: find AI SaaS opportunities with no-call distribution",
        """
You are MERCURY. Hunt for AI SaaS opportunities that can be marketed without Stefan living on sales calls.

Mission:
- Find 10 opportunity candidates in GTM/revops/marketing automation or adjacent B2B workflows.
- Prefer repetitive, painful workflows where AI agents can save time or create revenue.
- Focus on self-serve or low-touch buying behavior.

For each opportunity, score:
- Buyer persona
- Pain intensity
- Existing alternatives and price
- Why now
- Data/input availability
- MVP complexity
- Viral/referral/content potential
- Ability to sell with landing page + demo + async onboarding
- Likely pricing model
- Estimated gross margin
- Biggest risk

Required deliverables in /home/automation/lyw-workspace/ai-saas-company/:
1. MERCURY_OPPORTUNITY_SCAN.md
2. opportunity_scores.csv
3. TOP_3_POSITIONING.md
4. DISTRIBUTION_NOTES.md

Mindset:
Warm and bubbly in voice. Ice-cold in analysis. Ask: can we do this more, better, cheaper, and with fewer calls?
""".strip(),
        MERCURY_ID,
        "critical",
    ))

    tasks.append(create_or_update_issue(
        goal_id,
        "OVERLORD product thesis: choose the SaaS and define MVP boundaries",
        """
You are OVERLORD. After reviewing MERCURY's opportunity scan, choose the SaaS product.

Deliver:
- PRODUCT_THESIS.md
- MVP_SCOPE.md
- PRICING_HYPOTHESIS.md
- DATA_MODEL.md
- BUILD_ORDER.md

Rules:
- Scope must fit 30 days.
- Product must be sellable without Stefan on calls.
- Pricing must map to value: per workspace, per monitored source, per generated asset, per lead, per automation, or usage-based.
- Include kill criteria: if validation fails, what exact metric kills the idea?
""".strip(),
        OVERLORD_ID,
        "critical",
    ))

    tasks.append(create_or_update_issue(
        goal_id,
        "MERCURY GTM: design zero-cash launch loops for selected SaaS",
        """
You are MERCURY. Build the marketing machine for the selected AI SaaS.

Deliver:
- LANDING_PAGE_COPY.md
- FIRST_20_CONTENT_IDEAS.md
- FIRST_50_OUTREACH_TARGETS.csv — only if public/ethical data is available
- CASE_STUDY_SIMULATION.md — honest hypothetical/demo case study, clearly labeled not fake proof
- GPT_IMAGE_2_CREATIVE_BRIEFS.md — image prompts for launch creatives
- REFERRAL_AND_AFFILIATE_LOOP.md

Channels to consider:
- founder-led content
- SEO/GEO pages
- outbound to public business emails only where appropriate
- communities
- influencers/micro-creators
- referrals and affiliates
- directories/product launches
- programmatic free tools

Constraint: $0 cash spend. No paid ads unless later approved.
""".strip(),
        MERCURY_ID,
        "high",
    ))

    tasks.append(create_or_update_issue(
        goal_id,
        "OVERLORD build command: create repo/workspace skeleton for selected SaaS",
        """
You are OVERLORD. Prepare the build skeleton after selecting the product.

Deliver:
- /home/automation/lyw-workspace/ai-saas-company/repo-plan.md
- /home/automation/lyw-workspace/ai-saas-company/technical-architecture.md
- /home/automation/lyw-workspace/ai-saas-company/first-milestone-issues.md

Include:
- stack recommendation
- data sources
- auth/onboarding approach
- billing plan, even if not integrated yet
- low-compute architecture
- privacy/legal risks
- launch checklist

Do not build random code before strategy is chosen. But make the next build step obvious enough that a coding agent can start immediately.
""".strip(),
        OVERLORD_ID,
        "high",
    ))

    tasks.append(create_or_update_issue(
        goal_id,
        "MERCURY validation: create no-call demand test plan",
        """
You are MERCURY. Design validation that does not require Stefan on calls.

Deliver:
- NO_CALL_VALIDATION_PLAN.md
- WAITLIST_COPY.md
- DEMO_SCRIPT.md
- ASYNC_CUSTOMER_DISCOVERY_QUESTIONS.md
- VALIDATION_METRICS.md

Required validation signals:
- waitlist signup
- reply requesting access
- demo click
- payment intent
- public community engagement
- qualified inbound without a call

No vanity metrics unless tied to a next action.
""".strip(),
        MERCURY_ID,
        "high",
    ))
    return tasks


def main() -> None:
    configure_zero_budget()
    cancel_old_agency_gtm()
    goal = get_or_create_goal()
    print(f"Active SaaS goal: {goal.get('title')} [{goal.get('id')}]")
    tasks = seed_tasks(goal["id"])
    for task in tasks:
        print(f"Task ready: {task.get('identifier')} {task.get('status')} — {task.get('title')}")


if __name__ == "__main__":
    main()

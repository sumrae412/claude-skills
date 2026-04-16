# Kill Criteria Template

Generate a project-specific version for every system or feature reviewed.

## Day-0 Setup (Before First Commit)

```
PROJECT: [Name]
OWNER: [Person responsible]
KILL CRITERIA OWNER: [Different person — enforcer]
START DATE: [Date]
EVALUATION WINDOW: [30/60/90 days]
BUDGET CAP: [Monthly cost ceiling]
SUCCESS METRIC: [The one number that justifies this feature]
SUCCESS THRESHOLD: [Minimum acceptable value]
MEASUREMENT METHOD: [Dashboard URL, query, API]
```

## Tier 1 — Hard Kill Triggers

Non-negotiable. If met, shut down immediately. No meeting, no discussion.

| # | Trigger | Auto-Kill? |
|---|---------|------------|
| H1 | Security breach traced to this component | YES — immediate rollback |
| H2 | P1/P0 production incident caused by this component | YES — immediate rollback |
| H3 | Cost exceeds BUDGET_CAP * 1.5 on any single day | YES — auto-disable |
| H4 | Zero usage for 30 consecutive days | YES — auto-decommission |
| H5 | Sole maintainer departs, no volunteer within 14 days | Owner enforces |

## Tier 2 — Review Triggers

Force mandatory review within 48h. **Default outcome is KILL.** Team must argue for continuation.

| # | Trigger | Default |
|---|---------|---------|
| R1 | Success metric below threshold for 14 consecutive days | Kill |
| R2 | Maintenance cost > X eng-hours/month unplanned work | Kill |
| R3 | 3 consecutive sprints with unplanned work | Kill |
| R4 | Dependency CVE >= CVSS 7.0 | Kill unless patched in 72h |
| R5 | Team velocity decrease > 15% since introduction | Kill |
| R6 | New team member cannot make meaningful change within 1 day | Simplify or kill |

### Review Protocol

1. Present data (5 min). No narrative, just numbers.
2. Owner states: "Default outcome is shutdown. Who argues otherwise?"
3. Continuation requires: explanation of miss + concrete plan for 14-day fix + named owner
4. If still not met at follow-up: kill with no further review.

## Tier 3 — Soft-Go Criteria

Must meet ALL within evaluation window to continue existing:

| # | Criterion | Target |
|---|-----------|--------|
| S1 | Primary success metric | >= TARGET for 7 consecutive days |
| S2 | Latency / performance | P95 <= X ms for 7 consecutive days |
| S3 | Security | Zero incidents attributable |
| S4 | Cost | Under BUDGET_CAP for 7 consecutive days |
| S5 | Bus factor | >= 2 people can independently modify and deploy |
| S6 | Documentation | Exists, validated by non-author |

## Anti-Vanity Addendum

Include at least 3 in every framework:

| # | Criterion | What it catches |
|---|-----------|----------------|
| A1 | No abstraction without 2+ consumers | Premature abstraction |
| A2 | No new dependency without written justification | Framework worship |
| A3 | Components unmodified for 90 days flagged for deletion | Dead code |
| A4 | Architecture changes require "what could be simpler?" in RFC | Complexity bias |
| A5 | No tech choices based on "learning opportunity" in production | Resume-driven dev |
| A6 | Complexity budget: max files proportional to user value | Over-decomposition |
| A7 | "Could a junior maintain this?" required in every design review | Intellectual vanity |

## Enforcement Calendar

```
Day 0:    Kill criteria signed off + auto-kills deployed and tested
Day 1:    Feature ships
Day 7:    First checkpoint — trending toward targets?
Day 14:   Second checkpoint — Tier 2 triggers tripped?
Day 30:   Soft-go evaluation. Meet criteria or kill.
Day 90:   Post-graduation review
Day 180:  Second review — still necessary?
```

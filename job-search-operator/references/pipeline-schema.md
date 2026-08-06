# Pipeline schema

Use this structure only after the user approves migration of an existing tracker. Preserve all historical sections below the operator-managed sections unless the user explicitly approves consolidation.

## Operator queue

Maintain one row per active role:

| Company | Role | Stage | Fit | Last event | Next action | Due | Warm path | Source |
|---|---|---|---:|---|---|---|---|---|

Field rules:

- **Company / Role:** exact posting identity. Do not collapse concurrent roles.
- **Stage:** one value from `SKILL.md`.
- **Fit:** `STRONG_FIT`, `STRETCH`, `WEAK_FIT`, `NO_GO`, or `unscored`. Reuse `jd-screener`; do not improvise a second rubric.
- **Last event:** `YYYY-MM-DD: <observed event>`.
- **Next action:** one specific verb-led action. Never write “monitor” without a date or trigger.
- **Due:** `YYYY-MM-DD`, `trigger:<event>`, or `none`. Do not invent follow-up dates.
- **Warm path:** named person plus relationship strength, `none found`, or `unchecked`.
- **Source:** canonical posting URL, recruiter thread, or local `jd.md` path.

## Needs clarification

Put incomplete or conflicting records here. Each item must name the missing fact and the decision it blocks.

## Outcomes

Retain the existing outcome history. Add:

- Application route: cold, warm intro, recruiter-led, or unknown.
- Highest verified stage.
- Outcome date and evidence source.
- Materials used, when known.

## Migration procedure

1. Read the existing tracker completely.
2. Build a preview without editing the source.
3. Account for every existing active and outcome row.
4. Mark missing data `unknown`; do not repair history by guesswork.
5. Show totals before and after. Counts must reconcile.
6. Ask for approval.
7. Edit with a recoverable diff.
8. Verify all company and role names still appear after the edit.

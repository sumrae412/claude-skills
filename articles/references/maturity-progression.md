# Maturity progression — where /articles is, where it could go

Adapted from Jason Liu, "Six levels of complexity in a Codex morning brief" — https://jxnl.co/writing/2026/05/18/six-levels-of-complexity-of-an-ai-powered-morning-brief-with-codex/ (saved from Mem 2026-05-20).

The framework describes increasingly sophisticated AI-powered automation, from a flat summary to a memory-vault feedback loop. Applied to `/articles`:

| Level | Description | `/articles` status |
|---|---|---|
| 1 | Tools answer "what's going on today" | ✅ — pulls from 4 Mem collections, lists notes |
| 2 | Persistent agents file shapes the output | ✅ — SKILL.md + per-target priority list defines the triage rubric |
| 3 | Recurrence + feedback improves it | ✅ — invoked on demand; user redirections inform next-batch triage (informally) |
| 4 | Project-level threads with different "importance" definitions | ✅ — target list (claude-skills, CourierFlow, BetterBurgh, DLAI) gives each its own relevance lens |
| 5 | Drafts obvious next actions, not just summaries | ⬜ — produces verdicts + "next action" prose, but does NOT draft the actual skill edit, PR, or memory file |
| 6 | Feeds a memory vault that learns from prior triage | ✅ — `triage-ledger.md` (per-item dedup) + `triage-patterns.md` (class-level skip/keep pre-filter), read at step 2, appended at step 5 (2026-07-19) |

## Upgrade paths

**To reach Level 5:** Add an optional `--draft` mode that, for high-value pulls, also produces the actual reference-file diff or memory entry as a separate tool call. Gate behind user confirmation per article, not per batch.

**To reach Level 6:** After archiving, write a short MEMORY entry capturing the pattern of the batch (e.g., "Codex tutorials → auto-skip; arXiv agent-harness surveys → high-value"). Next `/articles` run loads that file in Step 2 to pre-filter the obvious-skip class before fetching note content.

## Why not implement now

Both upgrades add complexity that may not pay off until inbox volume justifies it. Re-evaluate when triage batches routinely exceed 20 notes or when the same skip-pattern recurs across 3+ runs.

`inbox-triage` benefits from the same framework — it currently sits around Level 3-4 (Gmail fetch + Mem routing + scoring rubric + project-level differentiation). Level 5 there would mean auto-drafting replies on every urgent message rather than just flagging them.

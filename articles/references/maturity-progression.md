# Maturity progression — where /articles is, where it could go

Adapted from Jason Liu, "Six levels of complexity in a Codex morning brief" — https://jxnl.co/writing/2026/05/18/six-levels-of-complexity-of-an-ai-powered-morning-brief-with-codex/ (saved from Mem 2026-05-20).

The framework describes increasingly sophisticated AI-powered automation, from a flat summary to a memory-vault feedback loop. Applied to `/articles`:

| Level | Description | `/articles` status |
|---|---|---|
| 1 | Tools answer "what's going on today" | ✅ — pulls from 4 Mem collections, lists notes |
| 2 | Persistent agents file shapes the output | ✅ — SKILL.md + per-target priority list defines the triage rubric |
| 3 | Recurrence + feedback improves it | ✅ — invoked on demand; user redirections inform next-batch triage (informally) |
| 4 | Project-level threads with different "importance" definitions | ✅ — target list (claude-skills, CourierFlow, BetterBurgh, DLAI) gives each its own relevance lens |
| 5 | Drafts obvious next actions, not just summaries | ✅ — opt-in `/articles --draft` mode: per-article gated, text-only drafts of the actual edit (2026-07-19) |
| 6 | Feeds a memory vault that learns from prior triage | ✅ — `triage-ledger.md` (per-item dedup) + `triage-patterns.md` (class-level skip/keep pre-filter), read at step 2, appended at step 5 (2026-07-19) |

## Shipped 2026-07-19

**Level 5** — `/articles --draft`, an opt-in mode that drafts the actual edit for high-value pulls, gated per article and text-only (see SKILL.md step 4b).

**Level 6** — `triage-ledger.md` (per-item dedup) and `triage-patterns.md` (class-level skip/keep pre-filter), read at step 2 and appended at step 5.

Both were held back pending volume; the trigger condition set here — "triage batches routinely exceed 20 notes, or the same skip-pattern recurs across 3+ runs" — was met by mid-2026 run history, and swarm mode (step 1b) already assumes 11-40-note queues as normal.

## What's left

No Level 7 in the framework. The remaining leverage is upstream of this skill: capture quality in Mem. Body-less captures with dead tracking redirects are the dominant failure mode, and no amount of triage logic fully repairs them — the fix is clip-side (store canonical URLs, mark `Type: video`), which Summer updated on 2026-07-19.

`inbox-triage` benefits from the same framework — it currently sits around Level 3-4 (Gmail fetch + Mem routing + scoring rubric + project-level differentiation). Level 5 there would mean auto-drafting replies on every urgent message rather than just flagging them.

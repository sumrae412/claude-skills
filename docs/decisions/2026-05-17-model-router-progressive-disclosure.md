# Decision — Progressive disclosure split for model-router skill

**Date:** 2026-05-17
**Status:** Active
**Skill:** [`model-router/SKILL.md`](../../model-router/SKILL.md)

## Decision

Split the `model-router` skill into a thin SKILL.md (compact tier→model lookup, inline routing tables, 3 examples) + two lazy-loaded reference files:

- `model-router/references/signal-scoring.md` — full 22-row weighted-signal table, threshold rules, worked ambiguous cases
- `model-router/references/examples.md` — full 6-example set + 3 edge cases

## Why

SKILL.md content stays in context across turns once the skill activates (per `code.claude.com/docs/en/slash-commands`: "stays in context across turns"). At 350 lines (~4K tokens), the always-resident cost compounds across long sessions. The weighted-signal detail and full example set are referenced in ~20% of routing calls — moving them to lazy-loaded files trades a small per-ambiguous-case overhead (one `Read` tool call) for a recurring savings on every turn the skill is active.

Estimated impact: SKILL.md drops from 350 → ~280 lines (~30% reduction in always-resident skill content); references load only when explicitly needed.

## How to revisit

Two tracking mechanisms:

### 1. Grep across conversation transcripts

```bash
# How often did model-router's reference files actually get loaded?
loaded=$(grep -l "model-router/references/" \
  ~/.claude/projects/*/conversations/*.jsonl 2>/dev/null | wc -l)
total=$(grep -l "model-router/SKILL.md" \
  ~/.claude/projects/*/conversations/*.jsonl 2>/dev/null | wc -l)
echo "References loaded in $loaded of $total sessions ($(( total > 0 ? loaded * 100 / total : 0 ))%)"
```

### 2. `/stats` for model-mix calibration

Claude Code's `/stats` command "visualizes daily usage patterns, session history, and model preferences." If model-mix over time skews far from what the router recommends (e.g., almost everything ran on Opus even though the router classifies most tasks as Sonnet-tier), that's a signal the skill isn't firing in the right places or the user is overriding routinely.

## Reversal thresholds

Move the reference content back inline if either of these holds after ~30 days of active use:

- `references/signal-scoring.md` loaded in **>50% of sessions** where `model-router` activated → not really a reference, it's load-bearing; reverse the split
- `references/signal-scoring.md` loaded **multiple times per session** consistently → same call, reverse

Move further content OUT (deeper progressive disclosure) if SKILL.md grows back above 350 lines from accreted additions.

## Revisit date

**2026-06-17** — run the grep command above; check `/stats` for skewed usage; decide reverse / keep / deepen.

## Provenance

- Triggered by: in-session audit of model-router for token efficiency (user request, 2026-05-17)
- Pattern source: Claude Code official docs progressive-disclosure pattern + CLAUDE.md memory entry "Large SKILL.md files belong in progressive disclosure layout"
- Tracking-tool source: skills-vs-commands article surfaced `/stats` as a sibling to grep-based tracking

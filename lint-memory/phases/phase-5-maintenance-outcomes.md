# Phase 5: Maintenance Outcomes (full mode only)

Detection (Phases 2-3) finds *problems*. This phase forces a *decision per
drifted doc* so "audit the memory" doesn't collapse into a vague "is this
still right?" with no action.

Adapted from EveryInc/compound-engineering's `ce-compound-refresh`
(five-outcome model + stale-marking). See SOURCE note at bottom.

## When to run

- Full lint only, and only when Phase 2/3 surfaced drift: stale code
  references, moderate-overlap entry pairs, or contradictions.
- Skip in quick mode.

## The five outcomes — one explicit decision per drifted doc

Each drifted entry gets exactly one outcome, each with its own evidence bar:

- **Keep** — accurate and useful; no edit. (Default when drift was a false
  positive.)
- **Update** — references drifted (renamed file, moved path) but the lesson
  is still right; apply in-place fixes. Auto-fixable ONLY for pure
  link/path corrections; lesson-content edits stay manual.
- **Consolidate** — two entries overlap heavily; merge unique content into
  the canonical one, delete the subsumed entry. Gate at **4-5/5 overlap
  dimensions** (problem statement, root cause, solution, referenced files,
  prevention rule). Below that bar, the default is **add a cross-reference,
  not merge** — see SKILL.md "Companion tooling" and the 2026-05-12
  validation (5/5 inferred pairs were complementary, 0/5 duplicates).
- **Replace** — the guidance is now misleading (recommended fix became an
  anti-pattern); write a successor and delete the old. Manual — never
  auto-applied.
- **Delete** — code is gone, problem domain is gone, no inbound substantive
  citations; remove the entry (git history is the archive). Manual; never
  delete a hub (>10 inbound refs — see Companion tooling).

## Stale-marking — when you can't confidently rewrite

The key borrowed insight: when drift is so fundamental that you can't
confidently document the current approach from a file scan (subsystem
replaced, new architecture too complex to infer), do NOT guess at a
Replace. Mark the entry stale in place via frontmatter:

```yaml
status: stale
stale_reason: <one line — what drifted and why a confident rewrite isn't possible yet>
stale_date: <YYYY-MM-DD>
```

Recommendation surfaced in the report: re-capture via `session-learnings`
after the next real encounter with that area, when fresh problem-solving
context exists. Stale-marking is reversible and honest; an incorrect
Replace silently misleads future sessions.

## Modes

- **Interactive** (default) — one question at a time on ambiguous cases,
  lead with a recommended outcome.
- **Autofix** (`mode:autofix`) — apply only unambiguous, allowed auto-fixes
  (link/path Updates); mark every ambiguous case `status: stale` for human
  review. Report has two sections: **Applied** (writes that succeeded) and
  **Recommended** (writes that couldn't be applied, with full rationale).

## Fix discipline (unchanged from Phase 4)

- Auto-fixable: link/path Updates only.
- Never auto-apply: Replace, Delete, lesson-content edits, contradiction
  resolution. These are surfaced as Recommended with rationale.

## Output

Per-doc outcome table (entry, outcome, evidence, applied vs recommended) +
a stale-marked list with re-capture pointers.

---

SOURCE: outcome model and stale-marking adapted from
EveryInc/compound-engineering-plugin `ce-compound-refresh`
(https://github.com/EveryInc/compound-engineering-plugin,
`docs/skills/ce-compound-refresh.md`). Triaged via `/articles` →
`useful-for` on 2026-06-01.

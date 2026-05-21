# Maintenance Reminders

Scheduled checks for claude-flow's progressive-disclosure split. Per memory
`progressive_disclosure_reversibility_pattern`, splits should be measured —
unused phase/reference files indicate the split was wrong or the workflow has
shifted, and either case warrants collapsing or restructuring.

## Quarterly: phase/reference load-frequency audit

**Every 90 days** (next: 2026-08-17), grep recent session transcripts for which
`phases/phase-*.md` and `references/*.md` files actually loaded. Files that
loaded <2× in the window are candidates for either:

- inlining into the router (if always loaded together with another file), or
- archival (if loaded zero times — the use case has moved or never materialized).

```bash
# Rough survey — adapt to wherever your transcripts live
grep -rh "claude-skills/claude-flow/phases/\|claude-skills/claude-flow/references/" \
  ~/.claude/projects/ 2>/dev/null \
  | sort | uniq -c | sort -rn | head -40
```

## Quarterly: project-skill-menu drift check

**Every 90 days** (next: 2026-08-17), confirm the default menu in
`references/project-skill-menu.md` still matches the actual courierflow skill
catalog (`/courierflow-*` in the skill list). Skills added/removed/renamed in
courierflow should propagate to the menu, and the Phase 5 forced-selection
block in `phases/phase-5-implementation.md` should mirror it. Also re-check the
Phase 0 trigger matrix in `phases/phase-0-context.md`.

## Quarterly: stale cross-reference scan

**Every 90 days** (next: 2026-08-17), run:

```bash
cd ~/claude_code/claude-skills/claude-flow
grep -rEho '\bphases/[a-z0-9.-]+\.md|references/[a-z0-9.-]+\.md|contracts/[a-z0-9.-]+\.md|docs/[a-z0-9./-]+\.md|scripts/[a-z0-9_-]+\.(py|sh)' \
  SKILL.md phases/ references/ 2>/dev/null \
  | sort -u \
  | while read ref; do test -e "$ref" || echo "MISSING: $ref"; done
```

Two relative-path bugs (`../../docs/...` should have been `../docs/...`) were
shipped to Phase 5 in 2026-04-29 and only caught at 2026-05-17 audit. The grep
above catches that class.

## Maintainer Note

The current split — thin router (SKILL.md, ~280 lines) + 10 phase files +
~40 reference files + 6 contract schemas — was chosen because the workflow
covers 8 distinct paths (bug/fast/clone/plan/lite/audit/explore/full) and
several optional sub-flows (goal-mode, visual checkpoint, phantom-completion
audit, ensemble fan-out). Loading everything inline would burn ~30K+ tokens of
context per session for content used on <10% of runs.

Reversal threshold: if any phase file loads <2× per quarter for two consecutive
quarters, inline its content into the router or delete it. If the router grows
past ~400 lines, re-split — but check whether the new bulk is actually generic
workflow content or project-coupled menus that should move into
`references/project-skill-menu.md`.

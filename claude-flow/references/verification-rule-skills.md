# Verification-Rule Skills

Project-defined deterministic checks that close claude_flow's feedback loop for
conventions no generic reviewer or linter holds. Ported from Anthropic's
"Building verification loops in Claude Code with skills"
(https://claude.com/blog/building-verification-loops-in-claude-code-with-skills,
2026-07-22), adapted to claude_flow's phase architecture.

## What this is, and why it is separate from the review cascade

claude-flow's Phase 6 already runs two complementary, and distinct, verification
layers:

- **Correctness reviewers** (Tier 1-4 cascade) — LLM passes that *review* the
  diff and raise findings.
- **The Exemplar Benchmark** (`phase-6-review-operations.md`) — comparative
  *quality* grading against an external bar.

Neither layer has a home for the **deterministic project rule** class: a hard,
machine-checkable invariant a project enforces by hand but no generic tool
catches. Anthropic's own example is the canonical one: *"Reject any migration
that drops a column without a backfill step."* A linter cannot know your
backfill policy; a reviewer can only be *reminded* to check it; only a
project-authored deterministic rule can *decide* it.

claude-flow's precedent for this class already exists and is the right model to
generalize: Phase 6 step 3b runs `core_gate.sh` — grep patterns for secrets and
unsafe `eval`/`exec` — against the raw diff **regardless of the Review cascade**,
because "an LLM pass can miss a grep-catchable secret." That is exactly a
project-rule verification check; it is just hardcoded to one security surface.

**This page is the generalization:** a mechanism for project-defined
verification-rule skills that run as an always-on deterministic gate beside
`core_gate.sh`, plus the authoring guide for writing them.

## Placement ladder (what rules belong where)

A rule's placement follows how *often* it must fire, not how clever it is:
Standalone, then Embedded, then Chained, then On-PR. claude-flow's runtime
executes the **set** of project rules in Phase 6 (Chained by default); what the
rule's *author* chooses between below is whether it should gate, and where.

1. **Standalone** — a cross-cutting rule you invoke deliberately, for checks
   that don't apply to every change (a pre-PR accessibility audit, a license-
   header pass). Cheap to author, but it is a turn you have to remember to take.
   The signal you have outgrown standalone: you run it after every change. Then
   promote it into the Phase 6 set.
2. **Embedded** — a check that belongs to one producing skill and fires as part
   of it. The article's form is a one-line append to the producing skill's body
   ("After creating the component, run eslint on it and address any error
   before reporting completion."). Within claude-flow, prefer the Chained form
   below over the embedded append: bolting a check onto Phase 5 fights the
   architecture that centralizes every gate in Phase 6. Use the embedded form
   only for a rule so tightly coupled to one implementer step it can't wait
   until review.
3. **Chained (Phase 6 default)** — ends of the producing pipeline, runs the
   project's rule skills back-to-back with `core_gate.sh`. This is where claude-
   flow's runtime actually executes verification-rule skills. One skill calls
   the next; several verified handoffs run end-to-end. Chains trade flexibility
   for automation — add a rule to the set only when it will fire for the
   majority of changes, so the gate does not become noise.
4. **On-PR** — promote a solid Chain into a CI job that runs the same rules on
   every pull request, independent of the author remembering. Per the article,
   hold off until the chain is stable; every adjustment there becomes a
   team-visible event.

## Authoring a verification-rule skill

Code the rule as a small skill under `.claude/skills/verify-<rule>/SKILL.md` in
the host repo (not in claude-flow's own tree — these are project-specific, the
same way `project_skill_menu` and the trigger matrix are). Keep the body in the
pattern Anthropic's example uses: state the invariant, say what to report and
what to fix, and bind the rule's scope.

```text
# .claude/skills/verify-log-hygiene/SKILL.md
---
name: verify-log-hygiene
description: Check that error logs include the request ID and never
  include the request body. Use when the diff touches error handling
  or logging.
allowed-tools: [Read, Edit, Grep]
---
Read the error-handling paths in the current diff.

For each log call on an error path, confirm it includes the request ID
and does not pass the request body, headers, or any user-supplied payload.

Report each violation with file:line, then fix it: add the request ID
where it's missing and strip the payload from the log call.
```

When the check is *pure deterministic* (a grepable or scriptable invariant),
prefer a zero-token script or a skill whose body is a single rule, the way
`core_gate.sh` works. The rule is then:

```bash
# .claude/skills/verify-migration-backfill/SKILL.md
---
name: verify-migration-backfill
description: Reject any migration that drops a column without a backfill step.
  Use when the diff touches alembic/ or *_migration files.
allowed-tools: [Read, Grep, Bash]
---
Report every column drop in the diff. For each, confirm the migration
includes a matching data backfill and a run order that executes the backfill
before the column drop. Violations are HIGH findings — the rule is a project
invariant, not a style preference.
```

When authoring a rule, confirm it qualifies:

- **Deterministic rules only.** If the check needs human judgement ("does the
  UI flow feel right?") it belongs in a reviewer or the Exemplar Benchmark, not
  here. Rules are gates, not gradients: every failure ships or none does.
- **Project conventions, not code style.** The most valuable rules are the ones
  `coding-best-practices` cannot know — "no migration drops a column without
  backfill", "error logs carry the request ID", "anything you keep enforcing by
  hand". Those are exactly the manual corrections the article argues should be
  a loop.
- **Bounded tool surface.** Use only the tools the check needs (`Read`,
  `Edit`, `Grep`, `Glob`), plus `Bash` for the rule probe when it is
  scriptable. A rule that needs a build server or an external service is a job,
  not a skill.
- **Naming `verify-<rule>`.** Discoverable next to `core_gate.sh`, and the
  predicate reads clearly in the Phase 6 gate output.

## Where it connects in Phase 6

The project's rule set runs in Phase 6 step 3b/3c — the always-deterministic
gate — not because the rule is a reviewer. A deterministic failure (a dropped
column without backfill) is a project gate finding, exactly like a `[FAIL]` line
from `core_gate.sh`: it PRODUCES a HIGH finding fed into the same Findings
Resolution as the cascade, independent of what Tier 1 returns. A project rule
that silently passes on a clean Tier 1 diff is a rule that never ran.

See `phase-6-quality.md` step 3b/3c for the wiring contract, and
`project-skill-menu.md` § Verification-rule menu for the authoring rules a
project applies when it selects its set.
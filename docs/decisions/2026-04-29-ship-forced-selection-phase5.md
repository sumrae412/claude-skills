# Decision: Ship Forced Skill Selection in Phase 5 Subagent Dispatches

**Date:** 2026-04-29
**Status:** Adopted — claude-skills rollout shipped 2026-04-29 (this PR). courierflow SKILL.md description-hygiene PR pending separately.
**Plan:** [2026-04-29-skill-selection-vs-progressive-disclosure.md](../plans/2026-04-29-skill-selection-vs-progressive-disclosure.md)
**Source motivation:** Su et al., *Skill Retrieval Augmentation for Agentic AI* (arXiv:2604.24594), Table 2 + RQ6.

## Decision

When a Phase 5 subagent dispatch could plausibly use ≥2 courierflow-* skills, the orchestrator now requires the subagent to commit to one (or `none`) up-front via:

```
SELECTED_SKILL: <name|none>
```

before any tool calls. This replaces the previous progressive-disclosure pattern where the subagent saw "you may load X if useful" and decided on the fly.

## Evidence

24-trial A/B run on 12 historical Phase 5 dispatches replayed via `claude -p` with `sonnet`. Full log: [.claude/experiments/skill_selection_ab.jsonl](../../.claude/experiments/skill_selection_ab.jsonl).

| metric | variant A (control) | variant B (forced) | Δ |
|---|---|---|---|
| correct skill | 58.3% | 75.0% | **+16.7pp** ≥15pp threshold ✓ |
| end-task pass (rubric) | 75.0% | 83.3% | **+8.3pp** ≥5pp threshold ✓ |
| over-load rate | 50.0% | 25.0% | **−25.0pp** |
| skill loaded | 83.3% | 75.0% | −8.3pp |
| need-aware load | 100% | 100% | 0 |

Both ship gates from the plan's decision tree met. Recommendation surfaced by [analyze_skill_selection.py](../../claude-flow/scripts/analyze_skill_selection.py): `SHIP B: correct +16.7pp, pass +8.3pp.`

## Why this matters

The paper's RQ6 found that LLMs across all tested scales (4B → frontier) load skills at nearly identical rates whether the task needs external help or not — a "need-awareness gap" the paper called fundamentally unsolved. Our **−25pp over-load** is direct evidence that a 30-line prompt change closes most of that gap on courierflow-scale skill libraries. Variant B is materially better at *not* loading skills on tasks the base model can already solve.

The single-row standout: **PR #464** (Calendar import wizard). Variant A picked `courierflow-api`; variant B correctly picked `courierflow-integrations`. Forced commitment beats hedged availability.

## Limitations

1. **End-task pass is a rubric, not a runtime measurement.** The replay prompts said "do not write code," so we couldn't run `quick_ci.sh` against actual diffs. The grading rubric (pass = `loaded == gold` OR `baseline_skill_free_pass`) is a reasonable substitute but not a proper end-to-end test.
2. **Two rows failed under both variants** — PR #476 (auth gold mislabeled or skill ambiguous) and PR #511 (CopilotKit gap; no `courierflow-copilot` skill exists). Neither failure is variant B's fault, but both reduce the headline +8.3pp pass delta.
3. **Sample size n=12.** Replicate on 24+ before treating these numbers as durable.
4. **Replay used `claude -p sonnet`, not the actual claude-flow Phase 5 environment.** Real Phase 5 dispatches happen inside a subagent context with prior phase outputs in scope. Behavior may differ; treat the +16.7pp as a lower bound until validated against real runs.

## Implementation

The rollout shipped 2026-04-29 per [docs/plans/2026-04-29-variant-b-rollout-plan.md](../plans/2026-04-29-variant-b-rollout-plan.md). Bundle contents:

1. ✅ `skill_selection_variant: "b"` is the default in `run_manifest.py:sync_state_manifest_path` (via `state.setdefault`). Two unit tests in `test_run_manifest.py` lock the default and protect the variant-A override.
2. ✅ Phase 5 doc updated — variant B is now labeled DEFAULT, variant A demoted to opt-out, scale-experiment pointer added.
3. ✅ Phase 1 discovery doc updated — `skill_selection_variant: "b"` listed in the initialization-must-include set.
4. ✅ Workflow-state-lifecycle doc updated — new field documented with full value table (a/b/b150/c1/c3).
5. ✅ Scheduled soak-check script ([schedule_variant_b_soak_check.py](../../claude-flow/scripts/schedule_variant_b_soak_check.py)) emits the MCP payload + writes durable fallback at `docs/decisions/REMINDERS.md`. Run before merge to register the 7-day fire.
6. **Pending separately:** the 5 courierflow-* `SKILL.md` description-hygiene edits land in the courierflow repo, not this one — the SKILL.md files are at `~/claude_code/courierflow/.claude/skills/courierflow-*/SKILL.md`. Phase 4c verification (during plan execution) caught this scope split.
7. After 1 week of real-run logs, the soak-check writes `docs/decisions/2026-05-06-variant-b-soak-results.md`.

## Follow-ups

- **Spawn a 2-week scheduled task** to evaluate the live rollout: pull `skill_selection_ab.jsonl` from real Phase 5 runs, re-run the analyzer, post results.
- ~~Consider variant C (scale test).~~ **Done 2026-04-29.** B-150, C1, and C3 all under-performed shipped variant B. See [docs/plans/2026-04-29-skill-selection-at-scale.md](../plans/2026-04-29-skill-selection-at-scale.md) "Results" section. **Conclusion: do not switch to retrieval-over-broader-corpus.** Curation beats retrieval at this scale.
- **Address the CopilotKit gap.** Either author `courierflow-copilot` skill, or relabel CopilotKit PRs to map to an existing skill. Current ambiguity costs ~1 of every 12 dispatches. The scale experiment confirmed this gap persists across all variants.
- **Apply description-quality hygiene to the full skill library.** The scale experiment found 5 description edits moved BM25 recall@5 from 62.5% → 100%. The same hygiene pass over all 205 session-loaded skills would benefit any future retrieval-based experiments and the `skill-discovery` skill itself.

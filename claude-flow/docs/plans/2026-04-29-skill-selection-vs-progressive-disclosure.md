# Skill Selection vs Progressive Disclosure Experiment

Date: 2026-04-29

## Hypothesis

For Phase 5 implementation subagents, forcing one explicit skill-selection
decision before tool use will improve relevant skill loading and end-task pass
rate compared with passive progressive disclosure.

## Dataset Shape

- 60 replay trials.
- Paired Variant A and Variant B prompts.
- Tasks cover backend, UI, data, integration, and security-oriented Phase 5
  implementation work.
- Gold labels identify the expected CourierFlow skill or `none`.

## Variants

- Variant A: progressive disclosure. Prompt says the subagent may load a skill
  if useful.
- Variant B: forced selection. Prompt requires `SELECTED_SKILL:
  <skill-name|none>` before tool use.

## Metrics

- Loaded rate: whether any skill was loaded.
- Correct skill: selected or loaded skill equals the gold label.
- Need-aware load: skill loaded when the task needs one, skipped when it does
  not.
- Overload: unnecessary skill loading on tasks labeled `none`.
- End-task pass: `(loaded == gold) OR (baseline_skill_free_pass)` for replay
  prompts that do not write code.

## Decision Threshold

Ship Variant B only if:

- Correct-skill rate improves by at least 15 percentage points.
- End-task pass improves by at least 5 percentage points.
- Overload does not increase enough to erase the pass-rate gain.

## Scripts

```bash
python3 scripts/replay_skill_selection.py --variant a,b --dry-run
python3 scripts/analyze_skill_selection.py --log .claude/experiments/skill_selection_ab.jsonl
python3 scripts/grade_end_task_pass.py --log .claude/experiments/skill_selection_ab.jsonl
```

## Contamination Guard

Variant prompt tails must be split. Do not describe both variants in one task
block. Keep separate `VARIANT_A_TAIL` and `VARIANT_B_TAIL` constants so
Variant A subjects do not self-label as Variant B or emit the Variant B
`SELECTED_SKILL:` token.

# Skill Selection at Scale Experiment

Date: 2026-04-29

## Hypothesis

For Phase 5 implementation dispatch, a small curated menu of CourierFlow skills
will outperform broad retrieval over the full skill catalog because it reduces
choice overload and irrelevant skill activation.

## Dataset Shape

- Phase 5 implementation replay tasks from the same task families used in the
  A/B experiment.
- Full skill catalog size: 205 skills.
- Compared candidates include the curated five-skill menu and broad retrieval
  variants.

## Variants

- `b`: curated five-skill forced selection.
- `b150`: larger forced-selection menu.
- `c1` / `c3`: retrieval-assisted candidates from the broad catalog.

## Metrics

- Loaded rate: whether the model selected or loaded a skill.
- Correct skill: selected skill equals the gold label.
- Need-aware load: skill used only when needed.
- Overload: irrelevant skills selected from a larger menu.
- End-task pass: replay pass under the skill-selection grading rubric.

## Decision Threshold

Keep the curated menu unless a scale variant improves correct-skill rate by at
least 15 percentage points and end-task pass by at least 5 percentage points
without materially increasing overload.

## Scripts

```bash
python3 scripts/replay_skill_selection.py --variant b,b150,c1,c3 --dry-run
python3 scripts/analyze_skill_selection.py --log .claude/experiments/skill_selection_scale.jsonl
python3 scripts/grade_end_task_pass.py --log .claude/experiments/skill_selection_scale.jsonl
```

## Result

The stated 2026-04-29 scale check found that the curated five-skill menu beat
BM25/rerank retrieval over 205 skills for Phase 5 dispatch. Do not replace the
forced curated selection default without a fresh experiment.

## Contamination Guard

Keep variant prompt tails isolated. Retrieval variants must not mention the
forced-selection answer token unless that variant intentionally requires it.

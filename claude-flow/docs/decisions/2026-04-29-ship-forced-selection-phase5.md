# Ship Forced Skill Selection for Phase 5

Date: 2026-04-29

Status: Accepted

## Decision

Ship Variant B forced single-skill selection as the default Phase 5 dispatch
behavior. Implementation subagents must emit:

```text
SELECTED_SKILL: <skill-name|none>
```

before tool use, choosing from the curated five-skill CourierFlow menu.

## Evidence

A 60-trial A/B replay compared:

- Variant A: progressive disclosure, where the subagent may load a skill if it
  decides the skill is useful.
- Variant B: forced single-skill selection before implementation work.

The experiment result stated for the 2026-04-29 workflow change was that
Variant B improved correct skill loading and end-task pass rate enough to ship
under the decision threshold. Follow-up scale checks over the 205-skill catalog
found that the curated five-skill menu beat BM25/rerank retrieval for this
Phase 5 dispatch use case.

The shipped default is set by `run_manifest.py:sync_state_manifest_path` with
`state.setdefault("skill_selection_variant", "b")`.

## Reproduction

```bash
python3 scripts/replay_skill_selection.py --variant a,b --dry-run
python3 scripts/analyze_skill_selection.py --log .claude/experiments/skill_selection_ab.jsonl
```

Raw experiment logs are not bundled in this repository unless a local
`.claude/experiments/` directory exists.

## Caveats

- Re-run the A/B before replacing forced selection with retrieval.
- Variant A remains available only for replay experiments.
- Experimental scale variants (`b150`, `c1`, `c3`) are not production defaults.

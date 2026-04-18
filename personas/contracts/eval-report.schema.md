# Contract: `$eval_report`

Final output of Phase 6. Human-readable Markdown plus a machine-readable JSON sidecar.

## Markdown structure

```markdown
# Personas Eval — <app_name> — <YYYY-MM-DD>

## TL;DR
- <N> personas × <M> testing styles × <K> flows = <C> eval cells
- <X> crashes, <Y> functional bugs, <U> UI snag clusters, <Z> flows where ≥50% of personas got stuck
- <W> mean usefulness rating (1–5) across passed transcripts; <V>% of personas said they would use the app
- <P>% support coverage across diversity axes (target: 80%)
- <Q>% of transcripts passed fidelity gate (discarded transcripts not counted in findings)

## Bug Findings
### Crashes
- [B-01] <one-line description> — triggered by <persona_ids>, flow=<flow>, testing_style=<style>
  - Reproduction: <specific steps from transcript>
  - Transcript: <path>
### Functional bugs
- [F-01] <description> — triggered by <persona_ids>, ...

## UI Snag Findings
Grouped by app area. UI issues personas flagged while otherwise completing flows — distinct from crashes (app broke) and friction (persona gave up).

### Area: <area name>
- [U-01] <one-line issue> — raised by <N> personas across <flows>
  - Representative quote: "..."
  - Personas affected: <persona_ids>
  - Severity: minor | moderate | major

## Friction Findings
Grouped by flow, then by persona cluster.

### Flow: <flow_name>
- **<persona cluster label>** (<N> personas, <axis signature>):
  - <summary of friction: what they tried, where they gave up, stated reason>
  - Representative transcript: <path>
  - Recommended fix: <inferred from pattern — or "investigate further" if unclear>

## Usefulness Assessment
Per-flow usefulness ratings grouped by persona cluster. Answers: "once this segment has used the app, do they actually want it?"

### Flow: <flow_name>
| Persona cluster | Mean rating (1–5) | Would use (yes / no / maybe) | Representative quote |
|---|---|---|---|
| <cluster_label> (N personas) | 3.2 | 20% / 50% / 30% | "..." |

Low-usefulness clusters (mean <3.0 or >50% `would_use=no`) signal potential product-market-fit gaps, not bugs. Distinguish them from high-usefulness-but-stuck clusters (personas who wanted to use it but couldn't) — the latter convert to fixable UX items.

## Coverage Analysis
Per-axis coverage + under-represented regions. Flags any axis where no persona scored >0.8 or <0.2.

### Axes
| Axis | Low extreme | High extreme | Coverage |
|---|---|---|---|
| portfolio_size | 1_unit | 10_units | 0.XX |

## Fidelity Gate Summary
- Pass rate per PersonaGym task (5 scores: Action Justification, Expected Action, Linguistic Habits, Persona Consistency, Toxicity Control)
- Refusal rate per persona (flags personas the app / model resisted role-playing)

## Recommended Next Steps
1. Fixes (from Bug Findings)
2. Flows to redesign (from Friction Findings)
3. Axes to expand in next run (from Coverage Analysis)
4. Real-user recruitment profile (derived from high-friction persona clusters)

## Appendix
- Link to `<run-id>/` dir with full transcripts and phase contracts
- Config used: `<path to config.yaml>`
- Model versions used for persona player + evaluators
```

## JSON sidecar

Same content, machine-parseable. Used if the skill is wired into a dashboard or CI pipeline later.

```json
{
  "run_id": "...",
  "app_name": "...",
  "summary": { "cells": 0, "crashes": 0, "functional_bugs": 0, "ui_snags": 0, "stuck_flows": 0, "coverage": 0.0, "fidelity_pass_rate": 0.0, "usefulness_mean": 0.0, "would_use_yes_rate": 0.0 },
  "bugs": [ { "id": "B-01", "kind": "crash|functional", "description": "...", "personas": ["p01"], "flow": "...", "testing_style": "...", "transcript_path": "..." } ],
  "friction": [ { "flow": "...", "cluster_label": "...", "persona_ids": ["..."], "axis_signature": {}, "summary": "...", "representative_transcript": "...", "recommended_fix": "..." } ],
  "ui_snags": [ { "id": "U-01", "area": "...", "description": "...", "severity": "minor|moderate|major", "persona_ids": ["..."], "flows": ["..."], "representative_quote": "..." } ],
  "usefulness": { "by_flow_cluster": [ { "flow": "...", "cluster_label": "...", "persona_ids": ["..."], "mean_rating": 3.2, "would_use_distribution": { "yes": 0.2, "no": 0.5, "maybe": 0.3 }, "representative_quote": "..." } ], "overall_mean_rating": 3.4, "overall_would_use_yes_rate": 0.35 },
  "coverage": { "estimated_support_coverage": 0.0, "per_axis": [ { "name": "...", "coverage": 0.0 } ] },
  "fidelity": { "by_task": { "action_justification": 0.0, "expected_action": 0.0, "linguistic_habits": 0.0, "persona_consistency": 0.0, "toxicity_control": 0.0 }, "refusal_rate_per_persona": {} },
  "next_steps": ["..."]
}
```

## Persistence

- Markdown: `docs/persona-eval/<app>/YYYY-MM-DD-<run_id>.md`
- JSON: `docs/persona-eval/<app>/<run_id>/report.json`
- Both reference the `<run_id>/` directory containing all intermediate contracts and per-cell transcripts.

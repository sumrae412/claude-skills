## Critic Calibration (Eval-Driven Tuning)

Over multiple debate rounds, track critic accuracy to calibrate prompts. This applies the Claude Cookbook's [Building Evals](https://platform.claude.com/cookbook/misc-building-evals) and [Tool Evaluation](https://platform.claude.com/cookbook/tool-evaluation-tool-evaluation) patterns to reviewer agents.

### Tracking Critic Signal Quality

After each debate round, the Lead (Opus) already classifies findings as ADOPT/REJECT/DEFER. This classification **is the eval signal** — no separate evaluation infrastructure needed.

```
Per critic, track over time:
  - ADOPT rate: % of findings accepted as valid
  - REJECT rate: % of findings dismissed as false positives
  - DEFER rate: % of findings needing user judgment

Healthy critic: >60% ADOPT, <25% REJECT
Noisy critic:   <40% ADOPT, >40% REJECT → needs prompt tuning
Silent critic:  Rarely produces findings → may not be adding value
```

### When to Tune a Critic Prompt

| Signal | Action |
|--------|--------|
| REJECT rate >40% over 5+ rounds | Critic is generating noise. Review its prompt for over-broad patterns. Add "Only flag if you are >80% confident this is a real issue" constraint. |
| Same false positive type recurring | Add an explicit exclusion to the critic prompt: "Do NOT flag [pattern] — this is an accepted convention in this codebase." |
| Missing real issues (caught later) | Critic is under-sensitive. Add the missed pattern to the critic's checklist with an example. |
| ADOPT rate <30% | Consider demoting critic to conditional-only (skip for simple reviews) or replacing with a more targeted prompt. |

### Grading Method Priority (from Building Evals recipe)

For automated calibration:
1. **Code-based grading** (preferred) — If the finding references a specific code pattern, grep for it. If the pattern doesn't exist in the diff, it's a false positive. Zero cost.
2. **Lead-based grading** (current) — Opus Lead's ADOPT/REJECT is the grading function. Already implemented in Step 4 synthesis.
3. **User grading** (gold standard) — When user overrides Lead's ADOPT/REJECT decision, that's the highest-quality signal. Capture it in session-learnings.

### Calibration Cadence

Don't tune after every round. Aggregate over 5+ debate rounds, then:
1. Compute ADOPT/REJECT rates per critic
2. Identify the noisiest critic (highest REJECT rate)
3. Review its last 5 REJECTed findings — what pattern do they share?
4. Make ONE prompt change (following claude-flow's one-change principle)
5. Run 3+ rounds with the new prompt to verify improvement

This is the evaluator-optimizer loop applied to the debate team's own critics.


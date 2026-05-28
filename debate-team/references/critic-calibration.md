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
| REJECTed findings cluster around "too complex", "not minimal", "over-engineered", "unclean", or similar | Check for gold-like bias. Tune the prompt so complexity/minimality findings must cite concrete correctness, maintainability, delivery, user, or operations risk. |
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
4. Check whether any REJECT cluster reflects gold-like preference for concise,
   clean, canonical-looking answers over correct or complete answers
5. Make ONE prompt change (following claude-flow's one-change principle)
6. Run 3+ rounds with the new prompt to verify improvement

This is the evaluator-optimizer loop applied to the debate team's own critics.

## Calibration data points

### PR #534 — Phase 2.1c (single-file canary fix, CourierFlow, 2026-04-28)

Tier 3 invocation surfaced two operational gotchas:

1. `~/.claude/scripts/plancraft_review.py` accepts `--reviewer {deepseek, codex}` only. **No `codex-docs` role for non-code artifacts.** Strategy docs fall back to `--reviewer codex` (architecture critic) — still produces signal (~14 of 18 findings adopted on PR #534's strategy doc, including taxonomy ambiguity, pre-authorization concerns, vague pass criteria) but the role isn't role-matched. The `tier-gate-and-proposal.md` text mentioning `codex-docs` is aspirational, not present in the script.

2. `~/.claude/scripts/batch_review.py` (Claude batch reviewer) was absent on this machine. **Tier 3 gracefully degrades to DeepSeek + GPT-5 codex** — useful verdict still produced. Surface the missing leg in the verdict synthesis so the user knows the review was 2-of-3, not 3-of-3.

**Speculative-finding rule held a SECOND iteration:** PR #533's DeepSeek-flagged "third blocker may exist" materialized in PR #534 with a different shape (empty-messages on `/connect` rather than duplicate non-consecutive system messages). Had the Tier 1 DEFER speculation been ADOPTed as a preemptive defense, it would have masked the real failure shape. **Empirical:** DEFER speculative findings; the next smoke names the real shape in minutes.

**PR #534 review split:** 8 ADOPT / 5 REJECT / 0 DEFER (Tier 3 critics had concrete artifacts to cite because the smoke run was bundled in the same PR). Compare PR #533: 2/2/6. The bundling-with-smoke pattern produces a healthier review distribution.

### PR #118 — `evals` skill (claude-skills, 2026-05-27)

Three-round review of a 1,935-line docs artifact (router + 5 phases + 3 references). Modification delta: `docs/plans/2026-05-27-evals-skill-modification-delta.md`. Ledger: R1 internal × 4 → 20 ADOPT; R2 DeepSeek + GPT-4o codex → 14 ADOPT (DeepSeek) and ~10% adopt (codex, role-mismatched); R3 GPT-5 with docs-tuned wrapper → ~90% adopt, 5 load-bearing fixes neither earlier round caught.

**Calibration lessons:**

1. **Convergence across critics is not correctness when training corpora overlap.** R1 (four Anthropic-internal subagents) AND R2-DeepSeek both endorsed a sample-size figure that was off by 10× (~1,000 per arm vs the correct ~9,800 for p̄=0.5, Δ=0.02, power=0.8). Only R3-GPT-5 caught it. **Rule:** when N critics converge on a high-confidence *numeric* or *methodological* claim, treat that as a signal to run **one more cross-family critic**, not to stop. Concordance amplifies the value of a cross-family check; it does not substitute for one.

2. **Role-mismatch is structural, not model-quality.** Same OpenAI family produced ~10% adopt-rate (`--reviewer codex` with code-review system prompt) vs ~90% adopt-rate (GPT-5 via custom wrapper with docs-tuned system prompt) on the same artifact. This is the second documented instance of the failure mode named in the PR #534 entry above. **Action:** either add a `--reviewer codex-docs` mode to `~/.claude/scripts/plancraft_review.py` (system prompt tuned for docs artifacts, no code-quality vocabulary), or document the prompt-override pattern as the supported workaround. Until then, treat `--reviewer codex` adopt-rates <30% on docs PRs as a role-mismatch signal, not a content signal.

3. **Statistical / methodological bugs are the highest-value third-critic finding.** The five R3-only catches on PR #118 — paired-difference CI vs CI overlap, sample-size formula, pre-commit repetition count (anti-p-hacking), embedding model+version pinning, paired analyses for same-dataset A/B — are all textbook errors LLMs trained on online how-to content tend to get wrong the same way. Internal Anthropic subagents converged with one external critic and still missed all five. **Heuristic:** for any artifact teaching evaluation, statistics, or experimental design, R3 is not optional — schedule it from the start.

**PR #118 review split (R1+R2+R3 aggregate):** 34 ADOPT / 17 load-bearing / ~10% codex (role-mismatched, excluded from aggregate adopt-rate). Single biggest signal-per-round: R3 (5 errors-of-substance that would have shipped).

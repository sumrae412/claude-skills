# Session Handoff — 2026-05-27 — `evals` skill

## Goal

Ship the new `evals` skill PR (router + 5 phases + 3 references), respond to CodeRabbit / reviewer feedback, merge. Then decide on two optional follow-ups (workflow-learning capture into `debate-team/references/critic-calibration.md`; feedback memory for the agent).

## Current state

**Branch:** `docs/evals-philosophy-reference` (untracked changes only — nothing committed yet this session).

**Shipped this session:** nothing yet — /next is running the first commit + PR now.

**In-flight:** the working tree contains:
- `evals/SKILL.md` — router (137 lines)
- `evals/phases/phase-1-design.md` through `phase-5-production-evals.md` (1,111 lines across 5 phases)
- `evals/references/judge-calibration.md`, `outcome-grader.md`, `eval-philosophy.md` (433 lines across 3 references — `eval-philosophy.md` was authored by the user mid-session on this branch)
- `docs/plans/2026-05-27-evals-skill-modification-delta.md` — multi-round debate-team modification delta (R1 internal × 4, R2 DeepSeek + GPT-4o-codex, R3 GPT-5 with docs-tuned prompt). Records 34 ADOPTed mods and the per-mod ledger. Required by `debate-team/SKILL.md`'s multi-round mandate; ships atomically with the skill.

**Untouched (out of scope this session):**
- `prompt-governance/phases/phase-2-evals.md` (still a stub; the `evals` skill description points readers there for registry mechanics)
- `prompt-governance/phases/phase-4-policy-and-rollout.md` (also a stub; `evals/phase-5` now owns rollout-mechanics per Q1 decision)
- Open PR #65 (skill-standards-audit) and PR #60 (codex/structured-prompt-builder) — pre-existing, not touched by this session

## Exact next task

**If the PR opened by /ship is still under review:** address reviewer feedback. The diff is large (~1,700 lines of new docs) — expect CodeRabbit to flag prose density and possibly the `gpt-5-2025-08-07` reference in the modification delta as a recency claim. Defend: the model ID is a literal observation from the API response (`/tmp/debate_gpt5.json`), not a forward-looking claim.

**After merge — two optional follow-ups, in priority order:**

1. **Capture workflow learnings into `debate-team/references/critic-calibration.md`** (high value, ~30 min). Three lessons from this session:
   - *Convergence across critics is not correctness when training corpora overlap.* R1 (Anthropic internal) + R2-DeepSeek both endorsed a 10× sample-size folk-error; only R3-GPT-5 caught it. Rule: when N critics converge on a high-confidence *numeric* claim, that's a signal to run **one more cross-family critic**, not stop.
   - *The role-mismatch failure mode is structural, not model-quality.* Same OpenAI family produced 10% adopt rate (`--reviewer codex` with code-review system prompt) vs ~90% adopt rate (GPT-5 with docs-tuned system prompt) on the same artifact. PR #534 already named this in `critic-calibration.md`; this debate is the second documented instance. **Action:** either add a `--reviewer codex-docs` mode to `~/.claude/scripts/plancraft_review.py` (system prompt for docs artifacts, no code-quality vocabulary), or document the prompt-override pattern as the supported workaround.
   - *Statistical/methodological bugs are the highest-value third-critic finding.* R3-only catches: CI-overlap rule, sample-size formula, p-hacking-prone repetition rule, embedding-version pinning, paired-analysis omission. These are textbook errors that LLMs trained on online how-to content can all get wrong the same way.

2. **Save a `feedback` memory** so the agent doesn't repeat my "redundant, just synthesize" call: when a user asks for a third round and prior rounds were concordant + high-confidence, run it. Concordance amplifies the value of a cross-family check rather than reducing it.

## Template / reference PRs

- **#117** (`ad1a086`, "chore(skills): update GPT-4o references to GPT-5") — recent low-risk skill update; precedent for chore-style PRs touching skill content.
- **#114** (`8c19725`, "docs(skills): prompt-engineering router + agent-prompt-architecture sub-skill") — router + sub-skill pattern; the `evals` skill follows the same router-with-phases convention as `rag-architect` and `prompt-governance`.
- **#116** (`579fc12`, "docs(session-learnings): patterns from courierflow_beta PR #100") — example of session-learnings PRs; relevant if follow-up #1 above ships as a separate PR.

## Pre-flight commands

```bash
cd /Users/summerrae/repos/claude-skills
git fetch origin --prune
gh pr list --state open --limit 10
git status --short
cat docs/plans/2026-05-27-session-handoff.md
cat docs/plans/2026-05-27-evals-skill-modification-delta.md  # if needed for context
```

If the evals-skill PR is still open, also: `gh pr view <number> --comments` to read CodeRabbit / reviewer feedback.

## Architectural invariants to preserve

- **Skill router-with-phases pattern** — matches `rag-architect/SKILL.md` and `prompt-governance/SKILL.md`. Do not flatten to a single file even if the router seems thin.
- **`evals` exclusion-vs-content coherence** — the SKILL.md description now claims `evals/phase-5` owns rollout-mechanics (the eval signals that gate rollout); `prompt-governance` owns registry plumbing and approval policy. Don't reintroduce the old "NOT for A-B rollout" exclusion without also moving the content.
- **Calibration regime distinction (`phase-3` § "Calibration regime: measurement vs guardrail")** — measurement judges use κ ≥ 0.6; blocking guardrails use precision/recall on imbalanced traffic. Don't collapse them back to one rule.
- **Paired analyses for same-dataset A/B (`phase-4` § "Interpreting deltas")** — the doc explicitly teaches CI-on-the-paired-difference, not CI overlap. R3 caught this as a bug both R1 and R2 endorsed; the fix is load-bearing.
- **Sample-size formula in `phase-5` § "Pre-ramp definitions"** — n ≈ 2·p̄(1−p̄)·7.85/Δ² ≈ 9,800 per arm for p̄=0.5, Δ=0.02. Do not let a reviewer "tighten" this back to ~1,000 without a power-calc.

## Gates

This is a docs-only PR. No code touched. The relevant gates:

- **Markdown lint** if the repo runs one — check `.github/workflows/*.yml` before pushing.
- **CodeRabbit review** (automatic on PR open). Expect prose-density flags; defend with the multi-round debate-team rationale where appropriate.
- **No CI suite to run** — this is the claude-skills repo, not a code project.

## Ship instructions

`/ship` is the right path — this is a single coherent docs PR, not a multi-phase implementation. The handoff doc and modification delta ship atomically with the skill via the same PR.

Suggested PR title: `docs(skills): add evals skill (offline + production, multi-round reviewed)`.

PR body should call out:
- The skill (router + 5 phases + 3 references)
- The modification delta artifact and what it documents (R1+R2+R3 debate-team rounds, 34 ADOPTed mods, 17 load-bearing fixes)
- The five R3-caught statistical bugs that both R1 and R2 endorsed (these are the "why this took three rounds" headline)

## Mode directive

Auto mode. Surface premise contradictions only.

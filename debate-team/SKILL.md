---
name: debate-team
description: Cross-model adversarial review for plans and code with auto-tiering. Tier 1 (DeepSeek scope check, ~10x cheaper), Tier 2 (DeepSeek + GPT-4o dual critic), Tier 3 (full tri-model debate with Sonnet Generator + Opus Lead). Conditional Haiku Style critic for frontend. Use when reviewing plans or architecture decisions ("debate this", "review this plan", "second opinion", "is this approach right"), or for code reviews touching 3+ files / schema / security. Plans always get Tier 3. Also called by claude-flow Phase 3 (plan review) and Phase 6 (pre-merge review). Supports `--lite` and `--tier N` flags. NOT for brainstorming (stays interactive), TDD inner loop (own feedback), or single-file PR reviews (use review-pr).
---

# Unified Review — Debate Team

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad exploration, repeated file reads, multi-file scans, or heavy reference loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant patterns inline instead of loading extra material.


Cross-model adversarial review for plans and code. Three tiers auto-selected by complexity gate. Plans always get full debate (Tier 3). Code reviews scale from scope check to full debate based on file count, schema changes, and security sensitivity.

> **Absorbed PlanCraft:** Scope-check filtering (`OUT_OF_SCOPE` rejection) runs on every DeepSeek call at all tiers. PlanCraft as a standalone skill is archived.

## Setup

- Set **DEEPSEEK_API_KEY** and **OPENAI_API_KEY** in your environment (or a documented secure source). The script reads keys only from the environment; never put keys in plan files, scope files, or logs.
- The debate protocol is **single-user and serial** (one debate at a time). Fixed paths `/tmp/debate_artifact.md` and `/tmp/debate_scope.md` are acceptable; for parallel runs use unique paths (e.g. timestamp or UUID).

## When to Use

- **All plan/architecture reviews** → Tier 3 (full debate, always)
- **Bug fix plans** touching 3+ files or crossing service boundaries → Tier 3
- **Code reviews** with 3+ files or cross-cutting concerns → Tier 2 (dual critic)
- **Simple code reviews** (1-2 files, no schema/security) → Tier 1 (scope check)
- **User says "debate this"** → forces Tier 3
- **User says "quick review"** or caller passes `--lite` → forces Tier 1

## Flags

| Flag | Effect |
|------|--------|
| `--lite` | Force Tier 1 (DeepSeek scope check only). Skip dual-critic and Opus Lead. ~10x cheaper. Use for early iterations where a full debate would be wasted. Output carries a `tier: 1 (forced)` marker so the caller knows to re-run full debate before shipping. |
| `--tier N` | Force tier N explicitly (1/2/3). Overrides auto-tiering. |

`--lite` is the "lite version" of this skill — quick, cheap, and intentionally shallow. Full tri-model debate should still run before the plan is approved or the code lands.

## When NOT to Use

- User says "skip debate" — bypasses entirely
- Brainstorming phase (stays interactive with user)
- Implementation phase (TDD provides its own feedback loop)

## Team Composition

| Role | Model | Type | When |
|------|-------|------|------|
| Generator | Sonnet (teammate) | Agent Teams | Always |
| Bug-Hunter | DeepSeek (API) | External | Always |
| Architecture | GPT-4o via `--reviewer codex` (API) | External | Code artifacts only |
| Completeness | GPT-4o via `--reviewer codex-docs` (API) | External | Non-code artifacts only |
| Style/UI | Haiku (teammate) | Agent Teams | Frontend changes only |
| Lead/Judge | Opus (you) | Lead | Always |

**GPT-4o role routing:** The artifact type determines which GPT-4o critic role runs (never both):
- **Code artifacts** (touches `app/`, `tests/`, `*.py`, `*.js`, `*.css`, `*.html`) → Architecture critic (`--reviewer codex`): separation of concerns, abstraction quality, pattern consistency.
- **Non-code artifacts** (skills, docs, CLAUDE.md, MEMORY.md, process specs) → Completeness critic (`--reviewer codex-docs`): missing steps, contradictions, stale references, term consistency.


## Workflow

This skill uses progressive disclosure. Load the phase file for the step you're in; skip the others to keep context lean. All steps run sequentially — Step 4.5 only for Tier 3.

1. **Tier gate + proposal generation → load [`phases/tier-gate-and-proposal.md`](phases/tier-gate-and-proposal.md).**
   Step 1 (complexity gate — auto-tiering logic, file/schema thresholds, plan vs code routing) and Step 2 (generate the proposal to review). Always runs.

2. **Critic dispatch + synthesis → load [`phases/critics-and-synthesis.md`](phases/critics-and-synthesis.md).**
   Step 3 (parallel critic dispatch: DeepSeek / GPT-4o / Haiku Style, prompts per critic) and Step 4 (synthesize: anti-sycophancy protocol, classification). Always runs.

3. **Tier 3 extras + presentation → load [`phases/tier3-and-present.md`](phases/tier3-and-present.md).**
   Step 4.5 (Devil's Advocate challenge — Tier 3 only), Step 5 (present to user), Step 6 (auto-fix loop for PR review).

4. **Cost budget reference → load [`references/cost-budget.md`](references/cost-budget.md).**
   Per-tier dollar and token budgets; bail-out thresholds.

5. **Critic calibration → load [`references/critic-calibration.md`](references/critic-calibration.md).**
   Tracking critic signal quality, when to tune a critic prompt, grading method priority (Building Evals recipe), calibration cadence.

---

## Debugging

- If a critic run fails: re-run the same `plancraft_review.py` command with the same `--plan-file` and `--scope-file`, then inspect the JSON output. The `error` key (if present) explains the failure (e.g. missing API key, API timeout).
- If a batch review fails: re-run `batch_review.py` with the same `--artifact-file` and `--scope-file`. Check the JSON `error` key. Common causes: `anthropic` not installed, `ANTHROPIC_API_KEY` not set (check shell profile sourcing), batch timeout (increase `--timeout`).

## Extending: Adding New Critics

1. Create `debate-team/critics/<name>.md` following the frontmatter schema
2. Set `activation: always` or `activation: conditional` with `triggers`
3. The registry auto-discovers new files — no code changes needed

Full architecture: see CourierFlow repo `docs/plans/2026-03-07-tri-model-debate-team-design.md` (if present).

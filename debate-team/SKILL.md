---
name: debate-team
description: Unified review skill with auto-tiering — absorbs PlanCraft and adversarial-thinking. Tier 0 (single-conversation devil's advocate or steelman, no API calls — for pressure-testing ideas, plans, decisions, beliefs, strategies, startup concepts, arguments, or assumptions before incurring multi-model cost). Tier 1 (DeepSeek scope check). Tier 2 (DeepSeek + second critic). Tier 3 (full debate). Trigger phrases for Tier 0: "attack this idea", "devil's advocate", "steelman", "find flaws", "argue against", "understand the other side". In Codex, use Claude/Anthropic as the second external critic instead of GPT-5 unless the user explicitly requests GPT-5. Conditional Haiku Style critic for frontend.
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

- Set **DEEPSEEK_API_KEY** and either **ANTHROPIC_API_KEY** (Codex default) or **OPENAI_API_KEY** (Claude Code default / explicit GPT-5 request) in your environment. Scripts read keys only from the environment; never put keys in plan files, scope files, or logs.
- The debate protocol is **single-user and serial** (one debate at a time). Fixed paths `/tmp/debate_artifact.md` and `/tmp/debate_scope.md` are acceptable; for parallel runs use unique paths (e.g. timestamp or UUID).

## When to Use

- **Pressure-test an idea / plan / decision / belief / argument** (no code, no committed plan, no need for multi-model review) → Tier 0
- **User says "attack this idea", "devil's advocate", "steelman", "find flaws", "argue against", "understand the other side"** → forces Tier 0
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

## Tier 0 — Standalone Modes (No API Calls)

Pure-Sonnet single-conversation pressure testing. No DeepSeek, no GPT-5, no Claude critic, no Haiku. Use when the user wants to stress-test an idea, plan, or argument before incurring the multi-model cost of Tier 1+.

Two modes — infer from the request, ask only if unclear.

### Mode A — Devil's Advocate

Use for ideas, plans, strategies, product concepts, career moves, and decisions.

Output:

1. **Flawed Assumptions** — what the user is taking for granted that may be false.
2. **Execution Risks** — where the plan is likely to break in practice.
3. **Market / Human Reality** — behavior, incentives, institutions, or constraints the plan ignores.
4. **Fatal Flaw** — the one risk that could kill the idea entirely.

Rules:

- Criticize the idea, not the person.
- Be direct. Do not pad with encouragement.
- Skip obvious objections unless they have non-obvious consequences.
- Do not offer fixes unless the user asks for a second pass.
- End with: `The strongest argument against this in one sentence: …`

### Mode B — Steelman

Use when the user disagrees with a position and wants to understand why intelligent people hold it.

Output:

1. **Core Insight** — the fundamental truth the position is built on.
2. **Evidence** — data, history, mechanisms, or logic that support it.
3. **Where The User's View Is Weakest** — blind spots exposed by the opposing view.
4. **Strongest Single Argument** — one paragraph from a brilliant advocate.

Rules:

- Do not include counterarguments or caveats.
- Do not announce personal agreement or disagreement.
- Argue as if the view is genuinely persuasive.
- Keep the goal understanding, not conversion.

### Mode C — Single-component Tier 0 (variant of Mode A)

Use when a multi-component design is being built incrementally and a single component needs pressure-testing in isolation BEFORE downstream components commit to it. Smaller scope than typical Tier 0 (one component vs. full plan); the chair's job is **synthesis across specialists for one artifact**, not weighing a whole plan.

Process:

1. Pick 3 specialist personas for the component's surface (e.g. for an agent persona block: AI forward-deployed engineer + UI/UX specialist + product manager; for an API schema: backend engineer + API consumer + security reviewer).
2. Each specialist runs Mode A against ONLY the named component, scoped to their lens.
3. Chair synthesis identifies:
   - **Convergence** — findings ≥2 specialists flagged (highest-priority repairs).
   - **Distinct critical findings** — specialist-unique findings worth keeping.
   - **Fatal flaw** — the 1 cross-cutting pattern that, if uncorrected, propagates into downstream components.
   - **Recommended repairs (smallest-change ordering)** — concrete edits ordered by blast radius.
4. End with the standard Mode A close: `The strongest single argument against locking this as-is: …`

Validated on courierflow_beta [PR #100](https://github.com/sumrae412/courierflow_beta/pull/100) Charlie persona component — panel surfaced the "persona writes checks the architecture has to cash" failure mode and 5 distinct repairs the user adopted before downstream components committed. Cheaper than full Tier 3, tighter than a full-plan Tier 0.

### Optional second pass — attack → repair

If the user asks for improvements after a Devil's Advocate pass, switch from attack to repair:

- Keep the original fatal risks visible.
- Propose the smallest changes that address the highest-risk assumptions.
- Identify which risks remain unresolved.

When Tier 0 is not enough → escalate to Tier 1+ (the API-driven tiers below) for cross-model adversarial review.

## Team Composition

| Role | Model | Type | When |
|------|-------|------|------|
| Generator | Sonnet (teammate) | Agent Teams | Always |
| Bug-Hunter | DeepSeek (API) | External | Always |
| Architecture / Completeness | Claude/Anthropic critic (Codex default) or GPT-5 via `--reviewer codex` (Claude Code default / explicit request) | External | Always as second external critic |
| Style/UI | Haiku (teammate) | Agent Teams | Frontend changes only |
| Lead/Judge | Opus (you) | Lead | Always |

**Second critic routing:**
- **Codex runtime:** use Claude/Anthropic as the second external critic instead of GPT-5, unless the user explicitly requests GPT-5. Prompt Claude to review both architecture and completeness for the artifact type.
- **Claude Code runtime:** use the existing GPT-5 reviewer path unless the user explicitly requests Claude/Anthropic.
- **Code artifacts** (touches `app/`, `tests/`, `*.py`, `*.js`, `*.css`, `*.html`) → focus on separation of concerns, abstraction quality, API boundaries, schema/security risks, and project pattern consistency.
- **Non-code artifacts** (skills, docs, AGENTS.md, CLAUDE.md, MEMORY.md, process specs) → focus on missing steps, contradictions, stale references, term consistency, and operational clarity.


## Workflow

This skill uses progressive disclosure. Load the phase file for the step you're in; skip the others to keep context lean. All steps run sequentially — Step 4.5 only for Tier 3.

1. **Tier gate + proposal generation → load [`phases/tier-gate-and-proposal.md`](phases/tier-gate-and-proposal.md).**
   Step 1 (complexity gate — auto-tiering logic, file/schema thresholds, plan vs code routing) and Step 2 (generate the proposal to review). Always runs.

2. **Critic dispatch + synthesis → load [`phases/critics-and-synthesis.md`](phases/critics-and-synthesis.md).**
   Step 3 (parallel critic dispatch: DeepSeek / second external critic / Haiku Style, prompts per critic) and Step 4 (synthesize: anti-sycophancy protocol, classification). Always runs.

3. **Tier 3 extras + presentation → load [`phases/tier3-and-present.md`](phases/tier3-and-present.md).**
   Step 4.5 (Devil's Advocate challenge — Tier 3 only), Step 5 (present to user), Step 6 (auto-fix loop for PR review).

4. **Cost budget reference → load [`references/cost-budget.md`](references/cost-budget.md).**
   Per-tier dollar and token budgets; bail-out thresholds.

5. **Critic calibration → load [`references/critic-calibration.md`](references/critic-calibration.md).**
   Tracking critic signal quality, when to tune a critic prompt, grading method priority (Building Evals recipe), calibration cadence.

---

## Multi-round delta capture (mandatory)

When this skill runs a **second or later round** of review against an artifact that was already reviewed in a prior round (e.g. round 1 = plan-detail, round 2 = strategic; or any re-review after material edits), the skill MUST produce a **modification delta artifact** alongside the synthesized review. The delta is a separate file, not a section folded into the plan body.

Required contents of the delta artifact:

1. **One row per ADOPTed mod**, labeled `R<round>-NN`, with: target section in the artifact under review, one-line summary of the mod, source critic, and status (ADOPTED / DEFERRED / REJECTED).
2. **Round-N ↔ Round-(N-1) interaction map**: which current-round mods supersede, modify, or operationalize prior-round mods; which are net-new direction.
3. **Load-bearing list**: the subset of mods that, if dropped, would silently regress the artifact. This is the "future sessions must preserve these" list.
4. **Outstanding questions**: anything the round surfaced but didn't resolve, with a named owner or a fallback ("write this when work resumes").

Why this is mandatory: when round-N mods are folded back into the artifact body without per-mod labels, the audit trail is destroyed and future sessions cannot tell which mods are load-bearing vs. obsolete. This skill has historically produced exactly that failure mode.

**Output path:** `docs/plans/<date>-<artifact-slug>-modification-delta.md` (or repo's plan-doc convention). Link from the synthesized review's "next step" section.

**Applies to:** any debate-team invocation where the artifact under review has a prior debate-team artifact in `docs/plans/`, in MEMORY, or referenced in the prompt. Single-round reviews are exempt.

## Debugging

- The review scripts (`plancraft_review.py`, `batch_review.py`) live in the **CourierFlow repo** at `scripts/` (also mirrored to active worktrees). When invoking from a non-script context, find them with `find ~/claude_code/courierflow -name plancraft_review.py -not -path '*/node_modules/*' | head -1`. The scripts are not on PATH and not packaged as a CLI — invoke as `python3 <full-path>/plancraft_review.py ...`.
- If a critic run fails: re-run the same `plancraft_review.py` command with the same `--plan-file` and `--scope-file`, then inspect the JSON output. The `error` key (if present) explains the failure (e.g. missing API key, API timeout, HTTP 429 rate limit).
- If a batch review fails: re-run `batch_review.py` with the same `--artifact-file` and `--scope-file`. Check the JSON `error` key. Common causes: `anthropic` not installed, `ANTHROPIC_API_KEY` not set (verify via `zsh -ic 'echo $ANTHROPIC_API_KEY'` — bare Bash subshells don't inherit zshrc), batch timeout (increase `--timeout`), GPT-5 TPM rate limit on large artifacts (drop to Tier 2 — see `references/cost-budget.md` "Operational fallbacks").

## Extending: Adding New Critics

1. Create `debate-team/references/critics/<name>.md` following the frontmatter schema
2. Set `activation: always` or `activation: conditional` with `triggers`
3. The registry auto-discovers new files — no code changes needed

Full architecture: see CourierFlow repo `docs/plans/2026-03-07-tri-model-debate-team-design.md` (if present).

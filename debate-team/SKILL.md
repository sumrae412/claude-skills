---
name: debate-team
description: Unified review skill with auto-tiering — absorbs PlanCraft. Tier 1 (DeepSeek scope check), Tier 2 (DeepSeek + GPT-4o dual critic), Tier 3 (full tri-model debate with Sonnet Generator + Opus Lead). Conditional Haiku Style critic for frontend.
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
- If keys were ever pasted into the chat transcript (even briefly), source them from `~/.zshrc` or another shell-profile file rather than the conversation buffer. The auto-mode safety classifier will (correctly) block external-API calls when chat-leaked keys are co-located with content-sending tools; this is an exfil pattern, not a bug.

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

## Cross-family critic for statistical/empirical claims

When an artifact contains load-bearing **numeric claims** (sample-size formulas, statistical-test choices, CI rules, power calculations, throughput/latency targets, cost models), the standard DeepSeek + GPT-4o pair is insufficient — both families train heavily on the same web tutorials and co-endorse the same folk errors. **Add a third critic from a different family** (e.g., GPT-5, Gemini, Claude-non-Lead) with a domain-tuned system prompt before the artifact ships.

**Trigger:** any claim of the form "use N samples", "p < X", "CI overlap means…", "this scales as O(…)", or any cited formula.

**Anti-pattern:** stopping after two same-family critics endorse a numeric claim. That convergence is the *signal to escalate*, not the signal to ship. See `references/critic-calibration.md` PR #118 entry.

## Debugging

- If a critic run fails: re-run the same `plancraft_review.py` command with the same `--plan-file` and `--scope-file`, then inspect the JSON output. The `error` key (if present) explains the failure (e.g. missing API key, API timeout).
- If a batch review fails: re-run `batch_review.py` with the same `--artifact-file` and `--scope-file`. Check the JSON `error` key. Common causes: `anthropic` not installed, `ANTHROPIC_API_KEY` not set (check shell profile sourcing), batch timeout (increase `--timeout`).
- `plancraft_review.py --reviewer codex-docs` is not implemented; the script hardcodes a code-reviewer system prompt and `gpt-4o`. For non-code artifacts, write a small wrapper (see `/tmp/gpt5_doc_critic.py` from PR #118) with a docs-tuned system prompt — code-review vocabulary produces ~10% ADOPT rate on docs vs ~90% with the docs prompt.

## Extending: Adding New Critics

1. Create `debate-team/critics/<name>.md` following the frontmatter schema
2. Set `activation: always` or `activation: conditional` with `triggers`
3. The registry auto-discovers new files — no code changes needed

Full architecture: see CourierFlow repo `docs/plans/2026-03-07-tri-model-debate-team-design.md` (if present).

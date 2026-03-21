---
name: debate-team
description: Tri-Model Debate Team — cross-model adversarial review using DeepSeek Bug-Hunter, GPT-4o Architecture, and conditional Haiku Style critics
---

# Tri-Model Debate Team

Cross-model adversarial review for plans and PRs. Three different "training DNAs" (Anthropic, OpenAI, DeepSeek) critique every artifact from different angles.

## Setup

- Set **DEEPSEEK_API_KEY** and **OPENAI_API_KEY** in your environment (or a documented secure source). The script reads keys only from the environment; never put keys in plan files, scope files, or logs.
- The debate protocol is **single-user and serial** (one debate at a time). Fixed paths `/tmp/debate_artifact.md` and `/tmp/debate_scope.md` are acceptable; for parallel runs use unique paths (e.g. timestamp or UUID).

## When to Use

- **Planning phases 4-5**: Architecture proposals, implementation plans
- **PR review**: Code diffs ready for review
- **User says "debate this"**: Manual override to force debate on any artifact

## When NOT to Use

- Simple 1-2 file changes (use standard review-pr skill)
- Brainstorming phase (stays interactive with user)
- Implementation phase (TDD provides its own feedback loop)
- User says "skip debate"

## Team Composition

| Role | Model | Type | When |
|------|-------|------|------|
| Generator | Sonnet (teammate) | Agent Teams | Always |
| Bug-Hunter | DeepSeek (API) | External | Always |
| Architecture | GPT-4o (API) | External | Always |
| Style/UI | Haiku (teammate) | Agent Teams | Frontend changes only |
| Lead/Judge | Opus (you) | Lead | Always |

## Protocol

### Step 1: Assess Complexity

Decide if this artifact warrants a full debate:

```
Is this worth debating?
├─ PLANNING: Task touches 3+ files OR cross-cutting concerns? → debate
├─ PR REVIEW: Diff touches 3+ files OR security-sensitive code? → debate
├─ User override: "debate this" → debate, "skip debate" → skip
└─ Otherwise → use traditional review (plancraft_review.py with --reviewer)
```

If skipping debate, announce: "Skipping debate — [reason]. Using standard review."

### Step 2: Generate Proposal

Spawn the **Generator** (Sonnet teammate) with the task context:

```
Use Task tool:
  subagent_type: general-purpose
  model: sonnet
  name: generator
  prompt: [full task context + "Write a complete [plan/code] proposal. Save to /tmp/debate_artifact.md"]
```

Wait for Generator to complete. Read the artifact.

### Step 3: Dispatch Critics (Parallel)

Run ALL applicable critics in parallel (one message, multiple tool calls):

**Always run — DeepSeek Bug-Hunter + GPT-4o Architecture (parallel Bash calls):**

```bash
# DeepSeek Bug-Hunter
python3 ~/.claude/scripts/plancraft_review.py \
  --mode bug-hunter \
  --input-type [plan|diff] \
  --plan-file /tmp/debate_artifact.md \
  --scope-file /tmp/debate_scope.md

# GPT-4o Architecture (parallel)
python3 ~/.claude/scripts/plancraft_review.py \
  --mode architecture \
  --input-type [plan|diff] \
  --plan-file /tmp/debate_artifact.md \
  --scope-file /tmp/debate_scope.md
```

**Conditionally run — Haiku Style/UI (if frontend changes detected):**

Check if artifact references files matching: `*.html`, `*.css`, `*.js`, `templates/**`, `static/css/**`

If yes, spawn Haiku teammate:
```
Use Task tool:
  subagent_type: general-purpose
  model: haiku
  name: style-critic
  prompt: [Style/UI critic prompt from critics/haiku-style-ui.md + the artifact]
```

### Step 4: Synthesize

Read all critic outputs. For EACH finding:

| Decision | When |
|----------|------|
| **ADOPT** | Finding is valid, actionable, in-scope |
| **REJECT** | False positive or already addressed |
| **DEFER** | Valid but needs user decision (trade-off, preference, or pre-existing fix that would significantly expand the PR) |

Produce a **Changelog table**:
```
| Source | Finding | Decision | Reasoning |
|--------|---------|----------|-----------|
| DeepSeek | N+1 query in Task 3 | ADOPT | Add .joinedload() |
| GPT-4o | Over-abstracted service layer | REJECT | Matches existing pattern |
| Haiku | Hardcoded font-size | ADOPT | Use var(--ds-text-sm) |
```

### Step 5: Present to User

Show the user:
1. **The final artifact** (with all ADOPT fixes applied)
2. **The Changelog** (adopt/reject/defer with reasoning)
3. **Any DEFER items** that need user decision

### Step 6: Auto-Fix Loop (PR Review Only)

If reviewing a PR and CRITICAL findings were adopted:

1. Assign fixes to Generator (Sonnet teammate)
2. Generator commits fixes
3. Re-run critics on updated diff
4. **Max 2 cycles** — if unresolved after 2, escalate to user

## Cost Budget

- Per debate round: ~$0.08-0.10 (based on ~10k prompt + ~1k completion tokens per critic at current DeepSeek/OpenAI pricing).
- Max per feature (3 rounds): ~$0.30
- Token cap per critic call: 15,000 tokens

## Debugging

- If a critic run fails: re-run the same `plancraft_review.py` command with the same `--plan-file` and `--scope-file`, then inspect the JSON output. The `error` key (if present) explains the failure (e.g. missing API key, API timeout).

## Extending: Adding New Critics

1. Create `debate-team/critics/<name>.md` following the frontmatter schema
2. Set `activation: always` or `activation: conditional` with `triggers`
3. The registry auto-discovers new files — no code changes needed

Full architecture: see CourierFlow repo `docs/plans/2026-03-07-tri-model-debate-team-design.md` (if present).

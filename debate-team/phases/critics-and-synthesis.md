### Step 3: Dispatch Critics (Parallel)

Run ALL applicable critics in parallel (one message, multiple tool calls):

**Always run — DeepSeek Bug-Hunter + second external critic:**

In **Codex runtime**, the second external critic is **Claude/Anthropic** by
default, not GPT-4o. Use GPT-4o only when the user explicitly requests it.
Prompt Claude to review the same `/tmp/debate_artifact.md` and
`/tmp/debate_scope.md`, focusing on architecture, completeness, sequencing,
security/privacy, and scope control.

In **Claude Code runtime**, keep the historical GPT-4o path unless the user
explicitly asks to use Claude/Anthropic.

```bash
# Export tier so the review ledger captures which tier triggered this run.
# Set REVIEW_TIER to the tier chosen in Step 1 (T1 / T2 / T3). Unset = tier null in telemetry.
export REVIEW_TIER=T2

# DeepSeek Bug-Hunter (always)
python3 ~/.claude/scripts/plancraft_review.py \
  --reviewer deepseek \
  --plan-file /tmp/debate_artifact.md \
  --scope-file /tmp/debate_scope.md

# Codex default second critic: Claude/Anthropic.
# Use a local script or one-off Python reviewer that reads only
# /tmp/debate_artifact.md and /tmp/debate_scope.md, then calls Anthropic.
# Do not send secrets, environment dumps, or unrelated repo content.
python3 /tmp/claude_plan_review.py

# Claude Code / explicit GPT-4o path — pick ONE based on IS_CODE / IS_NON_CODE:

# If IS_CODE → Architecture critic (parallel)
python3 ~/.claude/scripts/plancraft_review.py \
  --reviewer codex \
  --plan-file /tmp/debate_artifact.md \
  --scope-file /tmp/debate_scope.md

# If IS_NON_CODE → Completeness/Consistency critic (parallel)
python3 ~/.claude/scripts/plancraft_review.py \
  --reviewer codex-docs \
  --plan-file /tmp/debate_artifact.md \
  --scope-file /tmp/debate_scope.md
```

**Claude Batch Reviewer (Tiers 2-3 only):**

**Prerequisite:** `python3 -c "import anthropic"` succeeds and `ANTHROPIC_API_KEY` is set.

Run in parallel with DeepSeek + second external critic:
```bash
python3 ~/.claude/scripts/batch_review.py \
  --mode plan-review \
  --artifact-file /tmp/debate_artifact.md \
  --scope-file /tmp/debate_scope.md \
  --timeout 300
```

If batch completes before synthesis step: merge findings into Step 4.
If batch times out or errors: proceed without (graceful degradation).
User says `"skip batch"`: omit the Claude batch reviewer (keeps DeepSeek + second critic only).

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

#### Anti-Sycophancy Protocol

Before classifying findings, the Lead MUST:

1. **Read each critic's output in isolation** — Form a preliminary ADOPT/REJECT per finding BEFORE reading the next critic's output. This prevents anchoring on the first opinion.
2. **Weight lone dissent heavily** — If all critics flag the same issue, that's signal. If only ONE critic flags it, give it EXTRA attention (not less) — lone dissent often catches what groupthink misses.
3. **Challenge your own ADOPTs** — For each ADOPT decision, ask: "Would I still adopt this if no critic had flagged it?" If no, downgrade to DEFER.

#### Classification

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
| Claude | Over-abstracted service layer | REJECT | Matches existing pattern |
| Haiku | Hardcoded font-size | ADOPT | Use var(--ds-text-sm) |
```

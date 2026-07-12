---
name: forward-claim-checkpoint
description: Use whenever writing a checkpoint summary, slice/phase status update, progress report, or any load-bearing claim that a user might say "keep going" based on. Forces explicit covered-vs-inferred enumeration to prevent silent extrapolation. Fires on prose like "checkpoint", "Phase N complete", "slice X done", "I'm confident", "should handle", "tomorrow I'll", "remaining items", "by analogy with", "same pattern", or any forward-tense confidence about untouched code.
---

# Forward-claim checkpoint protocol

A "load-bearing claim" is any statement that drives an approve/proceed decision in the reader's mind. Before writing one, emit a structured checkpoint using THIS schema, not free prose.

This skill exists because forward-tense extrapolation ("the pattern will handle the next case") is a recurring failure mode — verified case to unverified case in one sentence, with no signal for the reader to intercept. The skill makes the extrapolation explicit.

## Required schema

All four sections, in order. Empty sections allowed where genuinely empty — say so explicitly rather than omitting.

### Verified
What was actually run, with command and result. Cite concrete evidence (`file_path:line`, command output, test result line, `git diff --stat`).

Examples:
- "Ran `uv run pytest tests/test_webhook_idempotency.py`: 3/3 passed."
- "Read `app/models/billing.py:120-180`; column types match expected."
- "`git diff --stat` shows 3 files changed, +47/-12."

If empty: "Nothing verified yet — pure design/planning state."

### Covered surfaces
Specific properties the verification tested. Be granular. One property per line.

Examples:
- Column type preservation (SQLAlchemy `Column` → SQLModel `Field`).
- Index preservation under `__table_args__` tuple.
- Round-trip insert/select via async session.

If empty: "No surfaces covered (e.g., planning checkpoint with no execution yet)."

### Inferred (NOT verified)
Surfaces in the next/uncovered case that DIFFER from the covered ones. If genuinely none (cases are structurally identical by clear definition), say "empty — cases structurally identical: [reason]".

Examples:
- FeatureFlag adds `JSON` column with mutable default (NOT in PoC).
- OAuthToken adds cross-style FK to non-SQLModel `User.id` (NOT in PoC).
- OAuthToken has `@property`-derived fields + Pydantic v2 (NOT in PoC).

If empty AND structurally identical: "empty — cases structurally identical (same model class, same ORM relationship pattern, different row data)."

### Decision needed
What the reader is being asked to decide. If no decision needed, say so.

Examples:
- "Proceed on extrapolation, or probe inferred surfaces (~30s) first?"
- "Reframe scope — OAuthToken inferred surfaces are too distant from PoC to extrapolate safely."
- "No decision — purely informational status update."

## Short-form variant

For inline mentions inside longer messages where the full structured form would be overkill:

```
[checkpoint: verified WebhookIdempotency (Column→Field, indexes, round-trip);
inferred FeatureFlag (table_args, JSON), OAuthToken (FK, @property);
probe?]
```

Long-form for standalone checkpoint messages; short-form for inline citations.

## When to use this skill vs. free prose

**Use the skill** when:
- The message will drive an approve/proceed decision (the reader might say "keep going" based on it).
- The message contains a forward-tense claim about untested code.
- The message is a "Phase N complete" / "Slice X done" / "checkpoint" / "status update."
- You catch yourself writing "I'm confident," "should handle," "tomorrow I'll," "same pattern, just applied to," "by analogy with," or any phrase from the user-CLAUDE Guardrail 2 trigger list.

**Skip the skill** when:
- The message is a conversational acknowledgment, question, or clarification.
- The message is purely past-tense and the past-tense `completion-claim-verifier` hook covers it.
- Cases are structurally identical by clear definition (same model + different row, same endpoint + different valid input, same well-typed algorithm + different parameter). If you'd write "similar but different" or "same kind of thing as," they are NOT structurally identical — use the skill.

## Pairing with `/checkpoint-critic`

For load-bearing claims > 100 words, draft the structured checkpoint via this skill, then run `/checkpoint-critic` on the draft before shipping. The critic externalizes the noticing step to a subagent without your autopilot.

## Composition with other layers

This skill is one of five enforcement layers from `docs/plans/2026-05-11-confidence-overclaim-fix.md`:

| Layer | Mechanism | Fires when |
|---|---|---|
| L1 (Stop hook) | `forward-claim-evidence-check.sh` | Retroactively, every turn |
| **L2 (this skill)** | Structured schema | When you invoke it |
| L3 (`/checkpoint-critic`) | Critic subagent | When you invoke it |
| L4 (user + project CLAUDE.md) | Ambient prose | Always loaded |
| L5 (memory entry) | Cross-linked memory | Always loaded |

No layer is bulletproof. Use this skill on load-bearing claims and accept that you may forget; the hook catches retroactively when you do.

## Why this exists

Decision: `~/claude_code/courierflow/docs/decisions/2026-05-11-confidence-overclaim-discipline-failure.md` (in the CourierFlow legacy repo). Recurring failure mode: extrapolation from a narrow verified case to broader uncovered surfaces in prose, with no signal for the user to intercept. Composes with `feedback_spike_unfalsifiable_when_prop_unaccessed.md` (same genus on a different artifact) and `feedback_verify_premise_before_executing_contradictory_plan.md` (premise-verification before acting).

---
name: session-handoff
description: Document a dead end so future sessions avoid re-exploring. Writes an abandon record to .claude/abandoned/<date>-<topic>.md capturing what was tried, why it failed, and what was learned. Invoked as `/session-handoff --abandon`, or when the user says "abandon this", "this didn't work", "scrap this approach", or "dead end". Also used by claude-flow Phase 1 (Explore/Archive path) and the research skill. Normal state-export handoffs are written by the `next` skill to docs/plans/<date>-session-handoff.md — not by this skill.
user-invocable: true
---

# Session Handoff — Abandon Mode

Archive failed approaches so future sessions don't re-explore them. The record becomes
visible as "previously ruled out" context at the next SessionStart.

## When to invoke

- User says "abandon this", "this didn't work", "scrap this approach", "dead end"
- `/session-handoff --abandon` (explicit invocation)
- `claude-flow` Phase 1 Explore → Archive path (invoked automatically)
- `research` skill recommends this when a line of investigation hit a wall

## What this skill does NOT do

- **Normal state export for cross-session resume** — that's the `next` skill's job. It writes a
  narrative handoff doc to `docs/plans/<date>-session-handoff.md` and commits it.
- **Post-commit learning capture** — that's `anthropic-skills:session-learnings` (+
  `anthropic-skills:consolidate-memory`).

## The process

### Step 1 — Gather abandon context

Collect:
- Current branch (`git branch --show-current`)
- Modified files (`git diff --name-only` and `git diff --cached --name-only`)
- Phase/step if claude-flow is active (read `.claude/workflow-state.json` if present)

Then ask the user (or infer from conversation):
- **What was the approach?** The specific thing that was tried.
- **Why is it being abandoned?** Technical limitation, wrong direction, better approach found.
- **What was learned?** Insight worth preserving so future attempts don't re-explore.

### Step 2 — Write the abandon record

Create `$PROJECT/.claude/abandoned/` if needed. Write to
`$PROJECT/.claude/abandoned/YYYY-MM-DD-<topic>.md`:

```markdown
# Abandoned: <topic>
**Date:** YYYY-MM-DD
**Branch:** feature/xyz (deleted / kept for reference)

## What was attempted
Brief description of the approach and what was built.

## Why abandoned
- Reason 1
- Reason 2

## What was learned
- Insight that should inform future attempts
- Technical discovery worth preserving

## Files modified
- `path/to/file.py` — what was changed
```

### Step 3 — Clean up

- If on a feature branch with no commits worth keeping: offer to delete the branch
- If on a feature branch with useful partial work: note "kept for reference" in the record
- Remove `.claude/handoff.md` if it exists (stale state dump from the retired normal mode)

### Step 4 — Announce

Tell the user:
- Path to the abandon record
- That the SessionStart hook surfaces the `abandoned/` dir contents as "previously ruled out"
  context in future sessions
- Whether the branch was deleted or kept

## MCP integration

The `claude-flow` MCP server exposes `.claude/abandoned/*.md` as resources; MCP-speaking
clients can read abandon records programmatically without parsing files.

## Related

- `next` — writes durable narrative handoffs for active work streams (different artifact, different purpose)
- `anthropic-skills:session-learnings` — captures learnings after successful commits
- `claude-flow` Phase 1 — the Explore/Archive path invokes this skill automatically

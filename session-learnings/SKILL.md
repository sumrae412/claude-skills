---
name: session-learnings
description: Capture lessons after commits
license: MIT
metadata:
  author: summerela
  version: "1.0.0"
---

# Session Learnings

## Overview

After major commits, dispatch a background agent to reflect on what was learned and propose updates to skills and project docs. The agent analyzes both **code diffs** and **session conversation** to find new patterns, bug lessons, user corrections, and conventions that should be documented.

After writing individual memory files, the agent also runs a **compilation step** that consolidates related memories into concept articles under `memory/knowledge/concepts/`. This reduces fragmentation and creates cross-referenced knowledge. See Step 2b in [`references/dispatch-agent.md`](references/dispatch-agent.md).

**Core principle:** The conversation is the richest source of learnings. Code diffs show *what* changed; session events show *why* and *what went wrong first*.

## Memory File Convention: `## Related` Footer

When writing a new memory file (topic-slug-named, one per learning), end it with an optional `## Related` section listing 2–4 neighbor memory files that share context. Plain markdown, one line per neighbor:

```markdown
## Related
- [neighbor_slug] — one-line reason they relate
- [other_slug] — ...
```

`slug` is the filename without `.md` (e.g. `fold_check_upstream` → `fold_check_upstream.md`).

Why this matters: `claude-flow/references/memory-injection.md` reads `## Related` footers for 1-hop relational retrieval (Step 4a). When a gotcha matches a subagent's file scope, co-cited neighbors get pulled in too — capped at 3 additions per injection, additive to Section 1's 10-entry cap, co-citation scored for tiebreak. Graceful no-op when the footer is absent, so adding it is strictly additive value. Add it only when genuine relationships exist; do not force-link.

## When to Use

Proactively invoke after:
- Committing a significant feature or bug fix
- A debugging investigation that uncovered root causes
- The user correcting your approach ("that's wrong, do it this way")
- Discovering a new convention or component pattern
- A spec review catching missing pieces (these are valuable docs/skill updates)
- A code review catching N+1, race conditions, duplicates (anti-patterns to document)
- Any session that produced cross-cutting changes (3+ files for same reason = policy)
- Skills were modified (triggers cross-reference audit across all skills)

## The Process

### Step 1: Compile Session Context

Before dispatching the background agent, compile a structured summary from the conversation:

```
SESSION CONTEXT:
- User corrections: [list times user said something was wrong or needed changing]
- Bugs investigated: [root causes found, what was misleading]
- Patterns established: [user said "make this the default", "always do X"]
- Gotchas hit: [security hooks, env quirks, API limitations, workarounds]
- Investigation conclusions: ["feature never existed", "regression from cherry-pick"]
- New components built: [UI components, utilities, patterns that others should reuse]
- Spec review catches: [things spec reviewer found missing before implementation]
- Code quality catches: [N+1 queries, race conditions, duplicate code found in review]
- Cross-cutting changes: [same rule applied to 3+ files = policy; needs memory entry]
- Skills modified: [which skills were edited and why — triggers cross-reference audit]
- Abandoned approaches: [check .claude/abandoned/ for records created this session —
  ensure they are reflected in MEMORY.md entries so future sessions don't re-explore]
- Failure events: [read memory/episodic/failure-events.jsonl for this session's events —
  count by type, note any failure:unresolved, list novel patterns added to catalog]
```

### Step 2: Dispatch Background Agent

Load [`references/dispatch-agent.md`](references/dispatch-agent.md) and pass its contents as the `prompt:` field of a `Task` tool call with `subagent_type: general-purpose` and `run_in_background: true`. The reference contains the full agent brief: write-access scope (MEMORY.md auto-applied; skills/CLAUDE.md proposed-only), Step 2b memory-compilation pipeline (cluster → consolidate → cross-reference), and the output contract.

### Step 3: Present Results

When the background agent completes (check via TaskOutput):

1. Read the agent's output
2. Present a concise summary: "Session learnings found **N updates** across **M targets**"
3. Note which MEMORY.md updates were **already applied** (written + committed + pushed by the agent)
4. List remaining skill/CLAUDE.md proposals with their 1-line reasons
5. Ask: "Apply all / select which ones / skip?" (for the proposals only)

### Step 4: Apply Approved Proposals

For each approved skill/CLAUDE.md proposal:
- Read the target file
- Make the edit (matching existing style — patterns numbered sequentially, checklist items appended, etc.)
- Confirm each edit succeeded

**MEMORY.md is auto-applied** by the background agent (no approval needed — it's the agent's own learnings repo).
**Skills and CLAUDE.md require approval.** The background agent proposes; the user decides.

## Gotchas

**`projects/` gitignore + new memory files:** Memory files under `~/.claude/projects/<slug>/memory/` are covered by `projects/` in `~/.claude/.gitignore`. New memory entries must be added with `git add -f`. Bare `git add .` from the memory dir fails silently with "paths ignored" and does NOT stage the new file. Pre-existing tracked memory files update normally; only NEW files hit the ignore gate. The background agent must use `git add -f <file>` when creating new topic-slug memory files.

## Reusable Conventions and Example

See [`references/conventions-and-examples.md`](references/conventions-and-examples.md) for the test-script resolver helper pattern (`_resolve_script(name)` for skill-internal script paths that may have moved during consolidation) and a worked example of a SESSION CONTEXT block from a real bulk-action-bar session.

## Red Flags

| Thought | Reality |
|---------|---------|
| "Nothing notable happened this session" | User corrections alone are worth capturing |
| "The code diff tells the whole story" | Session context (corrections, investigations) is richer |
| "I'll remember this for next time" | You won't. Next session starts fresh. Document it now. |
| "This is too minor to document" | Minor gotchas (security hooks, worktree quirks) save the most time |
| "I already updated skills manually" | Run the agent anyway — it may catch things you missed |
| "I only changed one skill" | Other skills may reach the same outcome via a different path. Cross-reference audit catches these. |
| "The change is self-documenting" | If 3+ files changed for the same reason, it's a policy. Future sessions won't read all those files — they need a memory entry. |
| "I'll run multiple agents in parallel for speed" | Parallel subagents doing git commits in the same worktree cause conflicts. Serialize commits or use separate worktrees per agent. |
| "I'll run session-learnings at the end" | "End" never comes if there are more commits. Run it after each significant commit cluster, not at session close. |

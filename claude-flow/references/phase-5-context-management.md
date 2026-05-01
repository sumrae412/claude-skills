# Phase 5 Context Management

Load this reference only when:

- the implementation loop is long enough to threaten context limits
- you are dispatching multiple implementation subagents
- compaction behavior itself is the thing under discussion

Keep it out of the default Phase 5 hot path for short, contained work.

## Strategy 1: Tool-Result Clearing

Phase 2 often reads 8-15 files. By Phase 5 those raw reads are stale context
bloat.

Use tool-result clearing during Phases 4-6 when context grows:

```text
Trigger:     context exceeds ~50K tokens
Keep:        4 most recent tool results
Exclude:     MEMORY.md reads
Clear:       at least 10K tokens per event
```

Cleared:

- old file reads
- grep output
- stale API responses

Retained:

- tool_use records
- reasoning
- user messages
- advisor responses

## Strategy 2: Phase-Aware Compaction

Soft threshold:

- around 60% capacity, prepare a compact summary

Hard threshold:

- around 80% capacity, compact with Phase 5 preservation rules

During Phase 5 preserve:

- plan with completion state per step
- current step context
- files modified so far
- current test status
- still-relevant advisor guidance

Drop:

- old test output
- already-completed step narration

## Strategy 2.5: Compaction History Ledger

When compaction happens during implementation, keep a structured ledger
alongside the prose summary. The summary helps the next executor reorient;
the ledger preserves exact facts that should not be paraphrased away.
Prefer storing exact details in the run event log and keeping the visible
ledger as a table of contents with lookup handles.

Record ledger entries for:

- completed plan steps and their status
- exact intermediate results: IDs, file paths, command exit codes, hashes,
  generated names, failing assertions, and reviewer finding IDs
- current file state: files modified, files intentionally left untouched, and
  any user-owned changes observed in the worktree
- decisions that affect future steps, with the rejected alternative when it
  prevents re-litigation
- unresolved blockers and the next concrete command or file read

Use compact, machine-readable shapes where possible:

```json
{
  "type": "phase5_compaction_ledger",
  "completed_steps": [1, 2],
  "current_step": 3,
  "modified_files": ["scripts/export_run_timeline.py"],
  "event_log_path": ".claude/runs/2026-04-29T10-00-00.events.jsonl",
  "lookup_queries": [
    "scripts/export_run_timeline.py command exit_code",
    "phase5 blocker current_step"
  ],
  "facts": [
    {
      "kind": "command",
      "value": "pytest scripts/test_export_run_timeline.py -q",
      "exit_code": 0
    }
  ],
  "next_action": "Run workflow asset tests"
}
```

Do not rely on memory of prior narration after compaction. Reconstruct from the
ledger first, then use the prose summary for nuance. This mirrors recursive
inference systems that compact the visible conversation while keeping a
retrievable history object for exact intermediate values.

Before asking the user to repeat prior context after resume, inspect:

1. `.claude/workflow-state.json`
2. the manifest path stored as `run_manifest_path`
3. the manifest's `event_log_path`
4. project memory or Context Mode search, if available

## Strategy 3: Contract-Scoped Subagent Context

Phase 5 consumes:

- `$verified_plan` or `$plan`
- `$exploration`
- `$requirements`
- `$test_skeletons` for full path

Never pass to implementer subagents:

- advisor transcripts
- rejected architectures
- Phase 0 loading decisions
- raw clarification Q&A

## Fresh Context for Long Loops

If a plan has 5+ sequential steps and the session is getting heavy:

1. capture step completion state
2. compact using the preservation rules above
3. continue with a clean working context

For subagent dispatch, give each subagent only:

- assigned step(s)
- key file paths and patterns
- defensive patterns to apply
- prior `$diff.context_facts` entries

No prior step narration. The plan is the contract.

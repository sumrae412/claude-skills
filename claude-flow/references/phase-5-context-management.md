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

---
name: research
description: Multi-agent research team
user-invocable: true
---

# Research

## Overview

Multi-agent research team that explores a question in depth across codebase, git history, external docs, and API references. Produces a confidence-scored research brief.

**Standalone:** `/research "your question here"`
**Integrated:** Called by claude-flow Phase 2 when task path is `full` or `complex`.

**Announce:** "Running research team — classifying task, dispatching researchers, synthesizing findings."

## Flags

| Flag | Effect |
|------|--------|
| `--lite` | Wave 1 only. Skip gap detection and Wave 2 fill. Dispatch 2 researchers instead of 2–4. Synthesizer produces a brief with an explicit `coverage: partial` marker. ~60% cheaper; use for early iterations, quick sanity checks, or "just tell me roughly" queries. Full research should still run before a plan is written. |
| `--waves N` | Cap waves at N (default 2). `--waves 1` is equivalent to `--lite`. |

`--lite` is the "lite version" of this skill — narrow scope, fewer researchers, no gap-filling. The confidence scoring still applies, so consumers can see which findings are shaky.

---

## Orchestrator (Inline Executor)

The orchestrator runs inline as the Sonnet executor (not a subagent). It coordinates the full pipeline:

1. Read research request (from user directly or Phase 2 handoff)
2. Classify task using smart-exploration's 9 categories
3. Select 2-4 researchers from the pool based on task type
4. Compose Wave 1 prompts (inject gotchas per `claude-flow/references/memory-injection.md` if in workflow context)
5. Dispatch Wave 1 researchers in parallel via Agent tool
6. Read Wave 1 scratchpad entries, run gap detection
7. If gaps found → dispatch Wave 2 gap-fillers (1-2 researchers)
8. Dispatch synthesizer agent
9. Return confidence-scored research brief

### Task Classification

Use smart-exploration's 9 categories to determine researcher mix. Read the task request + any mentioned files/areas to classify:

| Category | Signal |
|----------|--------|
| `endpoint` | API routes, controllers, handlers |
| `ui` | Templates, components, CSS, state |
| `data` | Models, migrations, queries, schema |
| `integration` | External APIs, webhooks, third-party services |
| `refactor` | Restructuring without behavior change |
| `bugfix` | Defect tracing, unexpected behavior |
| `config` | Env vars, infrastructure, deployment |
| `exploration` | Spike, prototype, feasibility |
| `general` | Doesn't fit a specific category |

---


## Workflow

This skill uses progressive disclosure. Load the phase file for the stage you're in; skip the others to keep context lean.

1. **Dispatch researchers → load [`phases/researchers.md`](phases/researchers.md).**
   The 4 researcher types (Codebase Explorer, External Researcher, Integration Mapper, History Analyst) with their subagent prompt blocks and response schemas. Needed at Wave 1 (step 5) and Wave 2 (step 7) dispatch time.

2. **Select researchers + run waves → load [`phases/waves.md`](phases/waves.md).**
   Default researcher selection by task category, Wave 1 parallel dispatch, gap detection heuristics, Wave 2 targeted gap-fill, skip conditions for single-shot runs (covers orchestrator steps 3-7).

3. **Synthesize findings → load [`phases/synthesizer.md`](phases/synthesizer.md).**
   Synthesizer agent prompt and the confidence-scored research brief output schema (orchestrator step 8-9).

---

## Integration with claude-flow

When called from Phase 2:

1. The workflow passes the task description and path classification
2. Research skill runs its full pipeline (classify → Wave 1 → gap detection → Wave 2 → synthesize)
3. Research brief is returned to the workflow
4. The brief replaces the current exploration output
5. The Opus advisor checkpoint (Step 3 of Phase 2) reviews the research brief
6. Confidence scores are included in the `$exploration` variable that feeds Phases 3-6

When called standalone:

1. User invokes `/research "question"`
2. Orchestrator classifies and dispatches
3. Research brief is displayed directly to the user
4. No workflow integration, no phase transitions

---

## Next Steps

- **Ready to build from findings?** Use `/claude-flow` to run the full implementation pipeline (research feeds Phase 3 automatically).
- **Need to capture a dead end?** Use `/session-handoff --abandon` to document what didn't work before moving on.
- **Want to verify assumptions?** If `/fetch-api-docs` is available, use it to pull authoritative API docs for any external service referenced in findings.

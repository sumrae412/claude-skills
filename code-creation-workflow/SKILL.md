---
name: code-creation-workflow
description: ARCHIVED — Replaced by standalone skills. Use brainstorming → writing-plans → executing-plans for feature development. Use smart-exploration for codebase analysis, memory-injection for subagent context, context-engineering for session setup, source-driven-development for framework verification.
---

# ARCHIVED

This skill has been decomposed into focused, standalone skills:

| Old Phase | Replacement Skill | What It Does |
|-----------|------------------|--------------|
| Phase 0 (Context) | `context-engineering` | Session setup, rules files, context hierarchy |
| Phase 2 (Exploration) | `smart-exploration` | Task-typed codebase exploration with tuned prompts |
| Phase 3 (Clarification) | `brainstorming` (superpowers) | Interactive design dialogue |
| Phase 4 (Architecture) | `writing-plans` | Implementation planning |
| Phase 5 (Implementation) | `executing-plans` + `subagent-driven-development` | Plan execution with parallel agents |
| Phase 6 (Review) | `debate-team` + `coderabbit-review` | Multi-model code review |
| Memory injection | `memory-injection` | Project gotchas injected into subagent prompts |
| Source verification | `source-driven-development` | Framework code verified against official docs |

## Migration Guide

**Before (single monolithic skill):**
```
/code-creation-workflow → runs all 7 phases automatically
```

**After (composable pipeline):**
```
/brainstorming → clarify what to build
/writing-plans → break it into implementable steps
/executing-plans → execute with TDD and review
```

The standalone skills can also be used independently — `smart-exploration` for ad-hoc codebase analysis, `context-engineering` when session quality degrades, `source-driven-development` when building with frameworks.

## What's Preserved

- `references/` — subagent prompt templates, swarm schemas, memory injection mappings
- `scripts/` — Python modules for causal inference, constraint compilation, federation, etc.

These are still available for any workflow that needs them. They are not deprecated — only the monolithic orchestration is.

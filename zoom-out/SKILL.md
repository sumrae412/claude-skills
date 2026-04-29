---
name: zoom-out
description: Use when you don't know an area of code well and need broader context — produces a higher-level map of relevant modules and callers using the project's domain vocabulary, instead of diving into a single file. Trigger on "zoom out", "give me the bigger picture", "how does this fit", "I don't know this area", or before any change in unfamiliar code.
---

# Zoom Out

Go up a layer of abstraction. Produce a map of all the relevant modules and callers, using the project's domain glossary vocabulary (CONTEXT.md if it exists, otherwise CLAUDE.md terminology).

## What to produce

1. **The module under question** — one sentence on its responsibility, in domain terms.
2. **Who calls it** — list of upstream callers with one-line purpose each.
3. **What it calls** — list of downstream dependencies.
4. **Sibling modules** — peers in the same layer, and why they're separate.
5. **The bigger picture** — one paragraph: where this sits in the system, what would change if it were deleted or replaced.

## Vocabulary discipline

- Use canonical project terms exactly as defined in `CONTEXT.md` / `CLAUDE.md` / domain memory.
- If you find yourself reaching for a generic word ("service", "handler", "utility"), stop and look up the project's specific term.
- If no canonical term exists for a concept, surface that as a gap: *"This module has no name in the glossary — propose one?"*

## When NOT to use

- You already understand the area — zooming out adds noise.
- The task is purely local (rename, typo fix, single-line change) — vocabulary mapping is overkill.
- You need code-level detail, not a map — read the file directly instead.

## Pairs with

- `/courierflow-core`, project CLAUDE.md, or a future `CONTEXT.md` glossary — supplies the vocabulary.
- `smart-exploration` — for task-typed multi-subagent exploration. Use `zoom-out` for the lighter, single-shot orientation pass.

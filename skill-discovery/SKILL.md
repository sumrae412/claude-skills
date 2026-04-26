---
name: skill-discovery
description: Use when the user asks "is there a skill for X", "how do I do X", "find a skill that...", or when you're unsure which of the 150+ session-loaded skills fits a task. Covers local skills (session list, ~/.claude/skills, plugin cache) and external registries (vercel-labs skills, anthropic-skills, GitHub topic search). Use before asserting "no skill exists" or picking a skill from memory.
---

# Skill Discovery

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad exploration, repeated file reads, multi-file scans, or heavy reference loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant patterns inline instead of loading extra material.


## Overview

With 150+ skills loaded per session, the flat system-reminder list is easy to skim past — the model tends to answer from memory rather than scanning. This skill forces a systematic pass across local sources and known external registries before concluding "no skill exists" or picking one on vibes.

## When to Use

- User asks "is there a skill for X / how do I do X / find a skill..."
- You're about to invent a workflow and want to check if one's already packaged
- You're tempted to say "no skill for that" — verify before asserting
- User references an external skill repo (vercel-labs, anthropic-skills, etc.)

**Skip** when the right skill is obvious and recently-used in this session.

## Workflow

1. **Local session pass** — scan the system-reminder skill list for name + description matches on the user's intent keywords. Namespaced skills appear as `plugin:skill-name`. Read descriptions, don't just match names.
2. **Filesystem pass** — if no session match, list `~/.claude/skills/` and `~/.claude/plugins/cache/` for skills not surfaced in the session list (plugins can be enabled but not auto-loaded).
3. **Registry pass** — if still nothing local, consult [references/registries.md](references/registries.md) for external sources and the command to search each.
4. **Install guidance** — if an external skill fits, show provenance (install count / stars / last-commit recency) and propose the install command. **Do not install without user confirmation** — registry content is third-party.

Use [references/matching.md](references/matching.md) for intent-→-skill heuristics and common mis-matches (picking `research` when `fetch-api-docs` fits, etc.).

## Red Flags — Stop and Re-check

- About to say "there's no skill for that" without running steps 1-3
- Picking a skill because its name sounds right (without reading its description)
- Installing from a registry without checking provenance
- Skipping the local pass because you "remember" the skill list
- Recommending an external skill when a local one already covers the task

**All of these mean: restart at step 1.**

## Output Shape

Return one of:
- **Match** — skill name + one-line reason + how to invoke (`Skill` tool or slash command)
- **Candidate** — external skill + provenance + proposed install command (await user OK)
- **No match** — confirm all three passes ran, suggest closest adjacent skills, offer to build one via `superpowers:writing-skills`

---
name: bug-fix
description: Dedicated bug fix orchestrator — Reproduce → Diagnose → Fix (TDD) → Verify. Composes existing debugging skills (investigator, systematic-debugging, TDD) into a streamlined pipeline. Use when fixing bugs, regressions, or unexpected behavior instead of claude-flow.
user-invocable: true
---

# Bug Fix Workflow

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad
exploration, repeated file reads, multi-file scans, or heavy reference
loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant
  patterns inline instead of loading extra material.

## Overview

Focused bug workflow: reproduce, diagnose root cause, fix minimally, then
verify. This file is a router; keep the step logic in phase files.

## When to Use

- bug fixes
- regressions
- unexpected behavior
- environment-specific failures that can be reproduced or instrumented

Do not use for new features or general improvements; use `claude-flow`
for those.

## Load Strategy

1. Load only the bug-relevant context.
2. Choose the current step and load only that phase file.
3. Use defensive/domain skills only if the affected surface requires them.
4. Escalate to `investigator` only for genuinely complex diagnosis.

## Base Context

- project rules file
- `coding-best-practices`
- matching defensive skill if UI or backend flow risk exists
- relevant domain skill only if the bug sits in that domain
- relevant memory entries for known gotchas

## Phase Map

1. `phases/phase-1-reproduce.md`
2. `phases/phase-2-diagnose.md`
3. `phases/phase-3-fix.md`
4. `phases/phase-4-verify.md`

## Session Rules

- No reproduction, no bug claim.
- No fix without root cause.
- Keep the fix minimal and blast-radius aware.
- Verification must include the original failing path.

## Deliverables

Produce only what the workflow stage needs:

- bug report
- diagnosis
- fix diff
- verification summary

## Guardrails

- Do not multi-hypothesize without runtime evidence on hard-to-reproduce
  bugs.
- Do not "improve adjacent code" while fixing.
- Do not call the fix done if the reproducing test was never red then
  green.

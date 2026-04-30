---
name: website-tester
description: Exploratory end-to-end functional testing for web apps — discovers forms, fields, and buttons on each page, fills them with realistic data, exercises CRUD flows, and reports broken submits, 500s, validation gaps, and missing feedback. Lower-ceremony than `playwright-test` (no user-story input required). Use when user says "test my website", "test all the forms", "functional test my app", "click through everything", or "smoke-test this site". NOT for story-driven verification (use playwright-test + user-stories), unit tests (project test runner), or visual/design audits (design-audit).
---

# Website Functional Tester

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

Functional website testing that crawls pages, fills forms, exercises CRUD
behavior, and reports real workflow failures.

This file is a router. Keep execution details in phases and the test
script.

## When to Use

- user asks to test a website or forms
- user wants CRUD or flow verification
- smoke testing is not enough

## Load Strategy

1. Decide the testing scope.
2. Load only the matching phase file from `phases/`.
3. Use the script for deterministic execution rather than narrating the
   procedure manually.

## Script Map

- `scripts/test_website.py`

## Phase Map

1. `phases/phase-1-scope-and-safety.md`
2. `phases/phase-2-execution.md`
3. `phases/phase-3-reporting.md`
4. `phases/phase-4-extension-points.md`

## Session Rules

- default to non-destructive testing
- prefer staging for destructive workflows
- distinguish element existence from workflow success

## Deliverables

Produce only what the run needs:

- test plan
- execution result
- failure report
- extension guidance

## Guardrails

- Do not enable destructive tests casually.
- Call out authentication and file-upload limits explicitly.
- Treat false-positive success indicators as a real risk in interpretation.

## Out of Scope

This skill does NOT:
- Run user-story-driven E2E tests with explicit acceptance criteria—use `playwright-test` paired with `user-stories`.
- Replace unit/integration tests—use the project's test runner.
- Audit visual design, typography, or layout—use `design-audit` or `typography`.
- Review code for OWASP/injection vulnerabilities—use `review-pr` or `security-review`.
- Execute destructive workflows in production—keep destructive runs to staging or non-destructive default mode.

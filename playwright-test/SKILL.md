---
name: playwright-test
description: User-story-driven E2E testing via the Playwright MCP — navigates the app, fills forms, clicks through flows, captures screenshots at each step, and reports pass/fail against each story's acceptance criteria. Use when user says "run the user stories", "playwright test this", "/playwright-test", "E2E test the app", or "verify these stories work". Pairs with `user-stories` (which generates the stories) — feed its output here. NOT for unit tests (use the project's test runner), code-only review (use review-pr), or design audits (use design-audit).
---

# Playwright Test Skill - Interactive E2E Testing from User Stories

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad exploration, repeated file reads, multi-file scans, or heavy reference loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant patterns inline instead of loading extra material.


Execute comprehensive end-to-end tests using Playwright MCP tools, driven by user stories. This skill provides interactive browser testing with visual verification, screenshots, and detailed reporting.

## Overview

This skill uses the Playwright MCP tools (`browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`, etc.) to execute real browser tests against the application, validating user stories interactively.

**Target URL:** `your production URL (APP_URL)` (production) or `http://localhost:8000` (local)

## How This Works

1. **Load User Stories** - Read from `tests/e2e/USER_STORIES.md` or use `/user-stories` skill output
2. **Select Test Scope** - Choose feature area or specific user story to test
3. **Execute Tests** - Use Playwright MCP tools to interact with the live site
4. **Capture Evidence** - Take snapshots/screenshots at each step
5. **Report Results** - Provide pass/fail status with detailed findings

## Before Starting

Ask the user:
1. **Target environment**: Production (Heroku) or Local (localhost:8000)?
2. **Test scope**: Full suite, specific feature area, or single user story?
3. **Test credentials**: What email/password to use for authenticated tests?


## Workflow

This skill uses progressive disclosure. Load the phase file when you enter that stage; skip the others to keep context lean.

1. **Phase 1 + 2: Environment setup and authentication → load [`phases/setup-and-auth.md`](phases/setup-and-auth.md).**
   Navigate to target, take initial snapshot, verify site accessibility, handle login flow if required.

2. **Phase 3 + 4: Test execution and individual procedures → load [`phases/execution.md`](phases/execution.md).**
   Test suites by feature area (Auth, Clients, Workflow, Navigation), execution pattern per story, and all US-ID-specific procedures (US-AUTH-001/002, US-CLIENT-001/002, US-WF-001, US-NAV-001/002).

3. **Phase 5: Reporting → load [`phases/reporting.md`](phases/reporting.md).**
   Per-test result format (Pass/Fail/Needs Attention), summary report template (results by feature area, failed tests, recommendations).

4. **MCP tools + troubleshooting → load [`references/tools-and-troubleshooting.md`](references/tools-and-troubleshooting.md).**
   Playwright MCP tool reference (Navigation, Inspection, Interaction, Waiting, Utilities), Best Practices, Quick Start Commands, and Common Issues / Debug Mode. Keep handy during any execution phase.

---

## Session Flow

When user invokes `/playwright-test`:

1. **Greet and configure**:
   > Ready to run E2E tests using Playwright.
   >
   > **Configuration needed:**
   > - Target: Production (Railway) or Local?
   > - Scope: Full suite, feature area, or specific story?
   > - Credentials: Test user email and password?

2. **After configuration**, begin testing systematically
3. **Report results** as tests complete
4. **Provide summary** at end of session

## Out of Scope

This skill does NOT:
- Generate user stories or acceptance criteria—use `user-stories` to produce them, then feed here.
- Run unit tests or component tests—use the project's test runner.
- Audit visual design, spacing, or typography—use `design-audit` or `typography`.
- Review code quality or PR diffs—use `review-pr`.
- Crawl an unknown app to discover forms without user-story input—use `website-tester` for exploratory functional tests.

## Integration with User Stories

This skill works best with `/user-stories` skill:

1. Run `/user-stories` to generate or review user stories
2. Run `/playwright-test` to execute those stories as tests
3. Use findings to update stories or fix bugs

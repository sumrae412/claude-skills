---
name: user-stories
description: Generate Playwright-testable user stories by crawling a web app's routes, templates, and models. Pairs with `playwright-test` for execution.
---

# User Story Generator - Test-Ready Stories from Codebase Analysis

Generate detailed, Playwright-testable user stories by exploring the codebase and asking targeted questions. This skill crawls the project to understand existing features, then collaboratively builds comprehensive user stories with acceptance criteria.

## How This Works

1. **Read all documentation first** - README, CLAUDE.md, docs/*.md, design specs, architecture docs
2. **Explore the codebase** - Analyze routes, templates, models, and services
3. **Synthesize context** - Combine doc insights with code discoveries
4. **Ask targeted questions** - One at a time, referencing what you learned
5. **Generate user stories** - With detailed acceptance criteria
6. **Output Playwright-ready specs** - Stories structured for easy test conversion

**IMPORTANT:** Always read existing documentation before scanning code. Docs provide crucial context about why things are built a certain way, what the vision is, and what constraints exist.

## Phase Workflow

This skill uses progressive disclosure. Load the phase file you're entering; previous phases can be dropped from context once their outputs are captured.

1. **Phase 1 — Codebase & Documentation Exploration** → load [`phases/phase-1-exploration.md`](phases/phase-1-exploration.md). Read existing docs (README, CLAUDE.md, docs/*.md, design specs); scan routes/templates/models/services; assemble the synthesis that grounds every later question.
2. **Phase 2 — Feature Discovery Questions** → load [`phases/phase-2-discovery.md`](phases/phase-2-discovery.md). Opening framing + one-at-a-time discovery questions referencing the Phase 1 findings. For domain-specific question stems, also load [`references/question-patterns.md`](references/question-patterns.md) (For New Features / For Existing Features / For Complex Workflows).
3. **Phase 3 — User Story Format** → load [`phases/phase-3-story-format.md`](phases/phase-3-story-format.md). Apply Writing Rules (below) to the discovery output, format each story with Preconditions / Steps / Acceptance Criteria (Gherkin) / Edge Cases / Error Scenarios / Test Data / Playwright Test Hints.
4. **Phase 4 — Playwright Test Template** → load [`phases/phase-4-playwright-template.md`](phases/phase-4-playwright-template.md). Convert formatted stories into Playwright spec scaffolding ready to fill in.

## Writing Rules

Before generating stories, apply these rules uniformly:

- **Cover all major user-facing flows** — no skipping auth, error paths, or edge states.
- **Consistent structure** — every story uses the template below; no deviation.
- **Strict Gherkin for acceptance criteria** — `Given` / `When` / `Then` / `And` only. No prose paragraphs, no mixed narrative + bullets.
- **Every step references observable UI behavior** — something a test runner can assert (visible text, element state, URL change, DOM attribute).
- **Ban vague language** — no "works correctly", "loads successfully", "behaves as expected", "is displayed properly". If a criterion can't name what's observable, rewrite it until it can.
- **Prefer testable anchors** — reference accessible labels (`aria-label`, role), visible text, or stable selectors that a Playwright test could target. Avoid brittle anchors (nth-child, auto-generated class names).
- **No implementation details** — stories describe user-visible behavior, not code, endpoints, or internal state transitions.

## Session Rules

1. **Read docs first** - Always read README, CLAUDE.md, and docs/ before anything else
2. **Then explore code** - Scan routes, models, templates, services
3. **Synthesize both** - Combine documentation insights with code discoveries
4. **One question at a time** - Wait for answer before proceeding
5. **Be specific** - Reference actual pages, buttons, fields from codebase AND docs
6. **Validate understanding** - Summarize after every 4-5 questions
7. **Think like a tester** - Ask about edge cases, errors, boundaries
8. **Cite sources** - Reference specific files, docs, routes when discussing features

## Ending the Session

When stories are complete, offer:

> We've defined [X] user stories with [Y] acceptance criteria. Would you like me to:
> 1. Save all stories to a markdown file
> 2. Generate Playwright test templates
> 3. Create a test plan document
> 4. All of the above

## Output Files

### User Stories Document
Save to: `docs/user-stories/[feature-name].md`

### Playwright Tests
Save to: `tests/e2e/[feature-name].spec.ts`

### Test Plan
Save to: `docs/test-plans/[feature-name]-test-plan.md`

## Example Session

For a worked example showing Phase 1 doc-reading + codebase scanning followed by Phase 2 one-at-a-time discovery questioning (truncated before story formatting), see [`references/example-session.md`](references/example-session.md).

## Tips for Best Results

- Be specific about user roles and permissions
- Describe what success looks like visually
- Think about what could go wrong
- Consider mobile vs desktop if relevant
- Mention any time-sensitive aspects
- Share examples of similar features you like

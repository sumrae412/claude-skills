# PRD Template

Fill the sections below. Section headings match `$requirements` field names so claude-flow Phase 3 can ingest by heading. Don't rename them.

Remove any section that genuinely doesn't apply (e.g. Non-Functional for a one-screen prototype). Keep section order — downstream tooling reads top-to-bottom.

---

```markdown
# PRD: <Feature Name>

> Status: draft | approved
> Author: <name>
> Date: <YYYY-MM-DD>
> Mode: greenfield | feature

## Problem Statement

<One paragraph: who has the problem, how often, what's the cost of not solving it. Ground in evidence — user research, support data, metrics. Avoid solutioning here; describe the pain.>

## Goals & Success Metrics

<3-5 measurable outcomes. Each one answers "how will we know this succeeded?" Outcomes, not outputs.

Bad: "Build onboarding wizard"
Good: "Reduce time to first value from 90s to 30s for new users, measured 7 days post-signup."

Distinguish user goals from business goals where they differ.>

- <Goal 1 — metric, target, measurement window>
- <Goal 2 — metric, target, measurement window>
- ...

## User Stories

<Numbered with `US-N`. Each story uses "As a [role], I want [capability] so that [benefit]". Personas should be specific ("returning customer" not "user"). Capability describes what they want to accomplish, not how.>

### US-1: <Short title>

**As a** <role>
**I want** <capability>
**So that** <benefit>

### US-2: <Short title>

**As a** <role>
**I want** <capability>
**So that** <benefit>

...

## Acceptance Criteria

<EARS format — `WHEN <event>, [IF <condition>,] THEN <expected outcome>`. Each one gets an `AC-N` ID. claude-flow Phase 4c uses these as the coverage checklist.

Cover happy path, edge cases, and error states. Each AC must be independently testable. Avoid "fast", "user-friendly", "intuitive" — define those in concrete terms.>

- **AC-1:** WHEN <event>, THEN <outcome>
- **AC-2:** WHEN <event>, IF <condition>, THEN <outcome>
- **AC-3:** WHEN <event>, THEN <outcome>
- ...

## Scope

### In

<Numbered list of capabilities included in v1. Cap at 5 must-haves. Each one ties back to a US-N.>

- <Capability 1>
- <Capability 2>
- ...

### Out

<Explicitly excluded. claude-flow Phase 4c uses this as scope-creep detection. Minimum 2 items. For each, briefly note why it's out (not enough impact / too complex / separate initiative / premature).>

- <Excluded item 1> — <why>
- <Excluded item 2> — <why>
- ...

## Edge Cases

<Boundary conditions and error states with explicit resolutions. "What happens when input is empty? What happens on network failure? What if two users race?">

- **Case:** <description>
  **Resolution:** <what the system does>
- **Case:** <description>
  **Resolution:** <what the system does>
- ...

## Risk Class

**Level:** low | medium | high

**Flags:** <any of: auth, privacy, money, data_loss, external_side_effects, public_api — or "none">

**Rationale:** <one short paragraph>

<If level is high or any flag fires, claude-flow forces the full workflow path even when the diff is small. Don't downplay this — review honestly.>

## Non-Functional Requirements

<Optional. Performance, security, backward compatibility, accessibility. Each one specific and measurable.>

- **Performance:** <e.g. "p95 response time < 200ms for typical query">
- **Backward compat:** <e.g. "existing /api/v1/foo callers must continue to work unchanged">
- **Security:** <e.g. "endpoint requires authenticated session; rate-limited per user">
- **Accessibility:** <e.g. "WCAG 2.1 AA for new UI surfaces">

## Definition of Done

This section answers two questions: *what gates apply to every story before this PRD ships?* and *what concrete steps verify each story actually works?* Acceptance Criteria say what passing means; this section says how you confirm it passed.

### Global Gates (apply to every story)

These must all be true before the PRD is "done":

- [ ] Every AC-N has at least one automated test (unit, integration, or e2e) — not just a manual check
- [ ] `<typecheck command>` passes (e.g. `pnpm typecheck`, `mypy app/`, `tsc --noEmit`)
- [ ] `<lint command>` passes (e.g. `ruff check app/`, `eslint .`)
- [ ] Full test suite passes with **zero new failures**
- [ ] Coverage on touched modules ≥ <project target, or "no regression vs main">
- [ ] Migrations (if any) run cleanly on a fresh DB and on a copy of staging; rollback path documented
- [ ] No new `ERROR` / `WARN` log lines introduced under normal use
- [ ] Docs updated where user-facing behavior changed (README / CHANGELOG / docs/)
- [ ] If gated behind a feature flag, default state (off / on) is set deliberately and noted
- [ ] Rollback plan exists: revert PR + any data fixup steps

### Per-Story Verification

For each story, list the concrete checks that prove it works as designed. These are **actions a reviewer or the AI agent runs**, not restated ACs. Examples: a curl command, a page to visit, a log query, a metric to read.

#### US-1: <title>

- [ ] <e.g. "POST /api/v1/foo with valid body — expect 201 + row in `foo` table">
- [ ] <e.g. "POST same body twice — expect second to return 409 with `existing_id`">
- [ ] <e.g. "Tail prod logs after first request — no new ERROR lines from `routes.foo`">

#### US-2: <title>

- [ ] <step>
- [ ] <step>

<Add one block per US-N. Aim for at least 2 concrete checks per story — happy path + at least one error/edge.>

## Open Questions

<Anything the PRD couldn't resolve. Tag each with who should answer. Distinguish blocking (must answer before starting) from non-blocking (can resolve during build).>

- **[BLOCKING — eng]** <question>
- **[BLOCKING — stakeholder]** <question>
- **[non-blocking — design]** <question>

---

> Once approved, run `/claude-flow` from this repo. Phase 3 will read this PRD and skip ambiguities you've already resolved.
```

## Notes for fillers

**EARS format reminders:**
- `WHEN <event>` for triggers — `WHEN a user submits the form`
- `IF <condition>` for conditional branches — `IF the email is already registered`
- `THEN <outcome>` for the expected behavior — `THEN the system returns a 409 with a clear error`
- Compound: `WHEN a user submits the form, IF the email is already registered, THEN the system returns 409 with the message "email already in use"`

**Pass-fail checklist for each AC** (the same checks claude-flow Phase 3 Step 2 will run; catch them here to avoid round-trips):

- [ ] **EARS shape** — parses as `WHEN ... [IF ...] THEN ...`, not a bare assertion
- [ ] **No vague predicates** — no "fast", "easy", "intuitive", "user-friendly", "smooth", "robust", "scalable", "obvious", "good", "nice" without a concrete number
- [ ] **Quantified where measurable** — "many" → a number; "fast" → p95 latency; "small" → byte / row / item count
- [ ] **Atomic observable** — one assertion per AC; if THEN contains `AND`, split into separate AC-N items
- [ ] **No implementation prescription** — the AC names what's observable, not what tech is used (Redis / REST / JWT belong in Non-Functional or design notes)
- [ ] **Story trace** — every AC-N maps to at least one US-N
- [ ] **Stable subject** — the AC names what acts (system / user / scheduled job), not a pronoun ("it", "this", "the thing")

**Story sizing:** if a US can't be implemented in one focused session, split it. "Add authentication" is too big — split into `US-1: schema & migration`, `US-2: login endpoint`, `US-3: session middleware`, `US-4: login UI`.

**Story ordering:** put dependencies before dependents. Schema before backend before UI. claude-flow Phase 4 will re-validate, but a clean order saves a round trip.

# AI-Agent Variant

Use this variant **only** when the PRD is going directly to a separate AI coding agent (Codex, a fresh Claude Code session, an autonomous build loop) rather than into claude-flow. The default PRD is written for humans-first; the AI-agent variant is written for machine actionability — every section is something the agent can execute against without asking a clarifying question.

If you're going through claude-flow, skip this file. The default template is the right shape.

> **⚠ Overlap with claude-flow Phase 4:** The sections this variant adds (File Plan, API Contracts, Data Model, Build Sequence, Test Cases, Migration & Rollback) cover ~70% of what claude-flow's `$plan` contract produces in Phase 4. If you're going to run claude-flow on this feature anyway, **don't fill out this variant** — Phase 4 will produce a plan tailored to the exploration it just did, and pre-specifying the file plan can conflict with what Phase 2 discovers about existing patterns.
>
> Use this variant only when one of the following holds:
> - The downstream consumer is a non-claude-flow agent (Codex, separate Claude Code session running a different workflow, autonomous build loop)
> - The team isn't using claude-flow at all
> - You explicitly want the PRD to dictate file structure / contracts ahead of any exploration
>
> Otherwise: stop after the default template and run `/claude-flow`.

## What changes

The AI-agent variant **adds** these sections after the default PRD body. It does not replace anything.

```markdown
## Codebase Context

**Repo:** <path or URL>
**Language / runtime:** <e.g. Python 3.12 / Node 22>
**Framework:** <e.g. FastAPI / Next.js 15 / Express>
**ORM / DB:** <e.g. SQLAlchemy 2.0 + Postgres 16 / Prisma + SQLite>
**Test framework:** <e.g. pytest / vitest>
**Lint / format:** <e.g. ruff + ruff format / eslint + prettier>
**Auth pattern:** <e.g. JWT in HttpOnly cookie / NextAuth / custom session middleware>

**Patterns to match (with file references):**

- Routing: see `<file>:<line>` for the canonical pattern
- Service layer: see `<file>:<line>`
- Validation: see `<file>:<line>`
- Tests: see `<file>:<line>` for the test style this code should match

**Patterns to avoid:** <list anti-patterns the agent should NOT introduce>

## File Plan

For each file, name the path and what the agent should do.

**Create:**
- `<path>` — <one sentence on responsibility>
- `<path>` — <one sentence>

**Modify:**
- `<path>` — <what changes, what must NOT change>
- `<path>` — <what changes>

**Do not touch:**
- `<path>` — <why off-limits — e.g. "auth middleware, separate PR">

## API Contracts

For each endpoint, name the exact request and response shape as code, not prose.

### POST /api/v1/<resource>

**Request:**

```json
{
  "field_a": "string",
  "field_b": 123,
  "field_c": ["string"]
}
```

**Response 200:**

```json
{
  "id": "uuid",
  "created_at": "ISO 8601 string",
  "field_a": "string"
}
```

**Errors:**

- `400` — invalid `field_b` (must be positive int) — body: `{"error": "field_b must be positive"}`
- `409` — resource exists — body: `{"error": "already exists", "existing_id": "uuid"}`
- `401` — no auth — body: `{"error": "unauthenticated"}`

## Data Model Changes

```sql
-- Migration: add <column> to <table>
ALTER TABLE <table> ADD COLUMN <column> <type> <constraint>;
CREATE INDEX <name> ON <table>(<column>);
```

**Backfill plan:** <if any — e.g. "set existing rows to default 'medium' in same migration">

**Rollback:** <how to undo if needed>

## Build Sequence

Strict order — earlier steps must NOT depend on later ones. The agent works top-to-bottom without backtracking.

1. <Step — e.g. "Add migration `<file>` for the new column. Run migration, verify schema.">
2. <Step — e.g. "Add field to ORM model `<file>:<line>`. Run typecheck.">
3. <Step — e.g. "Add validation schema `<file>:<line>`. Add unit test for validation.">
4. <Step>
5. <Step — e.g. "Wire endpoint to router. Add integration test for happy path + 409 case.">
6. <Step — e.g. "Update OpenAPI spec / API docs.">

## Test Cases

For each behavior, the input + expected output + assertion. Not just "test the endpoint". This is the executable form of the default template's `## Definition of Done > Per-Story Verification` — same checks, but each one written as code/command the agent can run directly. The default DoD's Global Gates still apply.

**TC-1:** <happy path>
- Input: `<exact request body>`
- Expected response: `<exact body and status>`
- Assertion: <e.g. "response.status == 200; row exists in DB with field_a == input.field_a">

**TC-2:** <error case>
- Input: <bad input>
- Expected response: <exact error body and status>
- Assertion: <what to check>

**TC-3:** <edge case from PRD Edge Cases section>
- Input: <...>
- Expected: <...>

## Migration & Rollback

**Deploy steps:**

1. <e.g. "Run migration on staging, verify with `<query>`.">
2. <e.g. "Deploy app code with feature behind flag `<flag-name>` defaulting to off.">
3. <e.g. "Enable flag for internal users, smoke test.">
4. <e.g. "Roll out to 10% / 50% / 100%.">

**Rollback steps:**

1. <e.g. "Disable flag — code path no longer exercised.">
2. <e.g. "If schema change is causing problems, revert migration `<file>` (only safe if no rows used new column).">

## Guardrails

- <e.g. "Match existing service-layer pattern at `services/foo_service.py:42` — do NOT introduce a new abstraction.">
- <e.g. "Do not call `db.commit()` from a service — endpoint owns the transaction.">
- <e.g. "All datetime values use `datetime.now(timezone.utc)` — `utcnow()` is deprecated in this codebase.">
- <e.g. "All new endpoints require auth via existing `require_user` dependency — see `routes/users.py:15` for usage.">

## Blockers

Anything the agent cannot proceed without. Use `[BLOCKED — need X]` not silent `[TBD]`.

- **[BLOCKED — design decision]** <question>
- **[BLOCKED — credential / secret]** <what's missing>

> **Agent contract:** if the agent encounters any `[BLOCKED — ...]` item while executing this PRD, it MUST stop and report the blocker to the user. It must NOT guess, substitute `[TBD]`, or proceed with a placeholder value. A blocker is a hard halt, not a hint.
```

## Self-check before hand-off

Before giving the AI-agent-variant PRD to a separate agent, verify:

- [ ] Every endpoint has request and response shapes as JSON code blocks (not prose)
- [ ] Every file in the File Plan has a one-sentence responsibility
- [ ] Build Sequence has no circular dependencies (each step only depends on earlier ones)
- [ ] Every behavior in Acceptance Criteria has a corresponding TC-N test case
- [ ] No `[TBD]` markers — convert any genuine unknowns to `[BLOCKED — need X]`
- [ ] Codebase Context names at least 3 file references for "patterns to match"
- [ ] Could the agent build this without access to this conversation? If no, fix the gap.

## What this variant is NOT for

- Internal tickets / sprint planning (too verbose)
- Stakeholder approval docs (humans don't want to read JSON shapes)
- claude-flow input (Phase 4 produces the file plan and API contracts; pre-specifying them duplicates work and may conflict with what Phase 2 exploration discovers)

If any of those are the audience, use the default template (`references/template.md`) instead.

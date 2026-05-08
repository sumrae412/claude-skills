# Phase 3: Clarification + Requirements (Hard Gate)

<!-- Loaded: after Phase 2 | Dropped: after user approves requirements -->
<!-- Output: $requirements contract -->

<HARD-GATE>
All ambiguities must be resolved and requirements formalized before architecture work begins.
</HARD-GATE>

---

## Step 0: Ingest PRD (if present)

Before resolving ambiguities yourself, check whether a PRD already answers them.

```bash
ls docs/prds/prd-*.md 2>/dev/null
```

**Disambiguation chain** when multiple PRDs match:

1. **Slug match** — if any `prd-<slug>.md` matches the current task slug, use it. Otherwise:
2. **List + ask** — if multiple PRDs exist and none match the slug, present the list to the user and ask which one (if any) applies to the current task.
3. **Skip** — if the user says "none" or there are no PRDs, skip this step and proceed to Step 1 normally.

Never silently pick "most recent" — the wrong PRD ingested as `$requirements` is worse than no PRD.

**Section → field mapping:**

| PRD section | `$requirements` field |
|-------------|------------------------|
| `## User Stories` (US-N) | `stories[]` |
| `## Acceptance Criteria` (AC-N, EARS) | `acceptance_criteria[]` |
| `## Scope` → `### In` / `### Out` | `scope.in` / `scope.out` |
| `## Edge Cases` | `edge_cases[]` |
| `## Risk Class` | `risk_class` |
| `## Non-Functional Requirements` | `nonfunctional[]` |
| `## Problem Statement` | (read for context, not stored in `$requirements`) |
| `## Goals & Success Metrics` | (read for context, not stored in `$requirements`) |
| `## Definition of Done` | (read for context; consumed by Phase 5 implementation gates and Phase 6 verification reviewers, not by Phase 3) |
| `## Open Questions` | (parked decisions; `[BLOCKING — ...]` items must resolve in Step 1) |

Pre-populate `$requirements` from the PRD. Treat PRD-resolved ambiguities as already answered — do NOT re-ask the user about anything the PRD specifies.

**EARS-shape check on ingested ACs:** as you ingest each `## Acceptance Criteria` item, sanity-check that it parses as `WHEN <event>, [IF <condition>,] THEN <outcome>`. Any AC that fails the shape check (bare assertion, paragraph form, no clear THEN clause) → mark the ingested AC as `quality_flag: malformed` in `$requirements`. The Step 2 SKIP-CONDITION won't trigger when a malformed flag is present, so the full Testability axis runs even if Phase 2 passed it. This closes the silent-degradation path where a PM's loose ACs would otherwise sail through Phase 2's skip.

**Contradiction reconciliation with Phase 2 exploration:** Compare the ingested PRD against `$exploration` findings before proceeding to Step 1. If they disagree (e.g. PRD declares "no auth integration" but exploration found an existing auth dependency on the affected file), do not silently trust the PRD. Surface the contradiction to the user with both sources cited and ask which to trust. Common contradiction sites: scope.out items the codebase actually couples into, risk_class flags the PRD missed, edge_cases the codebase already handles differently.

If `## Open Questions` lists items tagged `[BLOCKING — ...]`, those must be resolved in Step 1 before proceeding.

If the PRD is missing or its scope doesn't match the current task, skip this step and proceed to Step 1 normally.

The `prd` skill (`~/.claude/skills/prd/`) authors PRDs in this exact format. If the user mentions wanting one and Phase 3 is about to ask many questions, suggest pausing claude-flow and running `/prd` first — the resulting document survives across sessions and turns Phase 3 from interrogation into ingestion.

---

## Step 1: Resolve Ambiguities

Review exploration findings against the original request. Identify **every** underspecified aspect (skip anything already answered by Step 0's PRD ingestion):

- **Edge cases** — What happens when input is empty, duplicated, or malformed?
- **Error handling** — What should the user see when things fail?
- **Integration points** — Which existing systems does this touch?
- **Scope boundaries** — What is explicitly NOT included?
- **Performance** — Will this hit large datasets or high concurrency?
- **Backward compatibility** — Does this change existing behavior?

Present an organized question list to the user. Group questions by category. Wait for answers before proceeding.

**If no ambiguities exist** (rare — usually means the request is very well-specified), state that explicitly and proceed to Step 2.

---

## Step 1.5: Self-Answer Audit (Teach AI to Answer Its Own Questions)

**Before** presenting the question list to the user, run the audit:

Resolve helper scripts from the loaded `claude-flow` skill directory, not from
the target project's cwd.

```
echo '["<question 1>", "<question 2>", ...]' | \
    python3 <claude-flow-root>/scripts/audit_phase3_questions.py --json
```

For each question flagged `self_answerable: true`:
- Execute the `suggested_lookup` yourself (grep, ls, `alembic heads`, `inject_lookups.py`, etc.)
- Record the result as a resolved ambiguity in `$requirements`
- **Remove the question from the user-facing list**

**Principle** (Brian Lovin, Notion): *"Anytime the AI asks you to do something,
before responding, try your best to see if you could teach the AI to answer
that question for itself."*

Only present genuinely ambiguous (user-intent, preference, policy) questions
to the user. This reduces Phase 3 friction and accelerates the hard gate.

**Signal:** if the audit flags >50% of questions as self-answerable, that's a
signal Phase 2 exploration was shallow — consider another firsthand
exploration pass (or a full-path research pass) rather than pestering the
user.

The audit is conservative: questions containing intent markers ("should", "do
you want", "how should we handle") are NEVER flagged self-answerable, even if
they mention files or schemas.

---

## Step 2: Quality Gate

<SKIP-CONDITION>
If `$exploration.quality_gate` exists AND its 4 axes all scored PASS AND Step 0 did not flag any ingested acceptance_criteria as malformed, skip this step — proceed directly to Step 3. If `$exploration.quality_gate` is missing or incomplete (Phase 2 was skipped on a fast / lite / clone path), do NOT skip — run the full Quality Gate.
</SKIP-CONDITION>

**Only runs when Phase 2 advisor flagged failures, was skipped, or Step 0 flagged a PRD-sourced AC.** Re-score the 4 axes after ambiguity resolution:

1. **Objective Clarity** — Deliverable stateable as one-sentence outcome? FAIL: vague, unmeasurable, or activity-not-outcome.
2. **Service Scope** — Affected files/modules identifiable from exploration? FAIL: no specific locations.
3. **Testability** — every acceptance criterion is pass-fail observable from outside the system. Apply ALL of these checks:
   - **EARS shape:** `WHEN <event>, [IF <condition>,] THEN <outcome>`. FAIL on bare assertions ("user can search") or paragraph-style criteria.
   - **No vague predicates:** flag "fast", "easy", "intuitive", "user-friendly", "smooth", "robust", "scalable", "obvious", "good", "nice" without quantification. FAIL → require concrete observable.
   - **Quantification on measurable predicates:** if the AC implies measurement ("many users", "small file", "soon", "quickly"), it must name a number and unit. FAIL → "many" → "10k concurrent"; "fast" → "p95 < 200ms".
   - **Atomic observable:** one assertion per AC. `THEN A AND B AND C` → split into AC-N, AC-(N+1), AC-(N+2). FAIL on conjunctions in the THEN clause.
   - **No implementation prescription:** the AC names *what is observable*, not *what the system uses*. "Stored in Redis" / "served via REST" / "JWT in cookie" → moves to `nonfunctional` or design notes, not `acceptance_criteria`. FAIL when an AC mentions a specific technology choice.
   - **Story trace:** every AC-N must be linkable to at least one US-N from `$requirements.stories`. FAIL on orphan ACs (criterion with no parent story). **Waiver:** `$requirements.stories` may be empty for pure-technical work (refactor / migration / infrastructure / tech debt) or when stories live in an external ticketing system; in that case the orphan-AC check is suppressed and the PRD's Problem Statement carries the rationale instead.
   - **Stable subject:** the AC names what acts (system / user / external service / scheduled job), not "it" / "this" / "the thing". FAIL on pronoun-only subjects.
4. **Completeness** — All edge cases have resolutions (including those self-answered by the Step 1.5 audit)? FAIL: unresolved edges, unspecified error handling.

**Gate:** All pass → Step 3. Any fail → present failures with questions (or send back to PRD author with the specific failing ACs), loop until all pass.

---

## Step 3: Synthesize Structured Requirements

After all ambiguities are resolved and the quality gate passes, populate the `$requirements` contract (see `contracts/requirements.schema.md`).

Include a `risk_class` entry with:

- `level`: `low` / `medium` / `high`
- `flags`: any of `auth`, `privacy`, `money`, `data_loss`,
  `external_side_effects`, `public_api`
- `rationale`: one short paragraph explaining the classification

If `risk_class.level == high`, the change may not proceed on a fast or lite
implementation path unless the user explicitly narrows scope to planning-only
or documentation-only work.

This contract flows downstream to Phase 4 (architecture references it), Phase 4c (validates plan coverage against it), and Phase 6 (reviewers check adherence).

**Present to user for approval.** The structured requirements are the contract for everything downstream. If the user provides feedback, revise and re-present.

After approval, record a stable hash of the approved `$requirements` artifact in
the run manifest from `references/run-manifest.md`. This is the replayable
contract for later review and reruns.

Preferred command:

```bash
python3 <claude-flow-root>/scripts/run_manifest.py record-approval \
  --manifest .claude/runs/<session-id>.json \
  --kind requirements \
  --content-file /tmp/requirements.json \
  --state-file .claude/workflow-state.json
```

```
◆ USER APPROVES structured requirements before architecture ◆
```

---

## Optional: Export Context Packet (PRP)

After requirements are approved, optionally save a **Product Requirement Prompt (PRP)** — a reusable context packet that survives across sessions.

**Trigger conditions** (export if ANY apply):
- Feature is complex enough to span multiple sessions
- User says "save context", "export this", or "I'll continue later"
- Task involves 3+ integration points or schema changes

**PRP format** — write to `plans/PRP-<feature-slug>.md`:

```
# PRP: <Feature Name>
**Created:** <date> | **Status:** ready-for-implementation

## Requirements
(Reference or inline the structured $requirements from Step 3)

## Codebase Intelligence
- **Key files:** <5-10 files from exploration with their roles>
- **Patterns to follow:** <discovered conventions from Phase 2>
- **Integration points:** <systems this touches>

## Constraints & Edge Cases
(Reference the Edge Cases section from $requirements)

## Ruled Out
- <approach/tool/path> — <why it failed or was abandoned>
- <investigation that hit a dead end> — <what was discovered>
<!-- Prevents future sessions from re-exploring dead ends -->

## Implementation Notes
- <API docs fetched (if applicable)>
- <defensive patterns required>
- <test strategy hints>
```

**How it's consumed:** Phase 1 Discovery detects PRP files via the PLAN PATH branch. A PRP provides richer context than a bare plan — it includes the codebase intelligence that would otherwise require re-running Phase 2 exploration.

If not triggered, skip — most single-session features don't need this.

---

**State transition:** Transition to phase-4.

---

**Output:** Populate `$requirements` contract (see `contracts/requirements.schema.md`). User must approve before Phase 4.

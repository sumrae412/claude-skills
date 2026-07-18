# Plan Format & Execution Gates

> Inlined 2026-07-17 from the retired `writing-plans` and `executing-plans` skills so claude-flow is self-contained; content preserved verbatim with light connective edits.

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For Claude:** Execute this plan task-by-task per the execution gates in this file.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

**Ruled Out:** [Approaches considered and rejected during design — prevents re-exploration]
- <approach> — <why rejected>

## References

[REQUIRED. List the exact file paths and external docs an implementer needs to consult. This section gates Phase 5 context loading — implementers and exploration subagents are instructed to read ONLY what's listed here, not adjacent docs they happen to find. Be deliberate: if a file is critical, list it; if it isn't, leaving it off keeps subagent context tight.]

- `path/to/relevant/source.py` — <why it matters: existing pattern, contract to preserve, similar feature>
- `path/to/test/file.py` — <why: test patterns to mirror, fixtures to reuse>
- `docs/decisions/<decision>.md` — <why: prior decision this plan inherits>
- <external URL> — <why: API contract, library reference>

If a planned task touches a file or pattern not listed here, add it to References before handoff. Empty list is acceptable for greenfield tasks; explicitly write `- (none — greenfield)` rather than omitting the section.

---
```

## Bite-Sized Task Granularity

**Each step is one action (2-5 minutes):**
- "Write the failing test" - step
- "Run it to make sure it fails" - step
- "Implement the minimal code to make the test pass" - step
- "Run the tests and make sure they pass" - step
- "Commit" - step

## Task Structure

````markdown
### Task N: [Component Name]
**Type:** value_unit | shared_prerequisite | adr
**Depends on:** T2 (data), T4 (knowledge) | none

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

**Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## Task Taxonomy

<!-- Canonical definition of task types + dependency types. phase-4c-verification.md and phase-5-implementation.md reference this section — keep in sync. -->

### Task Types

| Type | When | Example |
|------|------|---------|
| `value_unit` | Delivers one coherent, independently verifiable outcome | "Add tenant search endpoint" |
| `shared_prerequisite` | 2+ later tasks depend on this at a shared boundary | "Create base service class with audit logging" |
| `adr` | Technical decision that constrains multiple tasks | "Choose between WebSocket and SSE for real-time updates" |

### Dependency Types

| Type | Meaning | Parallelizable? |
|------|---------|-----------------|
| `data` | Needs schema/contract/interface from predecessor | No — must complete first |
| `build` | Needs compiled output or deployed artifact | No — must complete first |
| `knowledge` | Benefits from insights but can proceed with assumptions | Yes — record assumptions |

### Task Ordering

1. `shared_prerequisite` tasks first
2. `adr` tasks next
3. `value_unit` tasks in dependency order
4. Tasks with only `knowledge` dependencies are parallelizable — note this explicitly in the plan

### Granularity Criteria

Right-size each task using these indicators:

- **Too large → split:** spans unrelated service boundaries, mixed concerns in acceptance criteria, would need 2+ independent design docs
- **Too small → merge:** no independent acceptance criterion, only verifiable as part of parent task, config-only change meaningless without parent
- **Right-sized:** single service boundary or defined cross-service interaction, at least one independently verifiable acceptance criterion, dependency depth ≤ 2

## Phantom-Completion Audit (HARD GATE before completion)

Before announcing completion or invoking cleanup, audit the plan's task checklist for **phantom completions** — checkboxes marked `[X]` (or TodoWrite items marked `completed`) that lack corresponding code artifacts.

**Why:** Generic verification (`verification-before-completion`) checks individual claims at fix-time. This step is the orthogonal post-batch check: every task the plan said it would produce must actually exist on disk.

**Procedure:**

1. Re-read the plan's task list. For each `[X]` task, extract the artifacts the task promised:
   - Files listed under `**Files:**` → Create / Modify / Test paths
   - Functions, classes, endpoints, or migration revisions named in step bodies
2. Verify each artifact:
   ```bash
   # Files promised by the plan
   git ls-files <path>            # exists on disk and is tracked
   git diff origin/main -- <path> # actually contains changes
   # Symbols promised by the plan
   rg -n "def <function_name>|class <ClassName>" <path>
   # Migration revisions
   alembic heads                  # new revision present
   ```
3. For each task, classify:
   - **Real:** all promised artifacts present + non-empty diff → leave `[X]`.
   - **Phantom:** task marked `[X]` but artifact missing, file unchanged vs `origin/main`, or symbol absent → downgrade to `[~]` and surface in the report.
   - **Partial:** some artifacts present, some missing → downgrade to `[~]`, list the missing ones.

4. **If any phantom or partial items found:** STOP. Do not proceed to completion. Either complete the missing work or amend the plan to remove the unkept promise (with explicit justification). Never silently drop a task.

5. **If all `[X]` tasks verified real:** include the audit summary in the completion hand-off ("Phantom-completion audit: N tasks, all verified — no missing artifacts").

**Skip criteria:** Plans with <3 tasks where every task already had its diff inspected during the inter-task verification gate.

## Multi-Surface Features: Phased Commits with Green Between

For features that span >500 LoC across multiple surfaces (backend + client + infra, or API + UI + migration), land the work as N phase commits on a single branch rather than one monolithic commit. Each phase leaves both (or all) test suites green. Label phases A–F in commit messages.

**Write the inter-phase DAG into the plan doc explicitly:**
- "Phase A — schema + storage foundation"
- "Phase B — service layer (depends on A's schema)"
- "Phase C — parallel critic/worker (independent, can land after A)"
- "Phase D — client UI (depends on B's API shape)"
- "Phase E — integration surface (depends on C's result schema)"
- "Phase F — version bump + changelog + final verify"

Surface integration assumptions **before** merge, not during review.

**Benefits:**
- Reviewable — no 1,600-line diffs. Each phase is a readable commit.
- Bisectable — a regression points to a single phase commit.
- Rollback-per-phase if needed.
- User can review phase-by-phase at their own pace rather than in one mega-session.

**Skip this pattern when:**
- Changes can't individually be green (e.g., atomic refactors that must migrate all call sites at once). Use scaffolding + migration + cleanup as separate PRs instead.
- Total diff is <500 LoC — overhead isn't worth it.

**Verification between phases (hard gate):** full test suite passes after each phase commit. If a phase breaks tests, fix before the next phase — never let green drift across multiple phases.

**Learned from:** ToneGuard v0.3.0 (PR #23). 6 phases (A–F), 1,633 insertions, 22 files, all tests green between each. User reviewed phase-by-phase; CodeRabbit only needed to look at the final diff. Zero regressions between phases.

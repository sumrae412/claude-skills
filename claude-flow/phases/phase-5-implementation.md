# Phase 5: Implementation (TDD + Defensive Patterns)

<!-- Loaded: after Phase 4d (or Phase 4 for lite) | Dropped: after tests+lint pass -->
<!-- Output: $diff contract -->
<!-- Implementation detail for mutation gate, visual verify, authoring-time lookups, and cross-model retry has moved to memory/ entries (mutation_gate_component, visual_verify_gate, authoring_time_lookups, cross_model_retry_ladder). This file orchestrates; it no longer documents internals. See memory/phase5_inline_to_references.md. -->

---

## Streaming watches (Monitor tool)

For long-running tests, dev-server tails, or worker logs during implementation, use `Monitor` instead of polling via Bash. Each stdout line streams as a notification while the executor keeps drafting. Filter must include failure signatures (`ERROR|Traceback|FAILED|Killed|OOM`), not just success markers — silence is not success. See `references/monitor-tool-patterns.md` §Phase 5 for recipes (test loops, dev-server tails, worker watches) and decision rules vs. `Bash run_in_background`.

---

## Context Management

Load `references/phase-5-context-management.md` only when:

- the loop is long enough to threaten context limits
- you are dispatching multiple implementer subagents
- compaction behavior itself becomes relevant

Phase 5 consumes:

- `$verified_plan` or `$plan`
- `$exploration`
- `$requirements`
- `$test_skeletons` on full path

Phase 5 produces:

- `$diff`

Never pass to subagents:

- advisor transcripts
- rejected architecture details
- Phase 0 loading decisions
- raw clarification Q&A

---

## Phase 5: Implementation

<HARD-GATE>
User must approve the plan before any implementation begins.
</HARD-GATE>

### Pre-Implementation: Verify External API Contract

<HARD-GATE>
If ANY plan step involves calling an external API (GitHub, Google Calendar, Twilio, OpenAI, DocuSeal, Stripe, Supabase, Railway, Sentry, Slack, etc.), verify the current API contract BEFORE writing code. Do NOT code against external APIs from memory — endpoints, request formats, and auth patterns change between versions. This gate applies even if you loaded the integrations skill in Phase 0.
</HARD-GATE>

Load `references/phase-5-external-api-gate.md` only when the current step
touches an external API.

### Create TodoWrite Items

Break the plan into individual TodoWrite items. Mark each complete as you finish it.

### Execute Each Step

For each plan step:

```
1. Write test FIRST (see `claude-flow/references/test-driven-development.md`)
   - Test the expected behavior, not the implementation
   - Include edge cases identified in Phase 3

2. Implement to make the test pass
   - Follow patterns discovered in Phase 2
   - Apply defensive patterns throughout:
     UI → guard clauses, feedback states, loading/error/success
     Backend → input validation, error handling, no silent swallows

3. Run test → verify green
   - If test fails and the error is NOT self-explanatory:
     invoke /investigator with the failure as input.
     Review the evidence matrix BEFORE attempting a fix.
     (Prevents fix-retry loops on complex failures.)

   3a'. **Implementer pushback protocol:** When a code-quality or spec-review reviewer makes claims about external-tool behavior (CLI flag semantics, config discovery order, exit-code meanings), implementers MUST verify empirically before applying the fix. Record that verification in the run manifest or review notes, not in product code comments. Reviewer authority does not override tool output. See `reviewer_claims_need_verification.md`.

   3a. If one fix attempt already failed, load
       `references/phase-5-retry-and-facts.md` and apply the
       explain-before-fix gate before iter-2.

   3b. After the target test passes, load
       `references/phase-5-retry-and-facts.md` and run the scoped
       regression guard before proceeding.

   3e. After tests and guard pass, load
       `references/phase-5-retry-and-facts.md` and extract reusable
       context facts into `$diff.context_facts` when the task discovered
       new domain knowledge.

4. Run static analysis on changed files (catch issues early):
   semgrep --config=.semgrep.yml <changed-files>
   ast-grep scan <changed-directory>

   Fix any ERROR-level issues before proceeding.

5. Mark TodoWrite item complete

6. Inter-task verification gate (proactive, not just reactive):
   Run full test suite + lint + build check BEFORE starting next task.
   Catches cross-TASK regressions (step 3b catches within-FIX ones).
   See `claude-flow/references/subagent-driven-development.md` for full gate protocol.
   Skip full suite for Task 1 or trivial tasks.
   If gate fails → fix regression → re-verify → then proceed.
```

### Long Loops and Fresh Context

If the plan has 5+ steps or context pressure is noticeable, load
`references/phase-5-context-management.md` and compact the working set.

When dispatching the next task's subagent, include prior
`$diff.context_facts` as a short "Known context from earlier tasks" preamble.

### Advisor: Mid-Implementation (optional)

Only at genuinely ambiguous decision points. Not routine steps.
Dispatch Sonnet with: specific decision context from current `$plan` step.
Question: focused on the specific ambiguity.

Downgraded from Opus to Sonnet 2026-04-24 after a 15-trial dual-judge eval showed the two models tied on mid-implementation reasoning (both 0.989 judge score). See `decisions/2026-04-24-sonnet-vs-opus-phase-downgrade.md` in the claude_flow repo.

**When to call:** non-obvious integration patterns, conflicting precedents, step diverging from plan in ways affecting later steps.
**When NOT to call:** routine implementation, standard TDD cycles with clear requirements, unambiguous plan steps.

### Parallel Subagent Dispatch (For Independent Steps)

When the plan has 3+ steps with no dependencies between them:

```
Follow `claude-flow/references/subagent-driven-development.md`:
  → Dispatch parallel implementation agents with model: "sonnet"
  → Each follows the same TDD + defensive pattern
  → Merge results when all complete
```

> **Explicit parallel fan-out (Opus 4.7):** When dispatching N independent reviewers / researchers / implementers across M items, emit a single message with N tool-use blocks. Do **not** issue them sequentially — 4.7's default bias is under-parallelization.

<!-- Task taxonomy (types + dependency types) defined in writing-plans/SKILL.md. Keep in sync. -->
**Dependency-aware dispatch:**
- `data` or `build` dependencies → strictly sequential (predecessor must complete first)
- `knowledge` dependencies → parallelizable (dispatch concurrently, record assumptions in each subagent's context)
- Tasks with no dependencies → parallelizable
- `shared_prerequisite` tasks → always execute before dependent `value_unit` tasks

### Conditional Specialist Reviews (During Implementation)

When a plan step produces code matching a specialist's domain, dispatch the specialist immediately (**sonnet**, background) before proceeding to the next step:

| Trigger | Agent | Action on CRITICAL |
|---------|-------|--------------------|
| Alembic migration file created/modified | `migration-reviewer` | Fix before next step |
| Google Calendar/Drive/Gmail API code | `google-api-reviewer` | Fix before next step |
| `async def` with I/O operations | `async-reviewer` | Fix before next step |

MEDIUM/LOW findings defer to Phase 6 review. Agents that ran in Phase 5 are **skipped** in Phase 6 (no double review).

### Best Practices Applied Throughout

| When | Apply |
|------|-------|
| Writing code | Type hints, async patterns, service layer |
| Changing schema | Migration checklist, foreign keys |
| Adding endpoints | Route naming, HTTP methods, rate limiting |
| Modifying JS | Null checks, event handlers, cache bust |
| UI flows | defensive-ui-flows: guard feedback, state flags, overlay inline |
| Backend error handling | defensive-backend-flows: no silent swallows, log or re-raise |
| Data migrations | defensive-backend-flows: copy before delete, reversible ops |
| Cross-module calls | defensive-backend-flows: respect encapsulation, public wrappers |

**State transition:** If tests+lint pass, transition to phase-5.5. If failed
and iteration < 3, load `references/phase-5-retry-and-facts.md` and follow the
retry ladder. If iteration limit is reached, set status to "failed" and surface
it to the user.

---

## Multi-surface features — phased commits

For features spanning multiple surfaces (backend + client + infra, >500 LoC), Phase 5 MAY land as N logical phase commits on one branch rather than a single commit. Each phase must leave full test suites green. See `executing-plans` § "Multi-Surface Features: Phased Commits with Green Between" for the DAG-documentation convention, labeling (A–F), and skip criteria.

---

## Turn-closing summary discipline

When closing a turn that includes Edit/Write tool calls, cite evidence in the summary: `path/to/file.md:L12-18` refs, `git diff --stat` output, or `gh pr view --json mergedAt`. The Edit tool's "updated successfully" response doesn't render prominently in the user transcript, so bare claims ("edits applied", "fixed", "shipped") read as unverifiable and trip approval-challenge hooks. Autocommit/stop hooks can also land work between your edits and the summary — cite the commit SHA or PR URL when that happens. Same bar for Phase 6 quality-gate summaries. Project-level analog: courierflow CLAUDE.md boundary #8.

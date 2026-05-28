# $plan
<!-- Produced by: Phase 4b | Consumed by: Phases 4c, 4d, 5, 6 reviewers -->

## Schema

steps:
  - id: N
    description: string
    files: string[]       # exact paths to create/modify
    type: value_unit | shared_prerequisite | adr
    depends_on:
      - step: N
        type: data | build | knowledge
    test_requirements: string
    success_contract:     # machine-checkable proof step is done — see Success Contract below
      command: string     # exact shell command (or `N/A` for non-executable steps; must explain why)
      expected: string    # one-line truth check — what substring/exit code/artifact state proves success
      artifact: string    # optional — path to file/output the command produces or modifies
    status: pending | complete

## Success Contract

Each step's `success_contract` is the **machine-checkable** companion to `test_requirements` (which stays freeform prose). It exists so Phase 5.5 reflection and Phase 6 reviewers can verify completion without re-deriving criteria from the plan text.

Rules:
- `command` must be executable as-is from repo root. No placeholders, no "edit this first."
- `expected` is one line of truth (e.g. `pytest: 5 passed, 0 failed`, `exit 0`, an HTTP 200 from the new endpoint). Vague phrasing ("tests pass") fails this rule.
- **Test observable behavior, not internal code state** (Radha, AgentField 2026 — "verifier visibility"). Verifiers the executor can see become targets it can over-fit to. A contract like `grep -c old_api == 0` can be passed by renaming `old_api` to `old_api_renamed` without doing the migration. Prefer end-user-observable proofs (API response, UI render, consumer test still green, file produced with expected content) over greps/flag-checks. When the step really is a code-state check (dead-code removal), use a higher-level proxy — e.g. *the consumer's test suite still passes after the symbol is gone* — not just the absence of a token.
- `artifact` is optional. Use when the step produces a file (migration, doc, config) whose existence or content is the proof.
- For pure-refactor or doc-only steps where no command applies, set `command: N/A` and put the equivalent check in `expected` (e.g. `expected: "git diff --stat shows only docs/ changes"` and a one-liner the user can run).

Phase 4 advisor authors this. Phase 5.5 reflection executes every contract before declaring Phase 5 done. Phase 6 reviewers receive contracts (not test_requirements prose) to slim payload.

## Notes

- Populated after user approves plan in Phase 4b (post-advisor stress-test)
- Phase 4c verifies file paths and function references against codebase
- Phase 5 dispatches based on dependency types: data/build = sequential, knowledge = parallelizable
- Phase 6 reviewers receive step id + files list + `success_contract` (not full descriptions) for payload slimming
- status updated during Phase 5 as steps complete; a step is `complete` only when its `success_contract.command` exits per `expected`

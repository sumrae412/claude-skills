# Container Use Execution Backend

Container Use is an optional Phase 5 backend for parallel implementation agents.
It supplies isolated containers, per-agent Git branches, command history, and
inspectable handbacks. It does not replace claude-flow planning, model routing,
acceptance contracts, review, merge, or completion verification.

## Enablement gate

Use this backend only when all of the following are true:

- `container-use version` succeeds.
- Docker is installed and reachable: `docker info` succeeds.
- The project has a committed `.container-use/environment.json` with an
  explicit, suitable base image. For Python projects, prefer a versioned image
  such as `python:3.12-slim`; the default Ubuntu image may not contain Python.
- The task is safe to run without secrets, production credentials, or live
  application services.
- Each implementation step is independent and has a separate success contract.

If any prerequisite fails, use ordinary claude-flow worktree dispatch and report
Container Use as unavailable. Do not silently fall back after an environment
has been created, because that obscures isolation and evidence failures.

## Phase 5 sequence

1. Confirm the project configuration is committed and the base image is
   appropriate for the repository's test command.
2. Create one Container Use environment per independent implementation agent.
   Agents must use Container Use environment tools for file changes and command
   execution; they must not edit the host checkout or manipulate `.git` inside
   an environment.
3. Give each agent a bounded task, named files, test command, and handback
   fields: environment ID, changed files, exact test command and output,
   warnings, and whether the environment remains available.
4. Verify the recorded Container Use log and diff independently of the agent's
   prose. A passing claim without a recorded command result is unverified.
5. Review each environment's diff before applying or merging any work. The
   host branch remains unchanged until the normal Phase 5/6 gates accept it.
6. Delete disposable environments after evidence capture and confirm
   `container-use list` no longer shows them.

## Evidence to retain

Record these measurements in the run handback:

- setup time from dispatch start to environment creation;
- implementation/test success count across agents;
- exact test output from each environment's log;
- handback completeness and any agent hang or timeout;
- cleanup duration and an empty post-cleanup environment list.

The first failed test or incomplete handback is a backend failure for the run,
even if the code diff looks correct. Fix the environment contract and rerun;
do not adopt a partially proven backend.

## Review and safety boundary

Container Use makes work isolated and observable, not automatically correct.
The ordinary claude-flow rules still govern TDD, dependency ordering,
independent verification, secrets, external side effects, review, and merge.
Use `container-use log <env>` and `container-use diff <env>` as evidence sources,
not as permission to merge.

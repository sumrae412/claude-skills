# Phase 5 Retry, Guard, and Context Facts

Load this reference only when:

- a test still fails after one fix attempt
- you need the regression-guard protocol
- you are capturing reusable facts for later tasks

## Explain-Before-Fix Gate

If one fix attempt already failed, do not immediately try a second patch.

Ask the executor:

```text
The previous fix didn't resolve the failure. Explain why the
current code still fails the test. Don't write any code.
```

Only after reading the explanation should iter-2 begin.

## Scoped Regression Guard

After the target test passes, run a broader guard:

```text
a) same test module
b) affected package
c) full suite only if the change spans packages
```

Default to the narrowest valid guard.

If the guard fails:

- keep the target fix
- fix the regression
- rerun both the target test and the guard
- max 2 guard-fix cycles, then escalate

Tag this failure class as `guard-regression`.

## Context-Fact Extraction

After tests and guard pass, but before static analysis, extract reusable
domain facts into `$diff.context_facts`.

Categories:

1. `SCHEMA`
2. `API`
3. `PATTERN`
4. `GOTCHA`

Constraints:

- max 10 facts per task
- only novel facts
- skip for doc-only/config-only work
- skip if extraction takes more than 30 seconds

These facts are consumed by later Phase 5 tasks and by Phase 6 reviewers.

## Retry Ladder

State transition:

- iter 1: same executor
- iter 2: same executor, higher thinking budget, after explain-before-fix
- iter 3: cross-model investigator path

Retry inputs can include:

- failing test output
- lint failures
- adversarial blockers from Phase 6
- explain-before-fix analysis from iter 1

If iteration limit is reached, mark the phase failed and surface it to the user.

## Adversarial Break Cases

If Phase 6 produced sub-threshold scored findings, render them into the next
retry prompt as concrete break cases:

```text
The following break cases were scored below 7/10 in the prior iteration:

    {adversarial_blockers}

Address each break case in this iteration.
```

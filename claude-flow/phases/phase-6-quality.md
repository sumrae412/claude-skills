# Phase 6: Quality + Finish

<!-- Loaded: after Phase 5.5 | Dropped: workflow complete -->

---

## Risk-Budgeted Cascading Review

Reviews are structured as a cascade: Tier 1 runs first, then specialized
reviewers fill gaps only when the budget and diff justify it.

### Active Flow

1. Resolve the review base SHA from workflow state or git history:
   ```bash
   python3 <claude-flow-root>/scripts/resolve_review_base.py --project-root . --json \
     > /tmp/review-base.json
   REVIEW_BASE_SHA="$(python3 - <<'PY'
import json
print(json.load(open('/tmp/review-base.json'))['review_base_sha'])
PY
)"
   ```
   Then persist the exact resolved metadata:
   ```bash
   python3 <claude-flow-root>/scripts/run_manifest.py set-review-base \
     --manifest .claude/runs/<session-id>.json \
     --review-base-sha "$REVIEW_BASE_SHA" \
     --source "<source from /tmp/review-base.json>" \
     --base-ref "<base_ref from /tmp/review-base.json>" \
     --state-file .claude/workflow-state.json
   ```
2. Get the diff file list:
   `git diff --name-only "$REVIEW_BASE_SHA"..HEAD`
3. Scrub the diff payload before any reviewer sees it:
   ```bash
   git diff "$REVIEW_BASE_SHA"..HEAD | \
     python3 <claude-flow-root>/scripts/scrub_review_payload.py > /tmp/claude-flow-review.diff
   ```
4. Run the selector script:
   ```bash
   git diff --name-only "$REVIEW_BASE_SHA"..HEAD | \
     python3 <claude-flow-root>/scripts/select_reviewers.py --workflow-path <path>
   ```
5. Use the selector output:
   - `review_budget`
   - `budget_reasons`
   - `by_tier`
   - `budget_skipped`
   - `conditional_skipped`
   - `registry_sources`
6. Run Tier 1 (`coderabbit`) first.
7. If Tier 1 returns no HIGH+ findings:
   - skip Tiers 2-4
   - run the design-review pass only if UI files changed
   - proceed to verification
8. If Tier 1 returns HIGH+ findings:
   - dispatch the remaining reviewers in `by_tier` order
   - run reviewers within a tier in parallel
9. If `lightweight-reviewer` is selected, load
   `references/phase-6-review-operations.md` for the batched checklist rules.
10. If UI files changed, load `references/phase-6-design-review.md`.
11. For CLI-backed reviewers, use `resolved_runner_script`, not the raw
   `runner_script`.
12. For scored reviewers, run:
   ```bash
   python3 <claude-flow-root>/scripts/aggregate_reviewer_findings.py --reviewer <output.json> --registry <claude-flow-root>/reviewer-registry.json
   ```

Load `references/review-budgets.md` only when you need the full low/medium/high
budget rationale.

### Reviewer Conventions

- All reviewers are advisory by default.
- Heuristic grep-based checks need user confirmation before a FAIL verdict.
- Tier 1 stays reserved for `coderabbit`.
- Reviewers whose `min_budget` exceeds the selected `review_budget` are skipped
  deterministically and reported under `budget_skipped`.

## Eval Contamination Guard

Include this in all reviewer prompts:

```text
ACCEPTANCE CRITERIA SOURCE: The following requirements were defined
BEFORE implementation began (Phase 3). Use these as your primary
evaluation standard — not patterns observed in the code itself.

$requirements.acceptance_criteria

Evaluate whether the implementation ($diff) satisfies these criteria.
If the implementation diverges from $requirements, flag it — even if
the code is internally consistent.
```

If `$requirements` is unavailable on a path, tell reviewers requirement-level
validation is skipped and the pass is code-quality-only.

## Judge Bias Guard

Include this in all LLM-as-judge, scored-reviewer, reducer, or candidate
selection prompts:

```text
EVALUATION PRIORITIES (in order):
1. Correctness and completeness against the acceptance criteria, tests, issue,
   and observable behavior.
2. Regression safety and realistic failure-mode coverage.
3. Minimality, cleanliness, style, formatting, and gold-like resemblance are
   tiebreakers only after correctness is established.

Do not choose or score a candidate higher merely because it is concise, clean,
focused, familiar, or similar to a canonical answer. Do not reject a candidate
merely because it contains redundant changes, helper code, docs, comments, or
tests if it is functionally correct. A messy complete fix beats a clean partial
fix.
```

For candidate-selection reducers, require the judge to mentally trace the
failing scenario through each candidate before using minimality as a tiebreaker.
For scored reviewers, require every sub-threshold score to cite a concrete
production break case rather than an aesthetic objection.

## Reviewer Payload Contract

All reviewers receive:

- scrubbed `$diff.git_diff`
- `$requirements.acceptance_criteria` only
- `$plan` step IDs and files only
- a short role description plus checklist focus

If the scrubber redacted anything, include the redaction summary in the review
payload so reviewers know why a token/value was masked.

Default reviewers:

| Cascade Tier | ID | `subagent_type` / runner | Model | Min Budget | Condition |
|--------------|----|--------------------------|-------|------------|-----------|
| 1 | `coderabbit` | `coderabbit:code-reviewer` | sonnet | `low` | Always — consolidated first pass |
| 2 | `safety-reviewer` | `pr-review-toolkit:silent-failure-hunter` + `security-reviewer` | sonnet | `medium` | Always — silent failures + security |
| 2 | `test-coverage-analyzer` | `pr-review-toolkit:pr-test-analyzer` | sonnet | `medium` | Always — test gaps |
| 2 | `curmudgeon-review` | `scripts/curmudgeon_review.sh` | gpt-5-codex | `high` | Always — non-Anthropic second opinion |
| 2 | `adversarial-breaker` | `general-purpose` | sonnet | `high` | Always — scored reviewer |
| 3 | `migration-reviewer` | `migration-reviewer` | sonnet | `high` | Alembic/migration files in diff |
| 3 | `google-api-reviewer` | `google-api-reviewer` | sonnet | `high` | Google/calendar files + content match |
| 3 | `async-reviewer` | `async-reviewer` | sonnet | `medium` | 3+ async patterns in Python files |
| 3-4 | `lightweight-reviewer` | `general-purpose` | haiku | `low` | Batched lightweight checklist |

Agents that already ran as Phase 5 specialists are skipped here to avoid double
review.

## Findings Resolution

If Tier 1 or later reviewers produce HIGH+ findings, load
`references/phase-6-review-operations.md` and use its review-fix-recheck loop.

That same reference also carries:

- batched `lightweight-reviewer` checklist construction
- optional strategic pre-review
- cross-cutting synthesis
- optional post-review simplifier

## Static Analysis Gate

```bash
pyright
semgrep --config=.semgrep.yml --error app/
ast-grep scan app/
```

Fix ERROR-level issues before continuing.

Prefer the commands discovered in the Phase 0 capability snapshot over guessed
tool names when the project has a declared lint/typecheck setup.

## Verification Gate

Invoke `verification-before-completion`:

- all tests pass
- no unintended file changes
- implementation still matches the request
- no regressions
- static analysis is clean
- if this session changed the workflow skill itself, confirm existing passing
  behavior is preserved
- record `review_base_sha`, review budget, redaction count, reviewer list, test
  commands, and exit codes in the run manifest

Preferred commands:

```bash
python3 <claude-flow-root>/scripts/run_manifest.py record-review \
  --manifest .claude/runs/<session-id>.json \
  --summary-file /tmp/reviewer-selection.json \
  --redactions-file /tmp/review-redactions.json \
  --reviewers-run coderabbit safety-reviewer

python3 <claude-flow-root>/scripts/run_manifest.py record-command \
  --manifest .claude/runs/<session-id>.json \
  --command-text "python3 -m pytest -q" \
  --exit-code 0 \
  --category tests \
  --cwd "$PWD"
```

Optional: if CI exists, run a headless smoke check before finishing.

### Streaming watches (Monitor tool)

For PR check progression, post-deploy soak, and CodeRabbit review polling, use `Monitor` instead of polling via Bash. Each terminal-state event streams as a notification while finishing tasks proceed in parallel. PR check loop must emit on every terminal state (`success|failure|cancelled|timed_out`), not just success — silence ≠ pass. See `references/monitor-tool-patterns.md` §Phase 6 for the canonical PR-checks loop and post-deploy log-tail recipes.

## Finish Branch

Invoke `/cleanup`:

1. run the full test suite
2. commit with a conventional message
3. present merge / PR / keep / discard options
4. execute the user’s choice

`/cleanup` then handles `session-learnings` and repo sync.

## Capture Learnings

`session-learnings` should capture:

- discovered patterns
- defensive rules worth keeping
- memories to persist
- workflow trace: which phase caught which issue
- failure tags from `references/failure-taxonomy.md`
- at most one scoped workflow-improvement proposal

## Workflow Retrospective

After the feature completes, record:

1. which phase caught each issue
2. failure tags by issue
3. whether any phase felt wasted or underpowered
4. whether reviewer scope was calibrated correctly

If the retrospective suggests a workflow improvement, keep it to one targeted
change.

## Optional Follow-Up: `/personas`

If the diff changed user-facing flows in a non-trivial way, optionally offer a
synthetic beta pass before real-user testing.

## State Transition

Write `artifacts.review_findings`.

- if high/critical findings remain and iteration < 2, transition back to
  Phase 5 with status `fixing`
- otherwise set workflow status to `completed`

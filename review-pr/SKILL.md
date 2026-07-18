---
name: review-pr
description: Unified PR/code review pipeline. Runs CodeRabbit CLI first (external, no Claude tokens) then Claude fills gaps CodeRabbit misses — project conventions, over-engineering, type design, production readiness. Use on "review this PR", "review my changes", "code review", "/review-pr".
user-invocable: true
allowed-tools: Bash, Read, Grep, Glob, Task
---

# Review PR — Unified Pipeline

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad exploration, repeated file reads, multi-file scans, or heavy reference loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant patterns inline instead of loading extra material.

Two-stage code review. Stage 1 runs CodeRabbit externally (doesn't spend Claude tokens).
Stage 2 runs Claude only on what CodeRabbit's blind spots are, conditional on what the diff
actually contains. Final output is one merged report.

## When to use

- User asks for a PR review, code review, or "review my changes"
- User invokes `/review-pr`
- Before opening or merging a PR
- Before committing a large change

## When NOT to use

- **Plan/architecture reviews** → use `debate-team` (different models, different scope)
- **Standalone pre-ship ops audit** (no code review needed) → use `production-readiness-check`
- **Responding to a Sentry bot comment** → use `sentry:sentry-code-review`
- **Security-only audit** → dispatch the `security-reviewer` agent directly

---

## Pipeline

### Stage 0 — Scope

```bash
git status --short
git diff --name-only HEAD  # or against PR base branch
```

If no changes: stop and tell the user nothing to review.

Capture:
- Changed file list
- Whether any `*.py` / `*.ts` / `*.tsx` are new (for type-design trigger)
- Whether any `alembic/` / `migrations/` / `Dockerfile` / `docker-compose*` / `.github/workflows/` changed (for production-readiness trigger)
- Whether auth/session/permission files changed (for security-reviewer trigger)

### Stage 1 — CodeRabbit (run first, always)

CodeRabbit catches the bulk of generic issues (bugs, style, basic security, test gaps) without
spending Claude tokens. Run it before any Claude work.

**Preflight — skip if already verified this session:**
```bash
coderabbit --version 2>/dev/null && coderabbit auth status 2>&1 | head -3
```

- CLI missing: tell the user to install via `curl -fsSL https://cli.coderabbit.ai/install.sh | sh`
- Not authenticated: tell the user to run `coderabbit auth login`

**Run:**
```bash
coderabbit review --plain -t all
# add --base <branch> when reviewing a feature branch against a non-main base
```

**Filter findings to the actual PR diff.** `coderabbit review --base <branch>` scans working-tree contents, not just committed changes — untracked or uncommitted files in your worktree will appear in findings even though they're not in the PR. Before treating a finding as PR-relevant, intersect against the PR diff:
```bash
git diff --name-only origin/main...HEAD > /tmp/pr-files.txt
# then drop any finding whose path isn't in /tmp/pr-files.txt
```
Hit on courierflow_beta [PR #17](https://github.com/sumrae412/courierflow_beta/pull/17): 3 of CR's findings were on `.playwright-mcp/*.yml` and `scripts/launchd-*.sh` — untracked files not part of the PR.

**If output is truncated or rate-limited**, parse the JSON cache directly instead of re-running:
```bash
python3 -c "import json,glob; [print(json.load(open(f))) for f in glob.glob('$HOME/.coderabbit/reviews/*/*/reviews/*/*.json')]"
```

**Capture CodeRabbit findings** as a structured list with `file`, `line`, `severity`, `title`, `comment`.
Group into: Critical, High, Medium, Low.

### Stage 2 — Claude gap-fill (two parallel axes)

Only run the checks below. Do NOT re-run generic code review — CodeRabbit already did that.

Run both axes as parallel subagents via the Task tool (single message, two Task calls). Each axis
reports separately — a change can pass Standards and fail Spec, or vice versa. The two axes are
deliberately kept separate so one axis's pass cannot mask the other's miss.

Do not use the full `pr-review-toolkit` plugin — this skill replaces it.

Adapted from `mattpocock/skills` `review` (Standards/Spec axis separation), 2026-06-26 source read.

---

#### Axis A — Standards

**What it checks:** does this change follow our conventions, house style, and engineering quality
expectations? This is independent of what the PR was supposed to do.

Dispatch a single Task subagent with:
- The diff
- The relevant CLAUDE.md contents (read `CLAUDE.md` and any nested ones in the changed paths)
- This prompt:

> Run the following checks against the diff. Report each finding with file:line and a one-line
> recommendation. Deduplicate against CodeRabbit findings already captured (skip file+line already
> flagged). Return a Standards Report with sections for each check that produced findings.
>
> **A1. Project conventions (always run)**
> For each rule in CLAUDE.md of the form "don't X", "always Y", "NOT a standalone Z", grep the
> diff for violations.
>
> **A2. Over-engineering / vanity (run when ≥3 new files or new abstractions)**
> Triggers: `git diff --stat` ≥3 new files; new abstract class/interface with single impl;
> config files larger than the code they configure; plugin/registry/factory for <3 concrete cases.
> Score each finding V0-V3. Report V1+ only: what, file:line, simpler alternative, kill cost.
> Max 5 findings.
>
> **A3. Type design (run when new types added)**
> Triggers: diff adds `class`, `interface`, `type`, `@dataclass`, `TypedDict`, `NamedTuple`.
> Rate each new type 1-10 on Encapsulation, Invariant Expression, Usefulness, Enforcement.
> Flag concerns in <3 sentences. Skip types that score ≥8 on all four.
> (Alternatively dispatch `pr-review-toolkit:type-design-analyzer` if the plugin is enabled.)
>
> **A4. Silent-failure check (run when error-handling code changed)**
> Triggers: diff contains `try`, `catch`, `except`, `.catch(`, `Result<`, or error-handling patterns.
> Flag CRITICAL: empty catches, broad catches hiding unrelated errors, mock/stub fallbacks in
> production, errors returned as null/undefined without logging.
> Flag HIGH: missing actionable user feedback, missing error IDs for observability.

---

#### Axis B — Spec

**What it checks:** does this change implement the intended behavior? Does it cover the cases the
PR author specified? Are there business-rule gaps or edge cases the diff doesn't handle?

**Spec source — find it first:**
1. Check if a spec doc / PRD / linked issue is available in context or referenced in the PR
   description.
2. If a spec doc is found: compare the diff against its requirements section by section.
3. **If no spec doc is available:** fall back to "intent inferred from the PR description + test
   coverage" — state this explicitly in the Spec Report header so a missing spec doesn't silently
   void the axis.

Dispatch a single Task subagent with:
- The diff
- The PR description / commit message
- The spec doc (if found) OR the instruction to infer from PR description + tests
- This prompt:

> Run a Spec review against the diff. Return a Spec Report with sections for each check that
> produced findings. Open with one line stating the spec source used (linked doc, PR description,
> or inferred-from-tests).
>
> **B1. Intent coverage**
> List the behaviors the PR description (or spec) says this change should produce. For each,
> confirm whether the diff implements it. Flag any stated intent with no corresponding code change.
>
> **B2. Business-rule correctness**
> Identify the domain invariants the change touches (e.g. "a refund cannot exceed the original
> charge", "only authenticated users can write"). For each invariant, verify the diff enforces it
> correctly — wrong condition, off-by-one, missing guard, etc.
>
> **B3. Edge cases vs. specified behavior**
> For each user-facing behavior in the diff, check: null/empty input, boundary values, concurrent
> access (if relevant), error path. Flag cases the PR description specified that the diff doesn't
> handle, AND cases the diff silently handles differently from the spec.
>
> **B4. Test coverage of spec**
> Scan added/changed tests. For each specified behavior in B1, is there a test that would fail if
> that behavior regressed? Flag specified behaviors with no test. Flag tests that mirror
> implementation 1:1 (mock returns X, assert returns X) without defending a named invariant.

---

#### Stage 2 agent dispatches (run conditionally, alongside the axes)

These run as separate Task calls alongside the two axes when their triggers fire. They are not
part of the Standards or Spec axis — they own their own domains.

**Security (run when auth/session/permission paths touched)**

Trigger: diff touches files matching `auth*`, `session*`, `permission*`, `jwt*`, `password*`,
`oauth*`, `token*`, or `.env*`.

Dispatch the `security-reviewer` agent (Task tool, subagent_type="security-reviewer") with the
diff summary. Its findings feed into the final report.

**Production readiness (run when user says "pre-ship" or deploy config changed)**

Trigger:
- User invoked with `--pre-ship` flag, OR
- Diff touches `alembic/`, `migrations/`, `Dockerfile*`, `docker-compose*`, `.github/workflows/`,
  or `k8s/`

Invoke the `production-readiness-check` skill — it owns this domain and stays as a standalone
skill for pre-ship audits.

### Stage 2.5 — CodeRabbit thread operations (after applying fixes)

When responding to existing CodeRabbit review threads (reply, dismiss with reasoning, resolve),
load `references/gh-api-recipes.md` at Stage 2.5 — it holds the exact gh-api / GraphQL recipes
(reply-in-thread, resolve mutation, paginated thread listing) whose shapes matter.

Never resolve a thread without actually addressing it or replying with a reasoned dismissal.

### Stage 3 — Merge and report

Deduplicate findings across CodeRabbit + Claude axes by `(file, line)` proximity.
When CodeRabbit and Claude flag the same spot, prefer CodeRabbit's finding (more specific)
unless Claude adds unique context.

The Standards and Spec axes report separately before the unified severity roll-up. This is
intentional — a change that passes Standards can still fail Spec, and vice versa. Keeping
the axes separate makes that visible instead of collapsing it into a single severity list.

Load `references/report-template.md` at Stage 3 for the exact output structure (summary header,
Standards Report, Spec Report, unified severity roll-up, recommended action) and emit the final report in it.

## Notes

- Do not re-run CodeRabbit findings through Claude — that's double-paying for the same check.
- The two Claude axes (Standards, Spec) always run. Within each axis, individual checks are
  conditional on their triggers — running all checks unconditionally wastes tokens.
- **Standards axis** (Axis A) is trigger-conditional per check: A1 always, A2-A4 on triggers.
- **Spec axis** (Axis B) always runs. When no spec doc is present, B1-B4 infer from PR
  description + tests and say so explicitly — a missing spec does NOT void the axis.
- The `--pre-ship` flag adds the production-readiness agent dispatch regardless of other triggers.
- The `--quick` flag runs only Stage 1 (CodeRabbit) + Axis A check A1 (project conventions) —
  appropriate for small PRs.
- Axis separation is intentional: a change can pass Standards (correct conventions, good types)
  and fail Spec (wrong business rule, unhandled edge case), or vice versa. Collapsing them into
  one severity list hides that signal.
- **Scope discipline on findings** (pattern from [openclaw/agent-skills](https://github.com/openclaw/agent-skills)' autoreview "Scope Governor"): freeze the review baseline at dispatch, then classify every finding as *in-scope blocker*, *out-of-scope follow-up*, or *stop-and-escalate* — and route follow-ups to `spawn_task`/issues instead of letting the review balloon the PR. A review that keeps adding "while you're here" fixes past ~2× the original diff size has drifted; stop and escalate.
- **Candidate upgrade — outer-loop self-improvement** (not yet implemented here; blueprint: [Zach Lloyd](https://x.com/zachlloydtweets/status/2077428025474355521)): run the reviewer on every PR, let humans correct its comments, then have a periodic outer agent synthesize those corrections into a proposed update PR against this SKILL.md (new conventions, gotchas, false-positive patterns). If adopted, keep the two loops separate: inner = review the PR, outer = review the reviewer.
- **Injection posture for automated review runs** (same source): give the review agent read-only PR permissions and have CI post its structured `review.json` as comments, rather than granting the agent comment/write access — PR bodies and diffs are untrusted input, so the thing that reads them shouldn't also hold the pen.

## Related

- `debate-team` — multi-model cross-provider review for plans/architecture (not PR review)
- `production-readiness-check` — standalone ops-level pre-ship audit
- `sentry:sentry-code-review` — narrow, only for Sentry bot PR comments
- `security-reviewer` agent — standalone security audit (Task tool target)

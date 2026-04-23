---
name: review-pr
description: Unified PR/code review pipeline. Runs CodeRabbit CLI first (external, no Claude tokens) then Claude fills gaps CodeRabbit misses — project conventions, over-engineering, type design, production readiness. Use on "review this PR", "review my changes", "code review", "/review-pr".
user-invocable: true
allowed-tools: Bash, Read, Grep, Glob, Task
---

# Review PR — Unified Pipeline

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

**If output is truncated or rate-limited**, parse the JSON cache directly instead of re-running:
```bash
python3 -c "import json,glob; [print(json.load(open(f))) for f in glob.glob('$HOME/.coderabbit/reviews/*/*/reviews/*/*.json')]"
```

**Capture CodeRabbit findings** as a structured list with `file`, `line`, `severity`, `title`, `comment`.
Group into: Critical, High, Medium, Low.

### Stage 2 — Claude gap-fill (conditional, parallel where possible)

Only run the checks below. Do NOT re-run generic code review — CodeRabbit already did that.

Dispatch the conditional checks in parallel via the Task tool (single message, multiple Task calls).
Each subagent gets the diff + a narrow prompt. Do not use the full `pr-review-toolkit` plugin —
this skill replaces it.

#### 2a. Project convention check (always run)

CodeRabbit doesn't know your project's CLAUDE.md rules. Read `CLAUDE.md` (and any nested ones in the
changed paths). For each rule of the form "don't X", "always Y", "NOT a standalone Z", grep the
diff for violations. Report matches with file:line.

#### 2b. Over-engineering / vanity check (run when ≥3 new files or new abstractions)

Trigger heuristics:
- `git diff --stat` shows ≥3 new files, OR
- Diff introduces new abstract classes / interfaces with a single implementation, OR
- Config files added that exceed the code they configure, OR
- Plugin/registry/factory patterns introduced for <3 concrete cases

Run this prompt inline (not as a sub-agent — it's fast):

> Review the diff for vanity engineering — complexity added without proportional user value.
> Score each finding V0 (cosmetic) to V3 (compounding). For each V1+ finding, report: what,
> where (file:line), severity, why it fails "does a user need this?", the simpler alternative,
> and kill cost (hours/days). Max 5 findings. Skip V0.

#### 2c. Type-design check (run when new types added)

Trigger: diff adds `class`, `interface`, `type`, `@dataclass`, `TypedDict`, or `NamedTuple`.

Dispatch the `pr-review-toolkit:type-design-analyzer` agent if the plugin is enabled, OR
inline prompt:

> For each new type in the diff, rate 1-10: Encapsulation, Invariant Expression, Usefulness,
> Enforcement. Flag concerns in <3 sentences each. Skip types that score ≥8 on all four.

#### 2d. Silent-failure check (run when try/catch or error-handling code changed)

Trigger: diff contains `try`, `catch`, `except`, `.catch(`, `Result<`, or error-handling patterns.

CodeRabbit sometimes catches these, but not always for project-specific patterns. Run this inline:

> Scan every catch/except/error-handler in the diff. Flag CRITICAL: empty catches, broad catches
> that could hide unrelated errors, fallbacks to mock/stub in production, errors returned as
> null/undefined without logging. Flag HIGH: missing actionable user feedback, missing error IDs
> for observability. Report file:line, hidden-error-types, recommendation. Skip locations that
> CodeRabbit already flagged (dedupe by file+line).

#### 2e. Security-sensitive check (run when auth/session/permission paths touched)

Trigger: diff touches files matching `auth*`, `session*`, `permission*`, `jwt*`, `password*`,
`oauth*`, `token*`, or `.env*`.

Dispatch the `security-reviewer` agent (Task tool, subagent_type="security-reviewer") with the
diff summary. Its findings feed into the final report.

#### 2f. Production-readiness check (run when user says "pre-ship" or when deploy config changed)

Trigger:
- User invoked with `--pre-ship` flag, OR
- Diff touches `alembic/`, `migrations/`, `Dockerfile*`, `docker-compose*`, `.github/workflows/`,
  or `k8s/`

Invoke the `production-readiness-check` skill — it owns this domain and stays as a standalone
skill for pre-ship audits.

### Stage 3 — Merge and report

Deduplicate findings across CodeRabbit + Claude stages by `(file, line)` proximity.
When CodeRabbit and Claude flag the same spot, prefer CodeRabbit's finding (more specific)
unless Claude adds unique context.

Output a single report:

```markdown
## PR Review Summary

**Scope:** N files changed, M lines added, L lines removed.
**CodeRabbit:** C critical · H high · M medium · L low findings
**Claude gap-fill:** X additional findings across [which 2b-2f checks ran]

### Critical (X)
- [source] file.ts:42 — description
- ...

### High (X)
- ...

### Medium (X)
- ...

### Project-convention violations (X)
- Rule from CLAUDE.md:line — violated in file:line

### Recommended action
1. Fix critical first
2. Address high before merge
3. Consider medium/low
4. Re-run `/review-pr` after fixes
```

## Notes

- Do not re-run CodeRabbit findings through Claude — that's double-paying for the same check.
- Only run stages 2a-2f that match their triggers. Running all of them unconditionally wastes
  Claude tokens and re-introduces the bloat this skill was designed to kill.
- The `--pre-ship` flag runs 2a + 2f regardless of other triggers.
- The `--quick` flag runs only stage 1 (CodeRabbit) + stage 2a (project conventions) —
  appropriate for small PRs.

## Related

- `debate-team` — multi-model cross-provider review for plans/architecture (not PR review)
- `production-readiness-check` — standalone ops-level pre-ship audit
- `sentry:sentry-code-review` — narrow, only for Sentry bot PR comments
- `security-reviewer` agent — standalone security audit (Task tool target)

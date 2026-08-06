# Quality Document — per-module persistent score

A **Quality Document** is a persistent, per-module artifact that records the current quality grade for each significant module/surface in a repo. It is updated after every Phase 6 review and outlives any single workflow run.

Source: [Learn Harness Engineering, lecture 12](https://walkinglabs.github.io/learn-harness-engineering/en/) — Quality Documents as the long-lived signal that tells future agents (and humans) which surfaces are healthy and which carry rot.

---

## Why this exists

Phase 6 reviews are point-in-time. A clean review on PR #N tells you nothing about the rest of the codebase, and a CRITICAL finding on PR #N+5 in the same module is treated as fresh news rather than the third such finding this quarter.

A Quality Document converts that point-in-time signal into a durable, grep-able quality map. Future Phase 0 (Context) reads it to decide which modules need extra care; future Phase 6 reviews update it; humans use it to triage refactor work.

---

## Location

Default: `docs/quality/QUALITY.md` at the repo root.

Per-project overrides are fine — record the path in the repo's `CLAUDE.md` if it differs.

---

## Format

Markdown table, one row per module, sorted alphabetically:

```markdown
# Quality Document

Last full pass: 2026-05-28
Scoring rubric: see "Rubric" section below.

| Module | Grade | Last updated | Last reviewer | Notes |
|--------|-------|--------------|---------------|-------|
| `app/routes/auth/` | A | 2026-05-28 | claude-flow PR #142 | Clean. No HIGH+ findings in last 3 reviews. |
| `app/services/billing/` | B | 2026-05-20 | coderabbit PR #138 | One MEDIUM finding outstanding (idempotency on retry); tracked in issue #99. |
| `app/services/notifications/` | C | 2026-04-12 | claude-flow PR #121 | Multiple silent-failure patterns; refactor candidate. Not blocked from changes. |
| `scripts/legacy_migrate/` | D | 2026-03-01 | claude-flow PR #98 | Known-rotten. No new code should depend on this. Plan to delete after Q2. |
```

Required columns:

- **Module** — repo-relative path (directory or file). Granularity is repo-dependent; prefer directory-level for backends, file-level for hot single-file surfaces.
- **Grade** — one of A / B / C / D (see Rubric).
- **Last updated** — ISO date of the most recent grade change OR re-confirmation.
- **Last reviewer** — the source of the grade (PR number, reviewer ID, or human name).
- **Notes** — one line on why the grade is what it is. Include issue/PR refs for outstanding work.

---

## Rubric

| Grade | Meaning | Typical signals |
|-------|---------|-----------------|
| **A** | Healthy. Safe to extend. | No HIGH+ findings in last 3 reviews; tests green; type-checked; clear ownership. |
| **B** | Mostly healthy with known soft spots. | One or two MEDIUM findings tracked in issues; some tech debt but contained. |
| **C** | Degraded. Changes need extra care. | Multiple unresolved MEDIUM/HIGH findings; sparse tests; patterns drifted from current conventions. Reviewers should expand scope on PRs touching this module. |
| **D** | Rotten. Quarantine. | CRITICAL findings outstanding; no test coverage; planned for deletion or rewrite. Block new dependencies on this surface; surface a warning in Phase 0 if the diff touches it. |

Grades are **directional, not numerical** — a B → C drop is a signal to invest; a C → B climb is a sign refactor work paid off. Don't over-fit on the boundary cases.

---

## Update protocol

After every Phase 6 review (see `phases/phase-6-quality.md` § "Quality Document update"):

1. Identify the modules touched by `$diff` (use the Phase 6 file list).
2. For each touched module:
   - If the review surfaced new HIGH+ findings that remain unresolved → consider downgrading the grade.
   - If the review was clean AND the previous grade was C/D AND the diff materially improved the surface → consider upgrading.
   - Otherwise → update only `Last updated` and `Last reviewer` (re-confirmation, no grade change).
3. Append a one-line note when the grade changes, citing the PR or reviewer that drove the change.
4. Commit the QUALITY.md update as part of the Phase 6 finish-branch commit (not a separate commit — keeps the audit trail linked to the diff that produced it).

**Do not** change grades for modules NOT touched in this review. Grade changes require evidence from the current review; stale grades are better than guessed grades.

---

## Phase 0 integration

Phase 0 (Context) reads `docs/quality/QUALITY.md` when present and injects relevant rows into the workflow context. If the user's task touches a module graded C or D, Phase 0 surfaces a warning so subsequent phases can budget for extra care (more reviewers, smaller diff, mandatory tests).

---

## Initial population

Bootstrap the document by listing the top-level modules of the repo (one directory per row) at grade B with a note "Initial bootstrap — no review history yet." Subsequent Phase 6 reviews will adjust grades based on evidence. Do not assign A grades during bootstrap; A requires demonstrated review history.

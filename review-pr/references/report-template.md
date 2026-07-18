# Final report template (Stage 3)

Output a single report with this structure:

```markdown
## PR Review Summary

**Scope:** N files changed, M lines added, L lines removed.
**CodeRabbit:** C critical · H high · M medium · L low findings
**Standards axis:** X findings (A1 conventions · A2 over-engineering · A3 types · A4 silent-failures)
**Spec axis:** Y findings | spec source: [linked doc / PR description / inferred-from-tests]
**Agent dispatches run:** [security-reviewer / production-readiness-check / none]

---

### Standards Report (Axis A)

> Does this change follow our conventions and quality expectations?

#### A1 — Project conventions
- Rule from CLAUDE.md — violated in file:line

#### A2 — Over-engineering
- V2 · file.ts:42 — <what> · simpler: <alternative> · kill cost: <X hours>

#### A3 — Type design
- TypeName · Invariant Expression: 4/10 — <concern in one sentence>

#### A4 — Silent failures
- CRITICAL · file.ts:88 — empty catch hides <error-type>

---

### Spec Report (Axis B)

> Does this change implement the intended behavior?
> Spec source: [linked doc at path/url | PR description | inferred from tests — no spec doc found]

#### B1 — Intent coverage
- MISS · "users can reset password via email" — no diff change corresponds to this stated intent

#### B2 — Business-rule correctness
- WRONG · file.ts:120 — refund guard uses `>` not `>=`; allows refund equal to original charge

#### B3 — Edge cases
- UNHANDLED · empty array input at file.ts:55 — spec requires "return empty state, not error"

#### B4 — Test coverage of spec
- NO TEST · "password reset email" behavior has no test
- SNAPSHOT · auth.test.ts:33 — mocks return value and asserts same value; no invariant named

---

### Unified severity roll-up (CodeRabbit + both axes + agent dispatches)

#### Critical (X)
- [source] file.ts:42 — description

#### High (X)
- ...

#### Medium (X)
- ...

#### Project-convention violations (X)
- Rule from CLAUDE.md — violated in file:line

---

### Recommended action
1. Fix critical first — address any Spec axis B2 business-rule failures before Standards issues
2. Address high before merge
3. Consider medium/low
4. Re-run `/review-pr` after fixes
```

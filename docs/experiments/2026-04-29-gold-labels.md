# Gold-Skill Labels — Phase 5 Skill Selection A/B

**Status:** VERIFIED 2026-04-29 — labels checked against `gh pr view --json files` for each PR. See "Verification notes" below the table for two flagged rows.
**Plan:** [2026-04-29-skill-selection-vs-progressive-disclosure.md](../plans/2026-04-29-skill-selection-vs-progressive-disclosure.md).

## How to fill this in (15 min, step by step)

You're picking 12 historical Phase 5 dispatches and labeling, for each one,
**which skill SHOULD have been loaded** and **whether the base model could
have solved it without any skill at all**. This is the ground truth the A/B
runs will be scored against.

### Step 1 — Find candidate dispatches (5 min)

Run from the courierflow repo root:

```bash
# Find merged PRs from last 30 days that touched courierflow code
gh pr list --state merged --search "merged:>=$(date -v-30d +%Y-%m-%d)" \
  --limit 50 --json number,title,mergedAt,files \
  --jq '.[] | "\(.number)\t\(.title)\t\(.mergedAt[:10])"'
```

Pick 12 PRs that hit Phase 5 (i.e., feature work, not pure docs/config).
Try to roughly match the target distribution from the plan:

- **4× UI**: PRs touching `app/templates/`, `app/static/`, `*.html`, `*.css`, `*.js`
- **4× API**: PRs touching `app/routes/`, `app/services/`, `app/main.py`
- **2× data**: PRs touching `app/models/`, `migrations/versions/`
- **2× cross-cutting**: PRs touching ≥2 of the above areas

### Step 2 — For each dispatch, label two things (8 min)

For each row in the table below:

**Column 4 — Gold skill** (the skill that *should* have been loaded):
Look at the PR's diff. Pick the ONE skill whose SKILL.md content would have
been most useful to the implementer. Pick `none` if the change was simple
enough that no skill content would have helped (e.g. one-line copy edit, a
typo fix, or a dependency bump).

| If the PR primarily... | Gold skill |
|---|---|
| Edits Jinja templates, CSS, or Alpine.js | `courierflow-ui` |
| Adds/edits FastAPI routes or service-layer code | `courierflow-api` |
| Adds/edits SQLAlchemy models or Alembic migrations | `courierflow-data` |
| Touches Calendar / Twilio / OpenAI / DocuSeal integrations | `courierflow-integrations` |
| Touches auth, permissions, or secrets handling | `courierflow-security` |
| None of the above OR fully solvable from base knowledge | `none` |

If a PR genuinely needed two skills, pick the one whose absence would have
caused the bigger error. (Multi-skill labels are out of scope for this A/B —
we're testing forced *single* selection.)

**Column 5 — Baseline skill-free pass** (could the base model have done this
without any skill?):
Read the diff. Ask: "If a competent engineer with general Python/FastAPI
knowledge but no courierflow context wrote this, would it have landed
correctly on the first try?"

- `true` = yes, no project-specific knowledge needed (e.g. `int(x)` typo fix,
  adding a generic FastAPI dependency, standard library usage)
- `false` = no, you'd have to know a courierflow gotcha to get this right
  (e.g. `is_primary_contact` not `is_primary`, eager-loading discipline,
  HouseholdMember + Client sync invariant, Alpine click-outside trap)

### Step 3 — Sanity check (2 min)

After filling, verify:

- [ ] At least 4 rows have `none` in column 5 — if every PR "needed a skill,"
      our test set is biased toward easy wins for variant B.
- [ ] At least 2 rows have `gold_skill = none` — if every PR has a gold skill,
      we can't measure variant B's over-loading risk.
- [ ] No two rows have identical PR numbers.

---

## The table (fill columns 4–5)

| # | PR # | Title (or short description) | Gold skill | Baseline skill-free pass |
|---|------|------------------------------|------------|--------------------------|
| 1  | 511 | feat(copilot): typed-tools + generative UI for searchWorkflows | `courierflow-ui` | false |
| 2  | 510 | feat(copilot): complete getTenantDetails with CSS and tests | `courierflow-ui` | false |
| 3  | 470 | feat(copilot): chat-first workflow builder layout | `courierflow-ui` | false |
| 4  | 466 | fix(copilot): anchor StepEditor test selectors | `none` | true |
| 5  | 486 | fix(copilot): use settings.anthropic_model so agent matches | `none` | true |
| 6  | 464 | feat(onboarding): F1 Import Wizard v1e — Calendar scan | `courierflow-integrations` | false |
| 7  | 505 | fix(copilot): direct-route 5 critical Actions | `courierflow-api` | false |
| 8  | 530 | docs(copilot): Phase 2 canary browser-smoke results | `none` | true |
| 9  | 473 | hotfix(spa): revert /home to dashboard.html | `courierflow-api` | false |
| 10 | 506 | fix(models): portable JSON/UUID types in ai_response_cache | `courierflow-data` | false |
| 11 | 476 | fix(auth): seed landlord templates on registration | `courierflow-security` | false |
| 12 | 528 | chore(deps): bump google-auth from 2.49.1 to 2.49.2 | `none` | true |

**Distribution:**
- UI: 3 | API: 2 | data: 1 | integrations: 1 | security: 1 | none: 4
- `baseline_skill_free_pass = true`: 4 (rows 4, 5, 8, 12) ✓ ≥4 threshold
- `gold_skill = none`: 4 (rows 4, 5, 8, 12) ✓ ≥2 threshold
- All PR numbers distinct ✓

## Verification notes (2026-04-29)

Files inspected via `gh pr view <n> --json files` from `~/claude_code/courierflow`. Labels above held in 10/12 rows. Two flags to consider before kicking off the replay:

**Row 9 swap (2026-04-29) — replaced PR #545 with PR #473.**
Original PR #545 was 23 files spanning a migration, models, routes, and 9 service files — multi-domain, would have produced a noisy correct-skill metric. Swapped to **PR #473 `hotfix(spa): revert /home to dashboard.html`** (3 files: `app/routes/landing.py` + 2 test files). Tight single-domain scope; clean `courierflow-api` label. `baseline_skill_free_pass = false` because knowing whether to revert vs forward-fix requires project context (the SPA migration was deliberate; the revert came from a production blank-page incident).

**Rows 1, 2, 7, 9 — CopilotKit gap.** Four PRs labeled `courierflow-ui` or `courierflow-api` are actually CopilotKit-specific work (typed-tools, generative UI, runtime routing). Neither of those courierflow-* skills covers CopilotKit patterns. Variant B's forced-selection on these rows will pick a partially-correct skill that doesn't fully address the work. This is a real signal — it tells us either (a) the courierflow skill library is missing a `courierflow-copilot` skill, or (b) these PRs shouldn't be in the test set. **Decision: leave them in; the gap is itself a finding the experiment can surface.**

**Row 5 (PR #486) — `none`/`true` labeling holds.** Single-file change to `app/services/copilot_agent.py` swapping a hardcoded model for `settings.anthropic_model`. No project-specific gotcha needed; standard config-passing best practice.

**Row 11 (PR #476) — `courierflow-security` holds.** Touches `app/routes/auth.py` + `app/routes/workflows.py`; the gotcha is the post-pivot template-seeding logic, which is auth/registration territory. `courierflow-api` would also be defensible (it's a route change), but `courierflow-security` captures the registration-flow knowledge better.

**Pre-replay action:** decide on row 9. If you keep it, accept that its correct-skill metric is noisy. If you drop it, swap in a tighter-scoped PR (preferably one with `gold_skill = none` to maintain the ≥4 threshold).

---

## What happens next

Once filled, this file is the input to the replay harness:

```bash
# Read this table → run each PR's Phase 5 dispatch under variant A and B →
# log results via scripts/log_skill_selection.py.
# (Replay harness work is the next implementation step after this file is filled.)
```

After all 24 trials (12 × 2 variants), run the analyzer to compute the 5
metrics from the JSONL log and apply the decision tree in the plan.

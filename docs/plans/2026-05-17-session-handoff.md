# 2026-05-17 — session handoff

## Goal

Adopt the prioritized pulls surfaced by this session's three `useful-for` triages against Anthropic's official Claude Code skills/commands docs. Highest leverage first: audit skill listing budget overflow via `/doctor`, then add `paths` globs to the `courierflow-*` skill family, then update the progressive-disclosure MEMORY entry with the 5K/25K compaction numbers.

## Current state

**Shipped this session:** nothing — pure analysis. Three `useful-for` triages run against external content:

1. Third-party article on built-in skills/commands (`/simplify`, `/batch`, `/loop`, etc.) — yielded 2 candidate primitives (`!`command`` dynamic shell injection, `context: fork`), both flagged as needing harness verification before bulk adoption.
2. Official `commands` reference doc — yielded 3 candidate primitives (`/goal`, `.claude/loop.md` default, `CLAUDE_CODE_FORK_SUBAGENT`), all deferred pending harness validation.
3. Official `interactive-mode` + `skills` reference docs — **the high-value triage.** Surfaced 5 strong-fit pulls (confidence 4-5) plus 5 secondary pulls.

**Decisions made this session (do not relitigate):**

1. **`paths` glob frontmatter is a strict win for `courierflow-*` skills.** Each domain (UI, API, data, integrations, security) has unambiguous file boundaries in CourierFlow's repo. Auto-trigger via file paths complements existing description-based triggers — does not replace them. Direct addressment of the BM25 calibration finding (description hygiene moved recall@1 from 25% → 87.5%; `paths` should push the long tail toward 100% on file-anchored tasks).
2. **Skill listing budget overflow is almost certainly happening invisibly.** ~150 skills loaded × 1,536-char per-description cap × ~1% context budget default = descriptions for less-frequently-invoked skills get dropped. `/doctor` reports this; `skillListingBudgetFraction` or `SLASH_COMMAND_TOOL_CHAR_BUDGET` raises the cap.
3. **5K/25K compaction re-attachment budget reinforces the existing progressive-disclosure rule.** Router + always-resident contracts must fit within 5K tokens to survive `/compact`. Memory entry "Large SKILL.md files belong in progressive disclosure layout" should be extended with these specific numbers.
4. **Defer per-skill `effort`/`model` overrides and `skillOverrides` until paths + budget audit are validated.** Adding multiple new frontmatter conventions at once is too much surface to debug if behavior is wrong. Validate one mechanism per PR.

**In-flight:** nothing.

**Untouched:** all five secondary pulls (`when_to_use` split, `${CLAUDE_SKILL_DIR}`, `ultrathink` keyword in reasoning-heavy skills, `CLAUDE_CODE_TASK_LIST_ID`, `Skill()` permission rules) — revisit after primary three land.

## Exact next task

**Sequence the rollout. Each step blocks the next — do not bundle.**

### Step 1 — Audit skill listing budget (single-command, free, no PR)

Run `/doctor` in a session. Look for the line reporting skill listing budget overflow and which skills' descriptions are being dropped.

- **If no overflow reported:** skip to Step 2. Log "/doctor clean" in this handoff's execution log section and move on.
- **If overflow reported:** edit `.claude/settings.json` (or `~/.claude/settings.json` for personal scope — pick whichever scope the affected skills sit in). Add `"skillListingBudgetFraction": 0.02` (try 2% first; raise to 0.03 if still overflowing). Re-run `/doctor` to confirm. Ship as a single-commit PR titled `chore: raise skillListingBudgetFraction to relieve skill description overflow`.

Acceptance: `/doctor` reports no skill description truncation after the change.

### Step 2 — Add `paths` glob to one `courierflow-*` skill (pilot, then bulk)

Pilot on `~/.claude/skills/courierflow-ui/SKILL.md` first because `app/templates/**` and `app/static/**` are the most unambiguous file boundaries. Add to frontmatter:

```yaml
paths:
  - "app/templates/**"
  - "app/static/**"
  - "app/templates/**/builder.html"
```

Validate by opening Claude Code in the courierflow repo, editing a file under `app/templates/`, and asking a generic UI question without naming the skill. Confirm `courierflow-ui` auto-triggers from the path signal alone.

**If pilot succeeds**, bulk-add to the other four in one PR:

- `courierflow-api`: `["app/routes/**", "app/services/**", "app/schemas/**"]`
- `courierflow-data`: `["app/models/**", "alembic/versions/**"]`
- `courierflow-integrations`: `["app/services/sync_service.py", "app/services/twilio_*.py", "app/services/openai_*.py", "app/integrations/**"]`
- `courierflow-security`: `["app/auth/**", "app/middleware/**", "app/routes/auth_*.py"]`

**If pilot fails** (path glob doesn't fire, syntax wrong, or behavior unexpected), debug before expanding scope. Do not bulk-add until the pilot validates.

Acceptance per skill: editing a file matching the glob auto-triggers the skill without explicit invocation; editing a file outside the glob does not.

### Step 3 — Extend progressive-disclosure MEMORY entry with compaction budget numbers

Edit `~/.claude/projects/-Users-summerrae-claude_code-courierflow/memory/MEMORY.md` (or wherever the canonical "Large SKILL.md files belong in progressive disclosure layout" entry currently lives — search for that exact phrase). Append:

> Compaction re-attachment budget: Claude Code keeps the first 5,000 tokens of each invoked skill after `/compact`, with a 25,000-token shared budget across all re-attached skills. Older skills drop entirely. Design the router + always-resident contracts to fit within 5K so core orchestration survives compaction; rely on lazy-loaded phase/reference files for the remainder. Source: official skills doc § Skill content lifecycle (2026-05-17).

Same edit pattern as prior MEMORY extensions — single-line cross-reference, no restructuring.

Acceptance: MEMORY entry contains the 5K/25K numbers with the source citation.

## Template / reference PRs

- **PR #95** (most recent merge) — communication-safeguards + writing-voice CATEGORIES.md cross-link. Use as the template for the simple settings-only PR in Step 1.
- **PR #94** (communication-safeguards) — multi-file skill PR shape; use as template for Step 2's bulk `courierflow-*` PR.
- **PR #93** (resume-tailor hiring-risk + paired shapes) — example of bundled skill-frontmatter changes shipping atomically with the docs that describe them.

## Pre-flight commands

```bash
cd /Users/summerrae/claude_code/claude-skills    # canonical repo, NOT the worktree
git fetch origin --prune
gh pr list --state open
git log main..HEAD --oneline                      # confirm where we are
ls docs/plans/2026-05-17-session-handoff.md       # confirm this doc is in the tree
```

## Architectural invariants to preserve

- `Plugin Cache / Skills Management` in CLAUDE.md — symlink resolution, single source of truth, no editing cache files
- `Description hygiene is the dominant retrieval lever for BM25/keyword search` MEMORY entry — `paths` complements description hygiene, does NOT replace it. Keep existing description text untouched when adding `paths`.
- `Large SKILL.md files belong in progressive disclosure layout` MEMORY entry — being EXTENDED in Step 3, not replaced
- `worktree_symlink_edit_lands_in_main_repo.md` MEMORY entry — when editing `~/.claude/skills/courierflow-*/SKILL.md` from a worktree session, the edit lands in the main repo's working tree. Must `cd /Users/summerrae/claude_code/claude-skills &&` to commit.
- `worktree_read_edit_path_mismatch.md` MEMORY entry — for Step 2's edits, use matching path prefixes for Read and Edit calls

## Parked artifacts

None.

## Gates

- After each PR: `./scripts/quick_ci.sh` (if defined for claude-skills repo) or equivalent — at minimum `git status` clean + no unstaged changes
- After Step 2 pilot: manual test by opening a courierflow file and verifying auto-trigger
- After Step 3: grep MEMORY for the 5K/25K numbers to confirm the edit landed

## Ship instructions

Each step ships as a separate PR via `/ship`. Do NOT bundle. Rationale: each pull validates a different harness behavior; bundling makes it impossible to attribute failures.

- Step 1: single-line settings change → `/ship` with a 1-line commit message
- Step 2: pilot PR first (1 skill), then bulk PR (4 skills) after pilot validates → `/ship` for each
- Step 3: single MEMORY edit → `/ship`

The work is pattern-application, not new feature work. Use `/ship`, not `/claude-flow`.

## Mode directive

`Auto mode. Surface premise contradictions only.`

## Execution log

_Next session: append a dated entry here after each step lands. Format:_

```
### 2026-MM-DD — Step N
- PR: #NNN
- Result: <one line>
- Surprises: <one line, or "none">
```

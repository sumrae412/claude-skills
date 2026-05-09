# Session handoff — 2026-05-09

## Goal

Land PRs #83 + #84 in claude-skills, then port `scripts/build_doc_graph.py` to the CourierFlow repo with output committed to `docs/.knowledge/GRAPH_REPORT.md` (pre-launch decision; flip to gitignored post-launch).

## Current state

**Shipped this session (in claude-skills @ `~/claude_code/claude-skills`):**

- **PR #83** — `feat/doc-graph-spike` — open, MERGEABLE. 3 commits:
  - `0ea8a34` doc-graph spike (`scripts/build_doc_graph.py`, `.gitignore`)
  - `f11721c` consolidate 12 per-skill SOURCE.md → root NOTICE.md
  - `1b08ac3` dedupe `coding-best-practices/docs/` vs `references/` (drift-aware merge)
- **PR #84** — `feat/orphan-triage` — open, MERGEABLE. Stacked on #83. 2 commits:
  - `d523eea` smarter orphan classification + COMMANDS.md index
  - `4427827` orphan-triage cleanup (Tier 0 merge, reindex, restructure)
- **Mem note `ce4f5501-2f4f-4901-93c9-9e7f791572e5`** — version 3, reflects PR #84 results.

**Out-of-tree edits made this session (need separate sync, /cleanup may handle):**

- `~/.claude/CLAUDE.md` — 2 new rows in Domain Skills table (`learning-coach`, `life-planner`); debate-team description updated. Not yet committed in personal-config repo.
- `~/.claude/projects/-Users-summerrae-claude-code-claude-skills/memory/` — 4 new entries (`feedback_license_check_before_deleting_attribution.md`, `iterative_spike_refinement_pattern.md`, `drift_aware_dedup_pattern.md`, `mem_as_navigation_layer_for_regenerable_artifacts.md`) + MEMORY.md index updates. Auto-memory dir.

**In-flight (this PR):** This handoff doc itself, committed to `feat/orphan-triage` (PR #84) so it ships atomically with the state it describes.

**Untouched / queued:**

- CourierFlow port of doc-graph script (the main next task).
- 30-day re-test of `synthesis-brief` (calendar reminder, not code work).

## Exact next task

**Port `scripts/build_doc_graph.py` to the CourierFlow repo.**

Acceptance criteria:

1. `~/claude_code/courierflow/scripts/build_doc_graph.py` exists, copied verbatim from claude-skills.
2. New target dir: `~/claude_code/courierflow/docs/.knowledge/` — committed (NOT gitignored). User decision: pre-launch we want the graph reviewable in PRs; flip to gitignored post-launch.
3. Script runs cleanly against `~/claude_code/courierflow/docs/` (use `--root docs/` to scope to docs only — the full repo would be too noisy).
4. Output report committed at `docs/.knowledge/GRAPH_REPORT.md`.
5. `docs/.knowledge/graph.json` also committed (JSON sibling for downstream tools).
6. Update CourierFlow `.gitignore` if any prior `.knowledge/` rule conflicts. (Pre-launch decision means it should NOT be gitignored.)
7. Add a one-paragraph note to CourierFlow `CLAUDE.md` or `docs/README.md` (whichever is more discoverable) explaining: "We ship the doc-graph report under version control until launch, then flip to gitignored. To regenerate: `cd ~/claude_code/courierflow && python3 scripts/build_doc_graph.py --root docs/`."

## Template / reference PRs

- **Pattern PR:** [#83 (claude-skills)](https://github.com/sumrae412/claude-skills/pull/83) — script + ignore convention. Replicate the script verbatim; flip the ignore convention.
- **Follow-up pattern PR:** [#84 (claude-skills)](https://github.com/sumrae412/claude-skills/pull/84) — orphan-triage acts on the script's output. CourierFlow will likely want a similar follow-up after the first run reveals its own orphans.

## Pre-flight commands

```bash
# Confirm claude-skills PRs landed (or are landing)
cd ~/claude_code/claude-skills
git fetch origin --prune
env -u GH_TOKEN gh pr view 83 --json state,mergedAt
env -u GH_TOKEN gh pr view 84 --json state,mergedAt

# Switch to the CourierFlow repo
cd ~/claude_code/courierflow
git fetch origin --prune
env -u GH_TOKEN gh pr list --state open --json number,title,headRefName

# Read this handoff
cat ~/claude_code/claude-skills/docs/plans/2026-05-09-session-handoff.md

# Read the doc-graph script (~345 lines, single file)
cat ~/claude_code/claude-skills/scripts/build_doc_graph.py
```

## Architectural invariants to preserve

- **Pre-launch / post-launch flip rule** — committed `docs/.knowledge/` only valid pre-launch per Summer's 2026-05-08 decision. After launch flip, add `docs/.knowledge/` to CourierFlow `.gitignore` and remove the committed report. Don't burn this decision into a doc that lives forever; record as a follow-up TODO.
- **Token-economy default** — load only the script + the destination dir; do not re-read claude-skills source files unnecessarily.
- **CourierFlow CLAUDE.md "active-files" rule** — if porting requires touching files outside `/active-files`, add them first.
- **Worktree gotchas** (`bash_cwd_resets_after_chained_cd_in_worktree.md`, `git_checkout_b_from_worktree_affects_main_repo.md`) — prepend `cd` to every chained command if the next session's cwd is a worktree.

## Parked artifacts

None. All work is in committed/pushed branches; nothing left in stash, no patch files, no abandoned drafts.

## Gates

```bash
# CourierFlow
cd ~/claude_code/courierflow
./scripts/quick_ci.sh          # blocks merge per CLAUDE.md "Ship gate"
ruff format --check scripts/build_doc_graph.py
python3 scripts/build_doc_graph.py --root docs/   # must produce non-empty docs/.knowledge/GRAPH_REPORT.md
```

## Ship instructions

**Use `/ship` (not `/claude-flow`)** — this is pattern-replication of an already-shipped PR (#83), not feature work.

After the script runs and the report is generated:

1. Add `scripts/build_doc_graph.py`, `docs/.knowledge/GRAPH_REPORT.md`, `docs/.knowledge/graph.json`, and any CLAUDE.md/docs README discovery note.
2. One commit: `feat(docs): doc-graph for docs/decisions + docs/plans (pre-launch convention)`.
3. PR title: `feat(docs): port doc-graph spike to CourierFlow docs/`. Body should reference claude-skills PR #83 as the upstream pattern.

## Mode directive

Auto mode. Surface premise contradictions only.

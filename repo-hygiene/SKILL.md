---
name: "repo-hygiene"
description: "Conservative cross-repo worktree + branch pruning audit. Classifies every branch/worktree as safe-to-delete (proven dead via merged PR or zero unique commits) or keep-with-reason, then deletes what's proven dead. Use for 'clean up stale branches', 'prune dead worktrees', 'repo hygiene sweep', or any multi-repo branch-pruning ask."
---

# Repo Hygiene Agent

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad
exploration, repeated file reads, multi-file scans, or heavy reference
loading.

- Load only the phase needed for the current step; don't re-read this whole
  file per repo.
- Prefer bulk PR joins (one paginated call) over per-branch lookups; fall
  back to per-branch `head` filters only for branches a bulk page missed.
- Batch independent git/API calls across repos in parallel where the
  environment allows it.

**Announce at start:** "Running repo hygiene audit — read-only first, then
deleting only what's proven dead."

## Identity

You are a conservative repo janitor. Prime directive: **when in doubt,
keep.** A wrongly-kept branch costs nothing; a wrongly-deleted one costs a
session of recovery. Delete only what you have printed proof is dead.

MODE is caller-supplied per invocation: `auto-delete what is PROVEN dead;
list-don't-touch everything else` is the default. A caller may instead ask
for audit-only (report, no deletions) — respect that if stated.

## Hard invariants (no exceptions, no force flags)

1. **Never touch WIP.** WIP = uncommitted tracked changes; untracked files
   outside `.claude/`; unique commits with no MERGED PR; an OPEN pull
   request; a CLOSED-but-not-merged pull request (content never landed
   verbatim — keep).
2. **Never remove:** the worktree you are running in; any worktree whose
   branch is the repo's actual default branch (check — it is not always
   `main`; e.g. some repos use `master`); any session worktree that is
   clean with zero unique commits (the harness reaps those itself); any
   worktree outside this repo's own worktree directory.
3. **Never delete a branch currently checked out in ANY worktree.**
4. **Never delete a remote branch that is the BASE of an open PR** —
   deleting a base ref auto-closes the downstream PR. Cross-check every
   deletion candidate against every open PR's base ref before executing.
5. **Active-workstream exclusion:** if any worktree's checked-out branch
   changes between the first audit pass and execution, a parallel session
   is live there — exclude that worktree and all sibling branches sharing
   its name prefix from every delete list.
6. **Evidence before every deletion (no inference).** A branch is
   deletable only if (a) the PR history shows a MERGED PR for that head
   ref (check the `merged_at` field, not just `state: closed` — closed
   ≠ merged), or (b) `git log origin/<default>..origin/<branch>` is empty
   (fully contained in the default branch). **A force-pushed / rewritten
   default branch invalidates ancestry-based checks** — if the fetch shows
   `(forced update)` on the default branch, treat any non-zero `git log`
   diff as unreliable noise, not proof of live work, and fall back to
   MERGED-PR-only evidence. Never use cherry/ancestry alone; squash merges
   make `git cherry` lie.
7. **Stop-and-report** (don't proceed, list findings instead) if: the
   reflog shows a `reset --hard` or unrecognized commits from a parallel
   agent mid-run; API/auth fails outright; or fetch/prune errors.

## Procedure

**Phase 1 — Preflight (per repo).** `git fetch origin --prune`, `git
reflog -15` (parallel-agent check), `git worktree list --porcelain`,
`git branch -vv` (local branches — usually just the default branch + the
current session branch; local branches are rarely deletion candidates
since the checked-out one is always protected).

**Phase 2 — Remote branch inventory.** List all remote branches (`git
branch -r` after prune, or the platform's branch-list API). This is the
full candidate set before classification.

**Phase 3 — Bulk PR join.** Fetch PR history in bulk (paginated, newest
first) and cross-reference every remote branch by head ref. For branches
not found on the first page(s), keep paging until the PR history is fully
covered (page count is bounded — stop once a page returns fewer results
than the page size). For any branch still not found after full coverage,
it never had a PR — fall through to the git-log unique-commit check
(invariant 6b).

**Phase 4 — Classify every branch:**
- `DELETE` = MERGED PR (confirmed via `merged_at`, not just closed state),
  or zero unique commits vs default; not checked out anywhere.
- `KEEP` = open PR / closed-but-unmerged PR / no-PR-with-unique-commits /
  currently checked out / the repo's default branch / active workstream /
  ambiguous for any reason. Record the reason for every KEEP.

**Phase 5 — Safety gates.** Re-check invariant 4 (open-PR base-ref) and
invariant 5 (worktree-branch drift) immediately before executing deletion
— state can change between audit and execution.

**Phase 6 — Execute.** Worktree removal first (native tool if available,
else `git worktree remove`, never `--force`) → local branch delete (`git
branch -D`, only list-verified) → remote branch delete (`git push origin
--delete <branch>`, or the platform API equivalent) → `git worktree
prune`.

**Phase 7 — Blocked-deletion fallback (do this whenever Phase 6 cannot
complete).** Environments differ in git/API permission scope — a
sandboxed session's credentials may allow ordinary pushes but reject ref
deletion (`403` or equivalent), and no delete-ref tool may be exposed even
via a connected platform MCP server. This has been confirmed to be a
deliberate platform boundary, not a scope gap: the `403` on `git push
--delete` in Claude Code on the web sandboxes originates from the
sandbox's own outbound proxy (not GitHub), and no delete-ref tool exists
in the connected GitHub MCP server either — the same action blocked two
independent ways is intentional (background/scheduled sessions should not
be able to execute unattended destructive ref operations). Do not treat
the block as a reason to keep retrying with different tool shapes, and do
not go looking for higher-privilege credentials (tokens, keys) to route
around it directly from the session — even on explicit caller request,
that specific workaround is out of bounds. Instead:

1. **Prefer Actions-dispatch execution when available.** If the repo has
   `.github/workflows/delete-dead-branches.yml` (a `workflow_dispatch`
   job that deletes a caller-supplied branch list using the Action's own
   `GITHUB_TOKEN`, with its own live re-check of default-branch/open-PR
   safety — see that file for the reference implementation), dispatch it
   with the confirmed-dead branch list for that repo via the platform's
   workflow-trigger tool (GitHub MCP: `actions_run_trigger` method
   `run_workflow`, `workflow_id: delete-dead-branches.yml`, `ref:
   <default branch>`, `inputs: {branches: "<comma-separated list>"}`).
   This executes real deletion on the platform's own infrastructure,
   inside a permission boundary the sandbox proxy doesn't sit in front
   of — it is not a workaround, it's a different, intentionally-granted
   execution path. Report the dispatched run and, once it completes,
   its per-branch result summary (deleted / skipped-protected /
   skipped-open-pr / error).
2. **Fall back to printing commands only if that workflow doesn't exist
   in the repo.** Print copy-paste-ready deletion commands for every
   confirmed-dead branch, grouped by repo, in the final report. Use the
   platform's CLI/API delete-ref form (e.g. for GitHub: `gh api -X
   DELETE repos/<owner>/<repo>/git/refs/heads/<branch>`). A blocked run
   is only useful if its output is directly actionable somewhere with
   more permission.
3. State plainly in the report which repos/branches went which route
   (Actions-dispatched vs. printed-fallback) and why, so the caller can
   tell a permission gap from an actual audit finding.

**Phase 8 — Verify + report.** Re-run branch/worktree counts (before →
after). Report every deletion executed with its evidence (PR number or
"0 unique commits"), a KEPT table with one reason per row, and — per
Phase 7 — either the Actions-dispatch run results or the blocked-deletion
command list for anything that couldn't be executed directly. Never end
with deletions unreported.

## Tooling gotchas

- **`gh` CLI is not always available** (e.g. Claude Code on the web
  sandboxes route GitHub access through an MCP server instead). Check
  `which gh` once at the start; if absent, use the connected GitHub MCP
  tools (`list_pull_requests`, `list_branches`, etc.) for read operations.
  There is currently no MCP delete-ref tool — deletion still requires
  `git push --delete` (which may itself be scoped out — see Phase 7) or
  the caller running the printed fallback commands elsewhere.
- **Large PR-history dumps exceed tool output limits on active repos.**
  Prefer compact field extraction (number/state/head ref/merged_at/base
  ref only) over reading full PR bodies; page through in that shape
  rather than one giant call.
- **`gh pr view --json state` = MERGED is necessary but not sufficient**
  for "content on main" in stacked-PR setups — for anything stacked, also
  confirm the merge SHA is reachable from the default branch's
  first-parent history.
- Shell cwd can reset between calls in some harnesses — prefix `git -C
  $REPO` (or equivalent) rather than relying on a persistent `cd`.

## Acceptance checks (before executing Phase 6)

- Control: a clean branch with a MERGED PR → deleted.
- Vague state: branch with no PR and non-zero unique commits → KEPT,
  reason printed.
- Mid-run mutation: a worktree's branch flips between audits → that
  workstream fully excluded, noted in report.
- Rewritten default branch: `(forced update)` seen on fetch → unique-commit
  counts for old branches treated as unreliable, MERGED-PR-only evidence
  used instead.
- Boundary: anything requiring `--force`, or any ambiguity → KEPT +
  listed.
- Permission boundary: deletion blocked by environment scope →
  Actions-dispatch attempted first if the workflow exists in-repo,
  otherwise Phase 7 fallback commands printed — never silently dropped.

End every run with: counts table, KEPT-with-reasons table, and either
"nothing pending", the Actions-dispatch results, or the Phase 7
blocked-deletion command list. Never end with deletions unreported.

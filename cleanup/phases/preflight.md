## Pre-flight: detect parallel-agent activity

BEFORE touching any worktree or branch, run:

```bash
# Re-read HEAD and reflog in case another agent moved things mid-session.
git -C <main-repo-path> branch --show-current
git -C <main-repo-path> reflog -20
git -C <main-repo-path> fetch origin --prune
```

If the reflog shows a recent `reset --hard origin/main`, a commit you don't recognize, or a branch switch you didn't initiate — a parallel agent is active. STOP. Confirm with the user before removing any worktrees.

See: `memory/gotcha_parallel_agent_merged_pr_mid_session.md`

## Worktree audit: cross-check squash-merged work

`git cherry origin/main <branch>` returns `+` for every commit of a squash-merged branch — DO NOT use it alone to declare work unshipped.

A worktree is SAFE to remove if ANY of:
1. `gh pr list --state all --head <branch>` reports a MERGED PR.
2. `git cherry origin/main <branch>` reports `-` for all commits.
3. A distinctive subject line from the branch appears in `git log origin/main`.
4. Known-dead-end experiment.

See: `memory/gotcha_git_cherry_squash_merge_false_positive.md`, `memory/gotcha_gh_pr_merge_delete_branch_worktree.md`

### Bulk-prune triple-check (validated 2026-05-06)

When auditing N stale worktrees at once, capture three signals per worktree and decide from the joint result, not any single one:

- `git -C <wt> status --porcelain | wc -l` — dirty file count (untracked `.claude/` session-state ≠ tracked changes; inspect before treating as dirty)
- `git -C <wt> log --oneline origin/main..HEAD | wc -l` — commits unique to the worktree branch
- `git ls-remote --heads origin <branch> | wc -l` — remote branch still exists

Decision rule: `dirty=0 AND unique=0 AND remote=0` → safe to prune. If `dirty>0` but the dirty files are all untracked session-state under `.claude/`, also safe under `--force`.

### PATH loss in bash for-loops with `$(...)` substitutions

Iterating over worktrees in `bash` and calling `git`/`wc`/`tr`/`head` inside `$(...)` can return `command not found` even after explicit `export PATH=...` at the top — subshells in command substitutions don't inherit the export reliably in some sandboxed contexts. Workaround: run the audit as a single `/usr/bin/python3 <<'PY'` block using absolute `/usr/bin/git`. Same root cause as the `gh api` bash-loop gotcha in CLAUDE.md, but extends to plain coreutils.


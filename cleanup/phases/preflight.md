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


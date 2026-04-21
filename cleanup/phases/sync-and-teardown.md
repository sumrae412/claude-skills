## Step 5: Session Learnings

**After Options 1 or 2 only** (work was shipped or PR'd):

Invoke `/session-learnings` in the background. Every shipped branch should capture what was learned — patterns, gotchas, corrections discovered during development.

**Wait for session-learnings to resolve** before proceeding to Step 6. Session-learnings may propose edits to skills, CLAUDE.md, or config files — those changes need to land in their repos (Step 6) before the worktree is torn down (Step 7).

## Step 6: Sync Config and Skills Repos

**After session-learnings resolves (Options 1 or 2), or after /ship's review agent completes.**

Session-learnings and review agents often update files in `~/.claude/skills/` and per-project memory dirs. These are separate git repos that need their own commit+push cycle — changes there are invisible to the project repo.

**Topology note:** `~/.claude/skills/` IS a git repo. `~/.claude/` itself is NOT a git repo (it's the installation root; settings.json/hooks/CLAUDE.md live here but are not under version control at this level). Per-project memory dirs under `~/.claude/projects/<slug>/memory/` may or may not be git repos — check each.

Guard every sync with a `.git` existence check so the loop silently no-ops on non-repos instead of silently swallowing `git status` failures:

```bash
# 1. Claude skills repo (IS a git repo)
cd ~/.claude/skills
if [ -d .git ] && [ -n "$(git status --porcelain 2>/dev/null)" ]; then
  git add -A
  git commit -m "update skills from session-learnings"
  git push
fi

# 2. Project memory repo (check per-project slug; may or may not be a git repo)
MEMORY_DIR=~/.claude/projects/<slug>/memory
if [ -d "$MEMORY_DIR/.git" ] && [ -n "$(cd "$MEMORY_DIR" && git status --porcelain 2>/dev/null)" ]; then
  cd "$MEMORY_DIR"
  git add -A
  git commit -m "update memory from session-learnings"
  git push || true   # memory repos often lack a remote
fi

# 3. ~/.claude/ itself is NOT a git repo.
# If settings.json / hooks / CLAUDE.md changed and need to be tracked,
# promote the change into ~/repos/claude-config and re-run install.sh.
# Do NOT attempt `cd ~/.claude && git ...` — it will silently no-op.
```

**Why this matters:** Without this step, skill/config improvements discovered during a session evaporate when the worktree is removed, or worse, sit uncommitted and get lost when you switch machines.

**If no changes detected:** Skip silently — don't report "nothing to sync" unless the user asks.

## Step 7: Worktree Cleanup

**Only if currently in a worktree.** If on a regular branch, skip this step entirely.

**When all prior steps are complete and nothing remains to be done, ask the user:**

```
All cleanup is finished. Would you like me to delete the branch and worktree?
```

Wait for the user's answer before proceeding. If they say yes, use `ExitWorktree` with the appropriate action. If they say no, leave everything in place.

Use the `ExitWorktree` tool — it handles directory switching and cleanup correctly:

| Option chosen | ExitWorktree action |
|--------------|---------------------|
| 1 (Merged) | `action: "remove"` |
| 2 (PR created) | `action: "remove"` |
| 3 (Keep) | Do not call ExitWorktree |
| 4 (Discard) | `action: "remove", discard_changes: true` |

The `ExitWorktree` tool will:
- Switch the session back to the original working directory
- Remove the worktree directory and branch (for `"remove"`)
- Refuse to remove if there are uncommitted changes (unless `discard_changes: true`)

If `ExitWorktree` reports uncommitted changes and you're on Option 1 or 2 (work already pushed), set `discard_changes: true` since the work is safely on the remote.


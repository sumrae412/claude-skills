## Step 4.4: PR Merge Verification — every worktree, always

<HARD-GATE>NEVER remove a worktree while its branch has an open PR. This applies to the current worktree AND every sibling worktree you're planning to clean up in the same pass.</HARD-GATE>

Whenever you're about to remove one or more worktrees (current or sibling, audited in bulk), run this check for EACH one:

```bash
for wt in <each worktree path being removed>; do
  br=$(git -C "$wt" branch --show-current)
  state=$(gh pr list --state open --head "$br" --json number,state --jq '.[0].state' 2>/dev/null)
  echo "$wt (branch: $br) — open PR: ${state:-none}"
done
```

- **All `none`** → proceed with teardown.
- **Any OPEN** → STOP. Do not remove that worktree. Merge the PR first (or ask the user what to do with it). A worktree removed with an open PR orphans the local branch state needed to address review comments, and the user has no signal that the PR still needs attention.

This gate applies equally whether you reached cleanup via Option 1/2 on the current branch OR via a bulk sibling-worktree audit. Sibling worktrees are not exempt just because they look stale.

**Why the rule is stated this bluntly:** "merge all PRs before removing a worktree" is a permanent user rule (2026-04-18). Not a suggestion, not a soft preference — a hard gate.

## Step 4.5: PR Merge Verification — current branch deep check (Options 1 & 2)

Step 4.4 gates every worktree removal. This step adds the extra diagnostics needed when the current-branch PR state is `OPEN` or `CONFLICTING` after Option 1/2:

After executing Option 1 or 2, check if the current branch has an open PR:

```bash
# Check for open PR on this branch
BRANCH=$(git branch --show-current)
PR_STATE=$(gh pr view "$BRANCH" --json state --jq '.state' 2>/dev/null || echo "NONE")
```

- **MERGED** → safe to proceed with build verification and teardown.
- **OPEN** (Option 1 — was supposed to merge) → Something went wrong. Attempt merge or warn user.
- **OPEN** (Option 2 — PR was just created) → **Warn explicitly:**
  "PR #N is open but unmerged. If this session ends, the work may be orphaned. The session-start hook will flag it, but consider merging now if ready."
  Wait for user acknowledgment before proceeding to worktree teardown.
- **NONE** → No PR exists (e.g., direct merge). Proceed normally.
- **CONFLICTING** (mergeable check returns this immediately on push) → main has moved under the worktree. Do NOT exit-remove. Salvage flow:
  1. `git branch backup/feat-X-pre-rebase HEAD` — backup before any destructive op
  2. Inspect what main changed: `git diff --name-only $(git merge-base HEAD origin/main)..origin/main`
  3. If main DELETED files this branch still has (typical for repo-split refactors): `git reset --hard origin/main` then selective `git checkout backup -- <files>` for the files that still belong here
  4. Adjust cross-repo path references (e.g., persona files now in another repo via `~/.claude/skills` symlink)
  5. Recreate logical commits, `git push --force-with-lease`
  6. Open companion PR in the other repo for files that moved out

  See MEMORY `cross_repo_split_brain_salvage.md`. The skill's normal in-place conflict resolution does not apply when the conflict is structural.

**Why this exists:** PR #286 was created via Option 2, the worktree was torn down, and the session ended. The PR sat unmerged for days because no one checked. This gate ensures cleanup never silently walks away from unmerged work.

## Step 4.6: Build Verification (Options 1 & 2 only)

After pushing code, verify the build succeeds before proceeding to cleanup:

1. **CI pipeline:** If the project has CI (GitHub Actions), check it:
   ```bash
   # Check latest workflow run on the branch
   gh run list --branch "<branch>" --limit 1 --json status,conclusion
   # If status is "in_progress", wait and re-check (up to 2 minutes)
   ```

2. **Railway deploy** (if applicable):
   ```bash
   # Use Railway MCP: list-deployments tool
   # Check latest deployment status for FAILED vs SUCCESS
   ```

3. **Gate logic:**
   - **Build passes** → proceed to Step 5
   - **Build fails** → **STOP.** Report the failure with logs/error details. Do NOT proceed to session-learnings or worktree teardown. The user needs the worktree to fix the issue. Offer to help diagnose.
   - **Build pending (>2 min)** → Ask user: wait longer, proceed anyway, or keep worktree until build confirms.

**Why this matters:** Tearing down the worktree before confirming a successful build means you lose the local environment needed to iterate on fixes. A failed deploy with no worktree forces a full context rebuild.

---


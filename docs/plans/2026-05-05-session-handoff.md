# 2026-05-05 — session handoff

## Goal

Validate the new **Step 7.5 (macOS Keychain retrieval)** in `inbox-triage/SKILL.md` end-to-end on a real login-gated task during the next inbox triage run, and populate additional `claude-automation:*` Keychain entries as portals come up.

## Current state

**Shipped this session (in this PR):**

- `inbox-triage/SKILL.md` — added Step 7.5 (Keychain retrieval flow), extended Step 7's third branch to route login-gated tasks through 7.5, added `security find-generic-password` to the Tools section. Net `+82 / -2`.

**Decisions made this session (do not relitigate):**

1. **1Password MCP is installed but unused.** `op-mcp` connects, tools load, but the only registered account (`team_deeplearningaiteam`) is company-managed — vault/service-account creation is locked. Personal 1Password subscription was not on the table.
2. **macOS Keychain `security` CLI is the chosen secrets backend.** Service-name prefix `claude-automation:<service>` is the authorized namespace; everything else in Keychain is out of scope.
3. **No service account, no MCP-driven retrieval.** Step 7.5 calls `security` via Bash. The 1Password MCP server can stay registered — it's just not referenced by any skill.

**In-flight:**

- One Keychain entry created and verified: `claude-automation:letterstream` (account `summer@deeplearning.ai`, pre-authorized for Claude Code app via `-T "$CLAUDE_PATH"`).
- No other portal entries exist yet (Townsgate, LendingClub, etc.) — populate as needed when tasks surface.

**Untouched:**

- 1Password MCP server registration in `~/.claude.json` — left in place; harmless if unused.
- `inbox-triage` still routes via Mem (PR #79 rename); Step 7.5 piggybacks on that flow without changing routing.

## Exact next task

**During the next inbox triage run, validate Step 7.5 on a real LetterStream task.**

- Trigger: any Mem `## Pending` checkbox referencing a LetterStream login.
- Acceptance: Step 7.5 retrieves the credential via `security find-generic-password`, the browser fill succeeds, the task moves to `## Done` with a `Keychain read: claude-automation:letterstream` line under the daily triage log entry. Password value never appears in chat output, tool descriptions, or Mem notes.
- If macOS shows a "Claude Code wants to use…" popup with no "Always Allow" button, the `-T` pre-authorization didn't take — re-run the `add-generic-password` command with the explicit Claude Code app path.

For each additional portal that comes up, run (in your terminal):

```bash
CLAUDE_PATH=$(mdfind "kMDItemKind == 'Application'" | grep -i "Claude.app" | head -1)
security add-generic-password -s "claude-automation:<service>" -a "<username>" -T "$CLAUDE_PATH" -T "" -U -w
```

`<service>` = lowercased portal name with no spaces (matches Step 7.5's resolution rule).

## Template / reference PRs

- **PR #79** — prior `inbox-triage` change (rename + Mem routing). Same skill, same review shape.
- **PR #78** — recent skill change with handoff doc shipped atomically. Use as template if anything about doc-co-shipping needs to be replicated.

## Pre-flight commands

```bash
cd /Users/summerrae/claude_code/claude-skills    # canonical repo, not the worktree
git fetch origin --prune
gh pr list --state open
git log main..HEAD --oneline                      # confirm where we are
```

## Architectural invariants to preserve

- `feedback_verify_saved_patch_base_before_apply.md` — no parked patches in this session, so n/a, but cited for consistency.
- `worktree_symlink_edit_lands_in_main_repo.md` — when committing skill edits from a worktree, `cd` to the canonical repo first; `~/.claude/skills/...` paths are symlinks.
- `two_clones_same_repo.md` and `shadow_path_drift_within_session.md` — there are two clones; canonical is `/Users/summerrae/claude_code/claude-skills/`.
- CLAUDE.md "Single source of truth (2026-04-16)" — skills live in exactly one place; edits via worktree resolve through symlinks.

## Parked artifacts

None. All work is committed on this branch as part of the shipping PR.

## Gates

- `git diff --stat` — confirm only `inbox-triage/SKILL.md` and this handoff doc are modified.
- `grep -n "1[Pp]assword\|1password" inbox-triage/SKILL.md` — must return nothing (verified during session: no stale refs).
- No quick_ci.sh in this repo (skills repo, not CourierFlow); CodeRabbit handles review.

## Ship instructions

Ship via `/ship`. This is a single-file skill edit + atomic handoff doc — pattern matches PR #79. No `/claude-flow` needed; no feature work.

## Mode directive

Auto mode. Surface premise contradictions only.

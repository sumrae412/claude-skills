---
name: repo-hygiene
description: Conservative repo janitor — prunes dead branches (MERGED PR or 0 unique commits) and stale worktrees across all session-scoped repos. Skips repos whose remote ref set is unchanged since the last run. State persists in agent-vault/agent/repo-hygiene-state.json.
user-invocable: true
---

# /repo-hygiene

Prune dead branches and worktrees across repos. Conservative by design: delete only what has printed proof of being dead; list-and-keep everything else.

MODE: auto-delete what is PROVEN dead; list-don't-touch everything else.

---

## Identity

You are a conservative repo janitor. Prime directive: **when in doubt, keep.** A wrongly-kept branch costs nothing; a wrongly-deleted one costs a session of recovery. Delete only what you have printed proof is dead.

---

## Hard invariants (no exceptions, no force flags)

1. NEVER touch WIP. WIP = any of: uncommitted tracked changes; untracked files outside `.claude/`; unique commits with no MERGED PR; an OPEN pull request; a CLOSED-but-not-merged pull request (content never landed verbatim — keep).
2. NEVER remove: the worktree you are running in; any worktree whose branch is `main`; any `.claude/worktrees/*` session worktree that is clean with zero unique commits (the harness reaps those itself); any worktree outside the repo's own `.claude/worktrees/` dir.
3. NEVER delete a branch currently checked out in ANY worktree.
4. NEVER delete a remote branch that is the BASE of an open PR — deleting a base ref auto-closes the downstream PR. Check `gh pr list --state open --json number,headRefName,baseRefName` against your delete list first.
5. ACTIVE-WORKSTREAM EXCLUSION: if any worktree's checked-out branch CHANGES between your first audit and execution, a parallel session is live there — exclude that worktree AND all sibling branches sharing its name prefix from every delete list.
6. Evidence before every deletion (no inference): a branch is deletable only if (a) `gh pr list --state all --head <branch>` shows a MERGED PR, or (b) `git log origin/main..<branch>` is empty (fully contained in main). Squash merges make `git cherry` lie (`+` for merged commits) — the MERGED PR state is the authority, never cherry/ancestry alone.
7. STOP-AND-REPORT (do not proceed, list findings instead) if: the reflog shows a `reset --hard` or unrecognized commits from a parallel agent mid-run; `gh` auth fails; or fetch/prune errors.

---

## Tooling gotchas (these have all bitten before)

- `env -u GH_TOKEN` on every `gh` call (env token silently overrides keyring).
- Shell cwd resets between Bash calls — prefix `git -C $REPO` everywhere.
- `gh pr view --json state` = MERGED is necessary but not sufficient for stacked PRs; also confirm merge SHA on `git log --first-parent origin/main`.
- `zsh`: `ls *.x *.y` aborts entirely if either glob matches nothing — separate per-glob or use `nullglob`.

---

## Procedure

### Phase 0 — Load state and filter repos (orchestrator-level, before any parallel dispatch)

Read stored state from agent-vault:

```bash
STATE_FILE="$HOME/claude_code/agent-vault/agent/repo-hygiene-state.json"
python3 -c "
import json, os
f = os.path.expanduser('$STATE_FILE')
print(json.dumps(json.load(open(f)) if os.path.exists(f) else {}))
"
```

For each repo in the session scope, compute the current remote refs hash **before** fetching (read-only, fast):

```bash
CURRENT_HASH=$(git -C $REPO ls-remote --heads origin | sort | sha256sum | awk '{print $1}')
```

**SKIP the repo** if ALL of the following are true:
- The stored `remote_refs_hash` for `$OWNER/$REPO` matches `$CURRENT_HASH`
- The stored `last_run_iso` is within 14 days (i.e. `(now - last_run) < 14d`)

Log skipped repos as: `SKIP <owner>/<repo> — refs unchanged since <last_run_iso>`

**NEEDS_HYGIENE** when any of:
- No stored state for this repo (first run)
- Hash differs (new branches appeared or branches were deleted since last run)
- `last_run_iso` is older than 14 days (safety re-run floor, catches PRs merged without branch deletion)

Only dispatch per-repo hygiene agents (Phases 1–7) for NEEDS_HYGIENE repos. If all repos are SKIP, report the full skip list and exit.

---

### Phase 1 — Preflight (per NEEDS_HYGIENE repo, run in parallel)

```bash
git -C $REPO fetch origin --prune
git -C $REPO reflog -15            # parallel-agent check (invariant 7)
git -C $REPO worktree list --porcelain
```

### Phase 2 — Worktree triple-audit

Per worktree, capture: dirty count (split real vs `.claude/`-only), `git log --oneline origin/main..HEAD` count, branch name. Use a single Python block — zsh loops lose PATH in `$()` substitutions.

### Phase 3 — Bulk PR join (ONE call per repo, not per-branch)

```bash
env -u GH_TOKEN gh pr list --repo $OWNER/$REPO --state all --limit 1000 \
  --json headRefName,state,number > /tmp/${REPO}_prs.json
```

Join locally. Rank per head: OPEN > MERGED > CLOSED (an open PR always protects).

### Phase 4 — Classify every local branch, remote branch, and worktree

- **DELETE** = MERGED PR, or 0 unique commits vs main; not checked out anywhere.
- **KEEP** = open PR / closed PR / no-PR-with-unique-commits / worktree / main / active workstream / external worktree. Record the reason.

### Phase 5 — Safety gates

Open-PR base-ref check (invariant 4). Re-run `git worktree list` and diff against Phase 2 (invariant 5).

### Phase 6 — Execute

`git worktree remove` (never `--force`) → `git branch -D` (only list-verified) → `git push origin --delete` in `xargs` batches of 40. `git worktree prune` at end.

### Phase 7 — Verify + report (per repo)

Re-run `git worktree list` / `git branch | wc -l` / `git ls-remote --heads origin | wc -l`. Report: before→after counts, every deletion with its PR number, and a KEPT table with one reason per row.

---

### Phase 8 — Persist state (orchestrator-level, after all per-repo agents complete)

For every repo that ran (NEEDS_HYGIENE), record the new post-run remote refs hash and timestamp:

```bash
STATE_FILE="$HOME/claude_code/agent-vault/agent/repo-hygiene-state.json"

python3 - <<'EOF'
import json, os, subprocess, hashlib, datetime

state_file = os.path.expanduser("~/claude_code/agent-vault/agent/repo-hygiene-state.json")
state = json.load(open(state_file)) if os.path.exists(state_file) else {}

# repos_processed is the list of (owner/repo, local_path) that actually ran
repos_processed = []  # filled in by the orchestrator from Phase 0 NEEDS_HYGIENE list

for repo_key, repo_path in repos_processed:
    try:
        raw = subprocess.check_output(
            ["git", "-C", repo_path, "ls-remote", "--heads", "origin"],
            text=True
        )
        h = hashlib.sha256("".join(sorted(raw.splitlines())).encode()).hexdigest()
        state[repo_key] = {
            "last_run_iso": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "remote_refs_hash": h
        }
        print(f"Updated: {repo_key} -> {h[:12]}...")
    except subprocess.CalledProcessError as e:
        print(f"WARN: could not hash {repo_key}: {e}")

json.dump(state, open(state_file, "w"), indent=2)
EOF

# Commit + push to agent-vault
git -C "$HOME/claude_code/agent-vault" add agent/repo-hygiene-state.json
git -C "$HOME/claude_code/agent-vault" diff --cached --stat
git -C "$HOME/claude_code/agent-vault" commit -m "repo-hygiene: update run state $(date -u +%Y-%m-%d)"
git -C "$HOME/claude_code/agent-vault" push origin main
```

**If agent-vault push fails:** log the error, print the state JSON to stdout so the orchestrator can surface it, and continue. A failed state write means the next run re-processes all repos (safe, just redundant work).

---

## Acceptance checks (run mentally before Phase 6)

- **Control:** clean worktree on a branch with a MERGED PR → removed + deleted.
- **Vague state:** branch with no PR and unique commits → KEPT, reason printed.
- **Mid-run mutation:** a worktree's branch flips between audits → that workstream fully excluded, noted in report.
- **Boundary:** anything requiring `--force`, or any ambiguity → KEPT + listed.

---

## End-of-run report shape

Every run ends with ALL of:
1. **Counts table** — before/after local branches, remote branches, worktrees, per repo.
2. **SKIP table** — repos skipped and the stored hash + `last_run_iso` that matched.
3. **KEPT table** — every surviving branch with its keep reason.
4. **Deleted** — every deletion with its evidence (PR number or "0 unique commits").
5. **Human-decision items** — anything that required `--force`, had ambiguous state, or hit a STOP condition.

"Nothing pending" is a valid final line only when the human-decision list is empty.

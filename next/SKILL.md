---
name: next
description: Hand off to the next session — write a self-contained continuation prompt/handoff doc, then ship the current work (commit → PR → review → merge) and run cleanup. Use when the user says "/next", "hand this off", "wrap up and write a continuation prompt", or wants to end one session and prime the next.
---

# /next — hand off, then ship and clean up

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad exploration, repeated file reads, multi-file scans, or heavy reference loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant patterns inline instead of loading extra material.


**Announce at start:** "Using /next to write a handoff doc, then ship and clean up."

Execute in this order. Do NOT interleave. Each step blocks the next.

## Step 1 — Write a continuation prompt

Before anything destructive, capture the handoff so a fresh session can resume cleanly. Write (or append to) a doc under `docs/plans/` — check first with `ls docs/plans/*handoff*.md`. If an existing session-handoff doc covers this work stream, append a new dated execution-log entry. Otherwise create `docs/plans/<YYYY-MM-DD>-session-handoff.md`.

The continuation prompt must be **self-contained** — the next session has zero memory of this conversation. Include:

1. **Goal** — one sentence. What is the next agent being asked to do?
2. **Current state** — what has already shipped this session (branches merged, PR numbers, commit SHAs), what is in-flight (open PRs, unmerged branches, pending reviews), what is untouched.
3. **Exact next task** — the single most-valuable thing to do next. Name the file paths, the operation, the acceptance criteria. If there is a choice between tasks, state the decision and the reasoning so the next agent does not relitigate it.
4. **Template / reference PRs** — link the 1–3 merged PRs that establish the pattern to replicate, if any. Cite by number, not prose.
5. **Pre-flight commands** — the literal commands the next agent should run before touching code: `cd <main-repo>`, `git fetch origin --prune`, `gh pr list --state open`, check for open PRs on recently-merged base branches, read the handoff doc.
5a. **Re-verify on resume** — three premises that silently drift between sessions and have caused shipped-on-wrong-branch / waited-on-nonexistent-review misfires. Tell the next agent to verify each, FIRST, before deciding next-action:
   - **Canonical repo path.** Record the absolute path; do not assume `~/repos/<name>` or similar — the resumer's layout may differ. Validate with `git -C <path> rev-parse --show-toplevel`.
   - **Current branch + worktree.** `git branch --show-current` plus `git worktree list`. A handoff doc that says "current branch: X" may refer to a sibling worktree's branch, not the resumer's cwd.
   - **CR / CI wiring state for THIS repo.** `gh pr view <recent-merged-PR> --json reviews,statusCheckRollup` against 1–2 recently merged PRs. Both empty across both samples → no automated review will ever land; do NOT block on "address review feedback" before merge. See `shipping-workflow`'s no-review-wired-up fast path. Validated 2026-05-27 on [claude-skills PR #118](https://github.com/sumrae412/claude-skills/pull/118) — handoff doc had wrong path (`~/repos/claude-skills`), wrong branch assumption, and gated on nonexistent CodeRabbit feedback.
   - **Worktree match.** If the handoff names a specific worktree (e.g. `silly-swanson-899c1e`), run `git worktree list` and verify the resumer's cwd matches. When the resumer opens in a different worktree, the named worktree may still exist with staged work — `cd` to the correct path before acting; do not recreate the work in the wrong tree. Validated 2026-05-28 on [courierflow_beta PR #108](https://github.com/sumrae412/courierflow_beta/pull/108): handoff named worktree `silly-swanson-899c1e`, resumer opened in `magical-mayer-4d97ac`, both worktrees existed with the silly-swanson tree holding the prior session's staged docs + open PR. `git worktree list` + `cd` prefix preserved the work; without this check the resumer would have re-authored from a clean tree and shipped a duplicate PR.
6. **Architectural invariants to preserve** — cite by memory-file slug (e.g. `pattern_copilotkit_page_context_readables.md`) or CLAUDE.md section. Do not re-explain the invariants; name them.
6a. **Parked artifacts (if any)** — if this session is leaving behind a saved patch, stash, or branch the next agent will resume from, name the artifact path AND the base SHA the artifact was generated against. Example: `Patch: abandoned/2026-05-04-foo.patch (generated from origin/main @ 5452caae)`. Also record net `+N / -M` line counts at save-time. The next agent will diff the recorded base SHA against current `origin/main` before applying — without it, they have no way to detect base-staleness silently. If the artifact is a stash, capture the `git stash list` entry too. See `feedback_verify_saved_patch_base_before_apply.md` and `pattern_parked_patch_double_anchor.md`.
7. **Gates** — `./scripts/quick_ci.sh` (or project equivalent), `ruff format --check` on touched files, any test-subset command that isolates the relevant suite.
8. **Ship instructions** — literal: "Ship via `/ship`. Update [specific doc row] with the PR number before merging." If the work is pattern-replication of an already-shipped PR, say so — the next agent should use `/ship`, not `/claude-flow`.
9. **Mode directive** — `Auto mode. Surface premise contradictions only.`
9a. **Unapproved drafts — embed verbatim, don't summarize.** If `/next` fires while drafts (decision records, spec amendments, PR bodies) are sitting in the conversation awaiting user sign-off, embed them VERBATIM in the handoff doc — not as a summary, not as a "see chat log" pointer. The next session has zero chat memory; a summary forces re-derivation and reopens decisions the current session had already worked through. Two reads of the user's `/next`-before-sign-off are valid (resume in cold context vs abandon the proposal); name both in the handoff and pick a default. Validated 2026-05-31 on courierflow_beta slice 7 binary-collapse handoff (PR #190): 6 spec amendment drafts embedded verbatim so the resuming session could ask for sign-off, then ship — no re-derivation.

Write the handoff doc, then read it back and ask: "If I had no memory of this session, could I execute the next task from this doc alone?" If not, fill the gap before proceeding.

## Step 2 — Ship the current work

Invoke the `shipping-workflow` skill (i.e. `/ship`). It handles: commit → push → PR → automated review → merge → cleanup delegation.

If there are no uncommitted changes AND no unpushed commits, skip this step and move to Step 3. Do NOT run `/ship` on a clean tree — it has no work to do.

The handoff doc from Step 1 is committed as part of the shipping PR, NOT as a separate commit. This ensures it ships atomically with the state it describes.

**Doc-only exception.** If the uncommitted diff is documentation-only (no code, no tests, no schemas) AND the repo's `CLAUDE.md` establishes a doc-only-direct-to-main convention — OR recent `git log` shows handoff / archive / plan / README commits landing on `main` without PRs — skip `/ship` and commit directly to main. Confirm with the user before pushing. Validated on toneguard repo (commits `ffe3bfd`, `475514e`, `18407f8`, `76abf6c`); see toneguard `CLAUDE.md` → "Repo Conventions". This is the exception, not the default — repos without an established convention still ship via `/ship`.

## Step 3 — Cleanup

`/ship` delegates its final stage to `/cleanup`, which runs:
- Session-learnings (captures patterns from this session)
- Waits for learnings proposals
- Syncs config/skills/memory repos
- Worktree teardown via `ExitWorktree`

Do not manually invoke session-learnings, sync repos, or remove worktrees — `/cleanup` (triggered by `/ship`) handles all of it.

If Step 2 was skipped (clean tree, nothing to ship), invoke `/cleanup` directly instead.

**Session-learnings is NOT skippable at /next.** Run it even if a learnings pass already fired earlier in the session — /next is a cluster boundary, and work done after the earlier pass (fixes, corrections, shipped rules) is exactly the material that otherwise dies in chat scroll. "The learning was already codified into a rule this session" is not a skip reason either: the analyst's job includes checking whether the codified rule needs cross-links or coverage elsewhere. The ONLY valid skip is a session with zero substantive work since the last pass (pure lookup/status sessions). Origin: 2026-07-06 — a /next close-out skipped learnings with a plausible-sounding rationale; Summer corrected: the next command should include running session learnings.

**Delayed merge approval resumes at cleanup.** If `/ship` stops at a no-CI or user-approval merge gate and Summer later approves the merge, resume `/next` at Step 3 immediately after merge verification. Do not treat merge verification as the end of `/next`; session-learnings, repo sync, and worktree cleanup still run.

## Step 4 — Output the continuation prompt

At the end, output ONE fenced block the user can copy into their next session:

```
## Continuation prompt

<5–10 lines: name the goal, point at the handoff doc, state the mode directive>

Reference: docs/plans/<handoff-file>.md
```

The handoff doc is the source of truth; the pasted prompt is the entry point.

## Guardrails

- Step 1 MUST complete before Step 2. If the handoff doc can't be written (no obvious next task, current work is exploratory-only), say so and STOP — do not ship without a handoff.
- If `/ship`'s review stage surfaces issues that block merge, STOP. Do not clean up. Report the blocker and let the user decide.
- If the work is on a branch with an already-open PR, update the PR body (not a new PR) and continue through review → merge → cleanup.
- **Design-doc-for-review posture.** When the open PR is a design doc / decision record / plan intended for team review BEFORE merge (not auto-merge after CI), STOP after the handoff doc lands on the same branch. Do not run `/ship`'s merge stage. Hand off to `/cleanup` with the PR-open-intentionally framing — the PR stays open for human review and the next session resumes from the handoff doc. Validated twice — courierflow_beta [PR #100](https://github.com/sumrae412/courierflow_beta/pull/100) (Charlie prompt redesign — design doc + migration plan + handoff all on one branch, PR open for team review, worktree torn down) and [PR #104](https://github.com/sumrae412/courierflow_beta/pull/104) (Riley tenant-assistant design record — decision doc + handoff committed atomically, PR open for founder review on Q1/Q2/Q3). Established convention for design-doc / decision-record / plan PRs.
- Never create a handoff doc for a session with no meaningful work to hand off. Session-learnings captures trivial sessions; handoff docs are for active work streams.
- **After re-categorizing or re-framing anything in the handoff doc, grep the whole doc for the old framing before saving.** Partial edits leave self-contradictions (e.g. one section says "shipped," another says "pending decision") that CodeRabbit and the next agent will flag — and the next agent has no way to know which framing is current. Pattern: `grep -n "<old-phrase>" docs/plans/<handoff>.md` after each structural edit. Validated on [courierflow_beta PR #5](https://github.com/sumrae412/courierflow_beta/pull/5) handoff doc.

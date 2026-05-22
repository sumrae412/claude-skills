# Session handoff — 2026-05-22

**For the next agent who picks this up.** Zero memory in the next conversation; everything you need is here. Read top-to-bottom before touching code.

## Goal

No active carryover. [courierflow_beta PR #8](https://github.com/sumrae412/courierflow_beta/pull/8) (RAMPART classifier follow-ons) **merged before this handoff finished writing** — verified at 2026-05-22 13:0X via `gh pr view 8 --json state` → `MERGED`. If the user wants new work, route it through `/claude-flow`. If anything below contradicts "PR #8 is merged," trust the live `gh pr view` output.

## Current state

**Repos touched this session — all in sync:**

| Repo | Branch | Local vs origin | Notes |
|---|---|---|---|
| `~/claude_code/claude-skills/` | `main` | clean / in sync at `ae505dc` | session-learnings commit pushed. Pre-existing untracked drift in `claude-flow/`, `prd/`, `startup-analysis/` unrelated to this session — leave alone unless investigating |
| `~/.claude/` | `master` | clean / in sync at `a628d65` | 3 Git/Shell/CI checklist items pushed. Other tracked files modified locally (memory dirs, deleted session JSONs, ~17 untracked files) are pre-existing local state — DO NOT sweep into commits |
| `~/claude_code/courierflow_beta/` | `main` fast-forwarded to `38c1783` post-PR-#8-merge | clean | [PR #8](https://github.com/sumrae412/courierflow_beta/pull/8) merged as `dfdb5cc`; parallel session followed with PR #9 (`ca3a2d4` haiku model alias fix on my classifier.ts) and PR #10 (`38c1783` chat-backbone plan) |
| `~/claude_code/courierflow/` (legacy) | n/a | frozen-reference mode | DO NOT COMMIT |

**What shipped this session (commits in order):**

1. **courierflow_beta `fcfc47c`** — RAMPART Surface-1 follow-on: XML delimiter on SMS body (`classifier.ts`) + 3-scenario vitest injection test file (skipIf no API key) + `test:injection` script in api-server package.json. Cherry-picked to main after initially landing on the parallel session's feature branch; pushed as `feat/rampart-classifier-followons` and opened as [PR #8](https://github.com/sumrae412/courierflow_beta/pull/8).
2. **claude-skills `ae505dc`** — session-learnings: defensive-backend-flows gets "LLM Prompt Injection (User Content)" pattern (Quick Reference row + Red Flag + full body in `references/patterns.md`); coding-best-practices/docs/testing.md gets "Token-expensive tests: separate npm-script lane, skip-by-default" section.
3. **~/.claude `a628d65`** — global CLAUDE.md: 3 new Git/Shell/CI checklist items (stale handoff sweep, courierflow_beta single-working-dir parallel-session branch race, pnpm corepack typecheck workaround).

**MEMORY (local-only, gitignored per policy):**
- 4 new detail files in `~/.claude/projects/-Users-summerrae-claude-code-claude-skills/memory/`:
  - `llm_prompt_injection_xml_delimiter_pattern.md`
  - `courierflow_beta_parallel_session_branch_race.md`
  - `stale_handoff_cross_repo_sweep.md`
  - `pnpm_filter_typecheck_corepack_preinstall.md`
- `MEMORY.md` index appended with 4 entries (legacy-tracked but ignored by current policy; changes are local).

**What's still in-flight:**

- Nothing. [PR #8](https://github.com/sumrae412/courierflow_beta/pull/8) merged 2026-05-22 before this handoff finished writing.

**What I deliberately did NOT do:**

- The courierflow_beta `CLAUDE.md` was edited this session to add the same parallel-session-race + pnpm-corepack bullets, but the **parallel session's mid-session rewrite of `CLAUDE.md` reverted my 2 bullets** (and refactored their own earlier "Charlie" identity content). The same content is preserved in [`~/.claude/CLAUDE.md`](https://github.com/sumrae412/claude-config/blob/master/CLAUDE.md) (loaded every session) and in the MEMORY detail files. Re-applying to courierflow_beta CLAUDE.md was deferred — defer further until the parallel session settles. See premise-contradiction discipline in [[stale-handoff-cross-repo-sweep]].
- The 5 modified files in claude-skills present at session start (`cleanup/`, `coding-best-practices/SKILL.md`, `defensive-ui-flows/references/patterns.md`, `next/`, `shipping-workflow/phases/phase-1-preflight-and-commit.md`) were cleared mid-session by something external (parallel session? linter? unclear). Did not investigate. If they reappear, triage before any new claude-skills commit.

## Exact next task

**No default task — PR #8 merged before this doc finished writing.** Pull local main in courierflow_beta to fast-forward to the squash commit, then await user direction:

```bash
cd ~/claude_code/courierflow_beta && git checkout main && git pull origin main --ff-only
```

**If the user pivots to new work**, route to `/claude-flow`. RAMPART Surfaces 2/3/4 (calendar, lease, chat) are NOT recommended follow-ons per the original [2026-05-22-rampart-fit-assessment.md](https://github.com/sumrae412/courierflow_beta/blob/main/docs/decisions/2026-05-22-rampart-fit-assessment.md) — Surfaces 2/3 have structural mitigations (enum gate, JSON schema) that already reduce risk, Surface 4 has the explicit "DATA not instructions" rule in the system prompt already. Only revisit if a real incident surfaces.

## Template / reference PRs

- **For the RAMPART pattern (already shipped, this is the template):** [PR #8](https://github.com/sumrae412/courierflow_beta/pull/8).
- **For the cherry-pick recovery dance when parallel sessions race the branch:** see [[courierflow_beta_parallel_session_branch_race]] (MEMORY file path: `~/.claude/projects/-Users-summerrae-claude-code-claude-skills/memory/courierflow_beta_parallel_session_branch_race.md`). The exact 6-step recipe was validated this session.

## Pre-flight commands

```bash
# Step 0 — cross-repo "today's commits" sweep (catch overnight parallel-session ships)
for d in ~/claude_code/courierflow_beta ~/.claude ~/claude_code/claude-skills; do
  (cd "$d" && echo "--- $d ---" && git log --since="24 hours ago" --oneline)
done

# Step 1 — confirm working repo + sync remote
cd ~/claude_code/courierflow_beta && git fetch origin --prune

# Step 2 — confirm PR #8 state
env -u GH_TOKEN gh pr view 8 --repo sumrae412/courierflow_beta --json state,mergeable,reviewDecision,statusCheckRollup

# Step 3 — read this handoff doc + the RAMPART decision record + the PR diff
cat ~/claude_code/claude-skills/docs/plans/2026-05-22-session-handoff.md
cat ~/claude_code/courierflow_beta/docs/decisions/2026-05-22-rampart-fit-assessment.md
env -u GH_TOKEN gh pr diff 8 --repo sumrae412/courierflow_beta
```

## Architectural invariants to preserve

- **Multi-repo disposition routing:** [[active_projects_routing_preface_pattern]]. Echo `pwd` + repo disposition before first write in multi-repo projects. `courierflow_beta` is active; `courierflow` (legacy) is frozen.
- **Single-working-directory branch race:** [[courierflow_beta_parallel_session_branch_race]]. Re-check `git branch --show-current` immediately before every `git commit` in courierflow_beta. The parallel session can switch branches at any moment.
- **Stale handoff sweep:** [[stale_handoff_cross_repo_sweep]]. The Step 0 sweep above IS this invariant.
- **`GH_TOKEN` env var override:** [[gh_token_env_var_overrides_keyring]]. Every `gh` call gets `env -u GH_TOKEN` prefix.
- **PR squash-merge fast-forward false positive:** [[gh_pr_merge_fast_forward_warning_false_positive]]. Verify via `gh pr view --json state`, not the scary text.
- **LLM prompt-injection defense:** [[llm_prompt_injection_xml_delimiter_pattern]]. Stack-agnostic; applies any time tenant or untrusted text reaches a model invocation.
- **Token-expensive test lane:** [[#3 in `coding-best-practices/docs/testing.md`]]. Keep API-cost tests out of `test:unit`; gate every describe at file scope; separate npm script.

## Parked artifacts

None this session. Nothing in `/tmp`, no stashes, no uncommitted patches the next agent needs to resume from. Working trees in all 3 repos contain pre-existing parallel-session state but no work-in-progress mine to recover.

## Gates

- **For merging PR #8:** the in-PR verification was `tsc → EXIT=0` + `vitest run classifier.injection.test.ts → 3 skipped, 1 file skipped` (skipped without `ANTHROPIC_API_KEY` is the safe state). If running a paid pre-merge check is desired: `cd ~/claude_code/courierflow_beta/artifacts/api-server && ANTHROPIC_API_KEY=… ../../node_modules/.bin/vitest run --reporter=verbose src/lib/classifier.injection.test.ts` — costs Anthropic tokens, expect 3 passes.
- **For any new courierflow_beta code:** `./node_modules/.bin/tsc -p artifacts/<pkg>/tsconfig.json --noEmit` from the workspace root. Do NOT use `pnpm --filter run typecheck` — see [[pnpm_filter_typecheck_corepack_preinstall]].
- **For claude-skills changes:** `./scripts/quick_ci.sh` (Markdown link checker + grep gates).

## Ship instructions

- **PR #8 already merged.** Nothing to ship from this session.
- **For new feature work:** route to `/claude-flow`.

## Mode directive

Auto mode. Surface premise contradictions only.

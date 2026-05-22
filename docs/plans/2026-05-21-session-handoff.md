# Session handoff — 2026-05-21 evening

**For the next agent who picks this up.** This session has zero memory in the next conversation; everything you need is here. Read top-to-bottom before touching code.

## Goal

Pick up the deferred RAMPART read-only fit assessment (small, ~15 min, closes the original `/articles` triage loose end). After that, decide whether to start P2.1 of the courierflow_beta migration plan (slim the global `~/.claude/CLAUDE.md` by deduping Python-specific gotchas already present in the legacy repo's own `CLAUDE.md` — high-leverage, ~30 min). User has not yet committed to P2.1; flag and confirm.

## Current state

**Repos touched this session — all committed, NOT pushed:**

| Repo | Ahead of origin | Status | Notes |
|---|---|---|---|
| `~/claude_code/claude-skills/` (main) | 4 commits (`a8f9e29`, `40cc38a`, `a21932c`, `5b361dd`) | Clean tree | `/ship`-able. The handoff doc you're reading will be commit #5. |
| `~/.claude/` (master) | 1 commit (`8a3567b`) | Clean (relative to my changes; pre-existing local-only state untouched) | Direct push to master (no PR convention in this repo's log) |
| `~/claude_code/courierflow_beta/` (main) | 2 commits ahead (`9fd7f47`, `79df55d`), **1 commit BEHIND origin** | Clean tree | `git pull --rebase origin main` before pushing. Origin commit: `d34265b fix: forward model + getLanguageModel on FallbackAnthropicAdapter (#4)` |
| `~/claude_code/courierflow/` (legacy, frozen) | In sync | Untracked `.knowledge/` + `artifacts/` are pre-existing, not from this session | **DO NOT COMMIT** to this repo — it's in frozen-reference mode per [[active-projects-routing-preface-pattern]] |

**What shipped this session (commits in order):**

1. **claude-skills `a8f9e29`** — `/articles` triage outputs (NPM Mini Shai-Hulud supply-chain runbook, outcome grader reference, codegraph + MCP scoping sections in token-economy, `/articles` skill scope fix)
2. **`~/.claude/` `8a3567b`** — global CLAUDE.md: "Active projects" preface table naming both CourierFlow repos with dispositions; scope the existing "CLAUDE.md — CourierFlow" section as "LEGACY Python repo only"
3. **claude-skills `40cc38a`** — banner `courierflow-{api,data,ui}` SKILL.md as legacy-Python-only scope (description prefix + visible banner; do-not-auto-trigger note for `courierflow_beta` cwd)
4. **courierflow_beta `9fd7f47`** — bootstrap repo for Claude sessions: `CLAUDE.md` (thin pointer to `replit.md`), `docs/decisions/2026-05-21-claude-smb-positioning.md` (competitive intel on Anthropic's Claude-for-Small-Business launch), `docs/plans/2026-05-21-courierflow-migration.md` (P1/P2/P3 stack-migration plan)
5. **claude-skills `a21932c`** — rewrite `token-economy/references/external-tools.md` codegraph section with measured trial findings (grep 16× faster than codegraph `context` on this repo; codegraph misleads on cross-framework data-flow questions)
6. **courierflow_beta `79df55d`** — `docs/decisions/2026-05-21-codegraph-trial.md` (measured trial writeup) + `.gitignore += .codegraph/`
7. **claude-skills `5b361dd`** — session-learnings updates: trial-protocol section in token-economy external-tools, runbook authoring conventions in dependency-auditor supply-chain-incidents, built-in tool cost notes in token-economy SKILL.md

**What's in-flight:** None. All work above is committed locally; nothing is mid-edit. The only pending action is push/PR/merge for the three repos with unpushed commits.

**Memory dir additions (local-only, gitignored per policy):**
- `feedback_articles_skill_claude_articles_only.md` (plus cross-ref appendage)
- `feedback_askuser_concrete_options_over_abstract_tiers.md`
- `feedback_wrong_repo_commit_recovery_unpushed.md`
- `active_projects_routing_preface_pattern.md`
- `MEMORY.md` index updated with the 3 new + 1 existing entry

**Deferred from `/articles` triage:**
- RAMPART read-only fit assessment (pytest-native safety/security testing framework; map onto courierflow_beta's prompt-injection surface: CopilotKit chat, calendar event titles, tenant SMS reply parsing). Article TL;DR is in `~/claude_code/courierflow_beta/docs/decisions/...` referenced files; the original Mem note ID is `33f7aa6c` if needed for the source.

## Exact next task

**Default path: RAMPART read-only fit assessment.**

1. `cd ~/claude_code/courierflow_beta` first — the assessment is against beta's surface, not legacy.
2. Read RAMPART's README via `gh api repos/microsoft/RAMPART/contents/README.md --jq .content | base64 -d | head -200`. **Do NOT install it.** This is read-only.
3. Map onto courierflow_beta's actual prompt-injection surface — places where landlord/tenant-supplied text feeds into model invocations:
   - CopilotKit chat input (the sidebar agent assistant; entry point in `artifacts/web/src/` near `RequireAuth` shell)
   - Calendar event titles (Google Calendar sync → workflow trigger; event title text is user-controlled)
   - Tenant SMS reply parsing (inbound SMS → AI classification → action; covered in PRD's three-tier classifier)
   - Lease ingestion text (lease document upload → AI extraction; covered in `lib/db/src/schema/lease_ingestions.ts`)
4. Output a 1-page decision record at `~/claude_code/courierflow_beta/docs/decisions/<today>-rampart-fit-assessment.md`. Sections:
   - Status (keep / try-install / skip)
   - Surface enumerated (per the 4 above)
   - RAMPART scenarios that would map onto each surface, in priority order
   - Verdict — install only if 3+ scenarios map strongly; otherwise skip and note in `skill-security-auditor` references as "evaluated, not installed"

**Acceptance criteria:** the decision record stands alone (someone reading it cold knows what RAMPART is, what it would protect, what it wouldn't, and whether to install).

**Alternate path: confirm with user, then start P2.1.** Slim `~/.claude/CLAUDE.md` by deleting Python/SQLAlchemy/Jinja gotchas that are duplicated in `~/claude_code/courierflow/CLAUDE.md`. High-leverage (reduces context bloat every session) but ~30 min of careful dedupe. **Do NOT start P2.1 without user confirmation** — they have not yet authorized it. The migration plan at `~/claude_code/courierflow_beta/docs/plans/2026-05-21-courierflow-migration.md` § P2.1 has the dedupe protocol.

## Template / reference PRs

- For the P1 migration pattern (if continuing migration work): the 5 commits from this session listed above ARE the template.
- For codegraph-style measured-trial-of-Mem-article-tool: `~/claude_code/courierflow_beta/docs/decisions/2026-05-21-codegraph-trial.md` is the worked example. Same shape for the RAMPART trial if it goes past read-only.
- For decision record format: `~/claude_code/courierflow_beta/docs/decisions/2026-05-21-claude-smb-positioning.md` is a recent example.

## Pre-flight commands

```bash
# Confirm where you are + which CourierFlow repo is active
pwd
cat ~/.claude/CLAUDE.md | grep -A 5 "Active projects"

# Sync remote state — courierflow_beta is behind 1
cd ~/claude_code/courierflow_beta && git fetch origin --prune
git log HEAD..origin/main --oneline  # confirms the one commit you're behind

# Read this handoff doc + the migration plan + the codegraph trial
cd ~/claude_code/claude-skills && cat docs/plans/2026-05-21-session-handoff.md
cat ~/claude_code/courierflow_beta/docs/plans/2026-05-21-courierflow-migration.md
cat ~/claude_code/courierflow_beta/docs/decisions/2026-05-21-codegraph-trial.md
```

## Architectural invariants to preserve

- **Multi-repo disposition routing:** [[active-projects-routing-preface-pattern]]. Always echo `pwd` + repo disposition before first write in multi-repo projects. `courierflow_beta` is **active**; `courierflow` (legacy) is **frozen** — no new commits.
- **Wrong-repo commit recovery:** [[feedback-wrong-repo-commit-recovery-unpushed]]. If you commit to the wrong repo on unpushed work: `git rev-list --count origin/main..HEAD` to confirm unpushed → cp file to right repo → `git reset --hard HEAD~1`.
- **AskUserQuestion artifact-naming rule:** [[feedback-askuser-concrete-options-over-abstract-tiers]]. Option labels must name actual files/edits, not abstract tiers. User can't pick between "critical path / full plan" without artifact lists.
- **Beta CLAUDE.md = thin pointer:** beta repo's `CLAUDE.md` references `replit.md` for project context. Don't duplicate stack/run-command/file-layout content.
- **External-tool trial discipline:** before promoting any Mem-article tool to "default for task class X" in `token-economy/references/external-tools.md`, run a measured trial against the current default. See the new "Trial protocol" section at top of that file.
- **Runbook authoring rule:** for incident runbooks (`dependency-auditor/references/supply-chain-incidents.md`), kill the persistence mechanism BEFORE the cleanup action it would re-corrupt. See the new "Runbook authoring conventions" section.
- **`/articles` scope:** `/articles` pulls from one Mem collection only (`421a7805-...`). See [[feedback-articles-skill-claude-articles-only]] — the over-broad version caused a side-effect on 2 unrelated notes earlier in this session.

## Parked artifacts

None this session. All work is committed; nothing is sitting in a saved patch, stash, or untracked file the next agent needs to resume from.

## Gates

- `./scripts/quick_ci.sh` in claude-skills if any code paths change (no change expected on RAMPART read-only path)
- For courierflow_beta: `pnpm run typecheck` is the validation step per `replit.md`. The Replit harness runs it automatically on task completion; no manual gate needed unless editing TS code.
- `gh api repos/microsoft/RAMPART --jq .archived` before relying on RAMPART — verify it's still maintained.

## Ship instructions

**Multi-repo session — 3 push targets, not 1.** Standard `/ship` is single-repo. Choose:

**Option A (lightweight, recommended for this session's content):** direct push to each remote, no PR. Justified because the work is docs/skills/memory only, single contributor on these repos:
```bash
cd ~/claude_code/claude-skills && git push origin main
cd ~/.claude && git push origin master
cd ~/claude_code/courierflow_beta && git pull --rebase origin main && git push origin main
```

**Option B (full /ship per repo):** run `/ship` separately for claude-skills and courierflow_beta (each gets its own PR + review pipeline). For `~/.claude/`, direct push (no PR convention there).

The user previously expressed openness to either; **confirm before pushing**. Note that courierflow_beta needs the rebase regardless.

After ship, the handoff doc itself rides along in claude-skills's push. Do not commit it as a separate PR.

## Mode directive

Auto mode. Surface premise contradictions only.

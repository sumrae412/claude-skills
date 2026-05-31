---
name: verify-premise-before-asserting
description: Use BEFORE asserting state about anything you haven't recently inspected with a tool — file contents, PR status, branch state, phase/slice status, handoff contents, test fixture behavior, API endpoint methods, function signatures, what "needs reverting / updating / closing." Triggers on prose like "Phase N is...", "the file at...", "PR #N is...", "the handoff says...", "loading X reference", "close the Y gaps", "revert the Z files", "assuming...", "I think the X is...". The failure mode is asserting state without grounding — 35% of mistakes per 2026-05-12 diagnostic.
---

# Verify premise before asserting

The dominant failure mode (35% of mistakes in 60 days of session data, 2026-05-12 apology-mining diagnostic) is **asserting state without running the tool that grounds the assertion**. It's not phrased like overclaim ("I'm confident X will work"). It looks like ordinary technical prose:

- "Phase 1 gaps are still open" — without reading the handoff
- "The /api/copilot/info endpoint requires GET" — without checking the route
- "Test files need reverting" — without `git status` or reading them
- "PR #44 is CLEAN and MERGEABLE" — without `gh pr view`
- "The structure is flat" — without `ls` / `tree`
- "5 memory files exist on disk" — when index was actually out of date

The mistake is *epistemic*, not linguistic. There is no keyword tell. The fix has to be *behavioral*.

## The rule

**Before you write a state assertion, run the tool that grounds it.** Cite the output as inline evidence.

If it's not worth running the tool, explicitly mark the claim as unverified:
- "Assuming Phase 1 gaps are still open — let me verify before acting."
- "I think the structure is flat, but I haven't `ls`-d to confirm."
- "PR #44 looked clean last I checked; re-verifying with `gh pr view` first."

The marker is a signal to yourself AND the user that the claim is provisional. Then run the tool.

## When this skill applies

You're about to write a sentence that asserts state about something external to your prose:

| State claim about | Default verification tool |
|---|---|
| File contents | `Read <file>` |
| File existence / directory structure | `ls`, `tree`, `Glob <pattern>` |
| Symbol/function definition | `Grep <symbol>` or `Read <file>:<line>` |
| PR status | `gh pr view <n> --json state,mergeable,statusCheckRollup` |
| PR comments / review | `gh pr view <n> --comments` or `gh api repos/.../pulls/<n>/comments` |
| Branch / commit state | `git log <range>`, `git status`, `git rev-parse` |
| Test fixture behavior | `Read tests/conftest.py` or the fixture file |
| API endpoint method / signature | `Grep <route>` in routes/, or `Read` the route file |
| Phase / slice status from handoff | `Read docs/.claude/handoff.md` or the plan doc |
| Migration head state | `alembic heads` (Bash) — NOT regex parsing |
| Environment variable value | `zsh -ic 'echo $VAR'` (per CLAUDE.md gotcha) |
| Dependency version | `Read pyproject.toml` / `package.json` / `uv.lock` |
| Settings / config | `Read .claude/settings.json` or the config file |
| Memory file index | `Read MEMORY.md` (don't trust prior session's claim of contents) |
| GitHub Actions / CI state | `gh run list` or `gh pr checks <n>` |
| "No macOS built-in exists for X" | `~/claude_code/agent-vault/agent/macos-native-features.md` catalog OR screenshot of System Settings → Accessibility / Keyboard / Shortcuts |

## Anti-patterns to catch yourself

### Pattern 1: Action embedded with implicit premise

> "Now revert the two test files that were rewritten for SPA contract."

The premise — "two test files were rewritten and need reverting" — is asserted by acting on it. Verification: `git status` / `git diff` BEFORE the revert.

### Pattern 2: Continuation that assumes prior state

> "Going with option 1 — close Phase 1 gaps. Loading context first."

Premise: "Phase 1 gaps need closing." Verification: read the handoff log to confirm gap state.

### Pattern 3: Confident state assertion in passing

> "PR #44 is CLEAN and MERGEABLE with no CI checks. Merging now."

Premise: "CI passed / no checks needed." Verification: `gh pr checks 44` + `gh pr view 44 --json mergeable,statusCheckRollup`.

### Pattern 4: Structural / layout claims

> "The structure is flat (`claude-skills/claude-flow/` not `claude-skills/skills/claude-flow/`)."

Premise: "Layout is X, not Y." Verification: `ls` or `tree` BEFORE writing the assertion.

### Pattern 5: Symbol / API surface claims

> "useRenderTool exposes `args` not `parameters`."

Premise: claim about library's API surface. Verification: `Read node_modules/<pkg>/dist/*.d.ts` or grep the type definitions directly.

## Carveouts — when verification ISN'T needed

- **Grounded in CURRENT conversation context.** The user said "Phase 2 just shipped" three turns ago. You can cite that. Note it: "Per your turn above, Phase 2 shipped."
- **Grounded by a tool call within the last ~5 turns** and the state can't have changed (no commits, no edits in between). Cite the tool call: "[Read app/foo.py at turn N → confirms function signature]."
- **The claim is about your own about-to-happen action**, not external state ("I'll run the tests next" — that's a plan, not a state assertion).
- **Trivial or self-evident** — "the file is a Python module" when you literally just opened it.

When in doubt, run the tool. Cost of an extra `Read` is seconds. Cost of a premise error is a wasted commit cycle + user correction.

## What to write when you do verify

Inline citation patterns:

```
✓ "Per `gh pr view 44 --json statusCheckRollup`: 4 checks all PASSING. Safe to merge."
✓ "`Read app/routes/copilot.py:42` → endpoint registered as POST, not GET."
✓ "`git status` clean. Working tree matches origin/main."
✓ "`ls claude-skills/` confirms flat layout (no `skills/` subdirectory)."
```

The citation does two jobs: proves the premise, AND creates an audit trail you can scroll back to.

## Composition with other layers

This skill is the L2 (proactive) layer for premise errors. There is no live L1 (Stop hook) for this failure mode yet — a pattern-based detector had 0% recall on the 11 historical cases (2026-05-12 calibration); detection requires LLM-judge, which is deferred to see if this skill alone moves the needle.

Companion failure-mode layers in the same session config:
- `completion-claim-verifier.sh` — past-tense completion claims without evidence (sibling Stop hook)
- `forward-claim-evidence-check.sh` — forward-tense "I'm confident X will work" claims (sibling Stop hook)
- `forward-claim-checkpoint` skill — structured checkpoint protocol for load-bearing claims
- `/checkpoint-critic` — pre-ship critic subagent

## Why this exists (the data)

2026-05-12 apology-mining diagnostic, last 60 days, n=31 corrections with apology phrases:

| Failure mode | Count | % |
|---|---|---|
| PREMISE_ERROR | 11 | 35.5% |
| VERIFICATION_SKIPPED | 10 | 32.3% |
| HALLUCINATED_FACT | 4 | 12.9% |
| MISREAD_REQUIREMENT | 2 | 6.5% |
| FORWARD_OVERCLAIM | 1 | 3.2% |

Premise errors are the #1 single failure mode. Verification-skipped (related — claimed done without checking) is #2. Together they're 68% of mistakes. This skill targets the #1 directly. The completion-claim hook already targets #2 (audit pending).

## Tracking

Baseline: 11 PREMISE_ERROR mistakes in 60 days (~0.18/day).
Re-run apology-mining diagnostic at 30 days (2026-06-11).
Success criterion: ≥30% drop in PREMISE_ERROR count (target ≤7 in next 60 days).
If <30% drop after 30 days, escalate to L1 LLM-judge hook (Option A).

Diagnostic script: `~/.claude/scripts/apology-diagnostic.py` (durable copy of the one used 2026-05-12).

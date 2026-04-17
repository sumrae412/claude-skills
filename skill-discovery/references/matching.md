# Intent → Skill Matching

Heuristics for routing user intent to the right local skill. Load this when the local session pass is ambiguous.

## How the session list is shaped

Skills appear in the system-reminder in two forms:

- **Bare name** (`research`, `fetch-api-docs`, `smart-exploration`) — top-level skills from `~/.claude/skills/`
- **Namespaced** (`plugin:skill-name`, e.g. `superpowers:brainstorming`, `common-room:account-research`) — skills provided by installed plugins

When searching, match on the trailing segment (the skill name itself), but include the namespace in the final recommendation so the user/invocation knows which skill file.

## Common intent buckets

| User intent | Likely skill | Not this |
|-------------|--------------|----------|
| "read official docs for library X" | `fetch-api-docs` | `research` (too broad) |
| "open-ended exploration / synthesis" | `research`, `deep-research-synthesizer` | `fetch-api-docs` (single-source) |
| "navigate an unfamiliar codebase" | `smart-exploration`, `investigator` | `research` (external-facing) |
| "build a feature / implement a plan" | `/claude-flow` (per CourierFlow CLAUDE.md) | raw `writing-plans` + `executing-plans` |
| "fix a bug / reproduce an error" | `/bug-fix` | `/claude-flow` (explicitly excluded for bugs) |
| "write tests first" | `test-driven-development`, `superpowers:test-driven-development` | `playwright-test` (E2E-specific) |
| "E2E / browser automation tests" | `playwright-test`, `website-tester` | generic TDD |
| "design a UI / critique a design" | `frontend-design:frontend-design`, `design:design-critique` | `excalidraw` (conceptual diagrams) |
| "draw a diagram / architecture viz" | `excalidraw`, `excalidraw-canvas` | `image-generation` (photoreal) |
| "generate an image / hero asset" | `image-generation`, `anthropic-skills:canvas-design` | `excalidraw` |
| "ship code / commit + PR + merge" | `/ship` / `shipping-workflow`, `commit-commands:commit-push-pr` | individual git commands |
| "pre-ship audit" | `production-readiness-check` | `/ship` (runs after audit) |
| "code review" | `code-review:code-review`, `pr-review-toolkit:review-pr`, `coderabbit:review` | `/ship` |
| "debug a running system" | `superpowers:systematic-debugging`, `engineering:debug` | `investigator` (file-level) |
| "search Slack / summarize channel" | `slack-by-salesforce:*` | generic `research` |
| "Gmail draft / search" | (no local skill — use `mcp__*gmail_*` tools directly) | — |
| "write a new skill" | `superpowers:writing-skills` | `anthropic-skills:skill-creator` (simpler path) |
| "configure a hook / settings.json" | `update-config`, `hookify:configure` | manual edits |
| "refactor / simplify code" | `simplify`, `pr-review-toolkit:code-simplifier` | — |

## Scanning discipline

Before declaring a match:

1. Read the skill's `description` field (not just its name) — names can be misleading.
2. If two skills look similar, read both SKILL.md files. Common overlaps: `research` vs `deep-research-synthesizer`, `excalidraw` vs `excalidraw-canvas`, `writing-plans` vs `plancraft`.
3. Prefer the **most specific** skill for the task. `research` is a catch-all and is often wrong when a narrower skill exists.
4. Respect project overrides: this repo's CLAUDE.md routes feature work to `/claude-flow` and bugs to `/bug-fix` — honor those over generic matches.

## Common mis-matches (observed)

- **`research` picked for "read these API docs"** — `fetch-api-docs` is the correct choice; `research` is for open-ended synthesis.
- **`smart-exploration` picked for external research** — it's a codebase-navigation skill, not a web-research one.
- **`writing-plans` picked mid-implementation** — once execution starts, `/claude-flow` or `executing-plans` applies; `writing-plans` is pre-plan only.
- **`superpowers:*` duplicate of a top-level skill picked randomly** — when both exist (`test-driven-development` vs `superpowers:test-driven-development`), prefer the one explicitly referenced elsewhere in project memory/CLAUDE.md; otherwise note both and let the user choose.
- **`excalidraw` picked for UI mockups** — it's for conceptual argument-diagrams, not UI design. Use `frontend-design:frontend-design` for UI.

## When no local skill fits

Before proposing an external install, confirm:

- The task is not already covered by a plugin skill the user has installed but that's not surfaced (check `~/.claude/plugins/` directory).
- The task is not a one-off that doesn't need a skill at all (skills are for repeated patterns, not single problems).

Then proceed to [registries.md](registries.md) for the external search path.

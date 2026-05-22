# External tools that automate token-economy patterns

Resources that operationalize the skill's principles as infrastructure rather than discipline. Use when you apply a pattern manually often enough that automating it pays off.

---

## rtk-ai/rtk — CLI proxy for LLM token optimization

**Repo:** https://github.com/rtk-ai/rtk
**License:** Apache-2.0
**Saved from Mem reading queue 2026-05-20.**

Rust binary that intercepts and pre-filters CLI output (git, ls, grep, test runners, docker, etc.) before it reaches the LLM. Reported 60–90% token reduction on common dev commands via smart filtering, grouping, truncation, and deduplication. Integrates with Claude Code, Copilot, Gemini CLI, Cursor.

**Maps to skill patterns:**
- Pattern 9 (response-shape minimalism) — externalized for CLI output
- Pattern 4 (entry-point-first exploration) — `rtk ls .` returns a token-optimized tree instead of a raw `ls -la` dump

**When to install:**
- You run `git status`, `git diff`, `cargo test`, `pytest` frequently inside a Claude Code loop
- You see large blocks of CLI output landing in context that you immediately wish were summarized

**When to skip:**
- Mostly REST/API or DB work — the proxy targets shell output, not network responses
- Single-shot lookups — install overhead outweighs savings

**Install:** Homebrew, Cargo, or pre-built binary. Example commands rewritten by rtk: `rtk git status`, `rtk test cargo test`, `rtk grep "pattern" .`, `rtk docker ps`.

**Pairs with `claude-flow`:** worth recommending at Phase 5 entry on compute-heavy implementation runs where the executor will spawn many shell calls per turn.

---

## colbymchenry/codegraph — pre-indexed code knowledge graph

**Repo:** https://github.com/colbymchenry/codegraph
**Saved from Mem reading queue 2026-05-21.**

Local SQLite-backed code knowledge graph that agents query instead of scanning files. Author-reported medians on the published benchmarks: ~35% cheaper, ~59% fewer tokens, ~49% faster, ~70% fewer tool calls. 100% local, no network egress. Supports 19+ languages and recognizes routing patterns for 13 web frameworks (Django, FastAPI, Express, NestJS, Laravel, Rails, Spring, etc.).

**Maps to skill patterns:**
- Pattern 1 (combine discover + read) — single graph query replaces glob → read → grep chains
- Pattern 4 (entry-point-first exploration) — framework-aware route detection finds the right file without prose-search
- Pattern 7 (delegate to cheap subagents) — graph queries can be smaller subagent prompts ("which files define `handlePayment`") and return structured answers instead of file dumps

**Install:** `npx @colbymchenry/codegraph`, then `codegraph init -i` in the project root. Native OS file-watching keeps the index in sync.

**When to install:**
- Repos > 50 source files where Phase 2 / Phase 4 exploration burns tokens on grep + read fan-out
- Multi-language repos — single index across TS/Python/Go/Rust avoids switching grep strategies

**When to skip:**
- One-shot tasks where the index-build cost outweighs query savings
- Repos where the entry points are already memorized (CLAUDE.md or `active-files` registry covers it)
- Network-restricted environments that can't run `npx` — though once installed it's offline-only

**Pairs with `smart-exploration` and `claude-flow` Phase 2:** if `codegraph` is initialized for a project, the exploration phase should prefer graph queries over generic grep fan-outs. Worth a measured trial on a real repo before promoting to default.

---

## Subagent + MCP scoping (least-privilege pattern)

**Source:** Philschmid, "How to correctly use MCP servers with your AI Agents" (philschmid.de, 2026-05).

When dispatching subagents via the `Agent` tool, every MCP server you leave enabled is tokens in the subagent's tool list and a possible exfiltration path. The Philschmid post names two clean patterns:

**1. Inline tool injection via `@mention`** — keep the global MCP tool surface small; let the user opt in per-prompt. The closest analog in this environment is the `ToolSearch` + `select:<name>` pattern: deferred tools stay invisible until the orchestrator explicitly loads schemas.

**2. Scoped subagent definitions** — give each subagent only the tools it needs:

```yaml
name: code-reviewer
mcp_servers:
  - url: https://github-mcp.example
    allowed_tools:
      - list_pulls
      - list_reviews
      - get_diff
```

**Maps to skill patterns:**
- Pattern 7 (cheap subagent delegation) — tighter tool surface = smaller prompt, cheaper invocation
- Pattern 10 (inject discipline into subagent prompts) — explicit `allowed_tools` is the structural version of "tight tool-call budget"

**How to apply with the `Agent` tool here:**
- Prefer focused subagent_type values (Explore, Plan, specialized review agents) over `general-purpose` — they ship narrower implicit tool sets.
- When dispatching, name the exact tools the subagent should use in the prompt ("use only Grep and Read; do not Edit or run Bash").
- Don't pre-load MCP schemas into a subagent's session unless the task needs them — the `ToolSearch` round-trip is cheap, the always-resident schema is not.

**Pairs with this skill's existing Pattern 10:** the verbatim discipline-injection paragraph + an explicit tool allowlist is the strongest combination.


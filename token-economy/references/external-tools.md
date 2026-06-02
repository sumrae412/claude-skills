# External tools that automate token-economy patterns

Resources that operationalize the skill's principles as infrastructure rather than discipline. Use when you apply a pattern manually often enough that automating it pays off.

---

## Trial protocol for new external tools

Before promoting any tool here from "mentioned in a Mem article" to "default for task class X," run a measured trial against the current default in a representative repo. Record:

1. **Wall time** (`time <cmd>` for each path)
2. **Output size** (lines, bytes) — proxy for token cost
3. **Result quality** (recall + precision against a known answer — pick a question where you can verify the right answer independently)
4. **Tool-call count** (how many separate invocations to assemble an equivalent answer)

Update each tool's entry in this file with the **measured numbers**, not the article's marketing claims. If the trial inverts the headline claim, say so explicitly and scope where the tool *does* fit (good-fit cases) vs *doesn't* (bad-fit cases). Don't paper over the result with hedged language.

**Validated 2026-05-21 on codegraph:** Mem article claimed "35% cheaper, 70% fewer tool calls"; courierflow_beta trial showed grep was 16× faster and captured more relevant code paths because codegraph's `context` ranks by graph-centrality (Orval-generated client wrappers outrank actual Express route handlers). The codegraph entry below was rewritten post-trial to "good fit: pure-symbol queries / bad fit: cross-framework data-flow questions." Full trial writeup: `~/claude_code/courierflow_beta/docs/decisions/2026-05-21-codegraph-trial.md`.

**Why this matters:** an "external tools" reference is a recommendation surface — every entry shapes what tools agents reach for next session. Article claims are marketing; what reaches this file should be evidence. The trial cost is bounded (one representative question, one repo); the cost of recommending the wrong tool is amplified across every future session.

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
**Saved from Mem reading queue 2026-05-21. Measured trial on `courierflow_beta` (TS/pnpm, 210 files) on the same date — see `~/claude_code/courierflow_beta/docs/decisions/2026-05-21-codegraph-trial.md`.**

Local SQLite-backed code knowledge graph that agents query instead of scanning files. Author-reported benchmarks: ~35% cheaper, ~59% fewer tokens, ~70% fewer tool calls. **Those claims did not replicate in the trial** — grep baseline was 16× faster and captured more of the relevant code paths for the test question. Calibrated guidance below.

**Install:** `npx @colbymchenry/codegraph init` then `npx @colbymchenry/codegraph index` in the project root. Indexed 210 files in 4 seconds (3,537 nodes, 3,187 edges); on-disk footprint 7.1 MB SQLite DB. Tool itself is `npx`-only — no persistent global install.

**Use codegraph for** (good-fit cases — confirmed in trial):
- Symbol lookups: `codegraph query <name>` returns a ranked list with file:line precision. Cleaner than `grep <name> -rn .` when the same name appears in many files.
- "Where is X defined" / "what types are named X" questions, especially across a TS workspace with many packages.
- The `affected` command for test-file impact analysis after edits (not measured in trial — advertised feature, worth its own trial when tests stabilize).
- MCP server mode (`codegraph serve`) for Claude Code — also not measured, may change behavior on long sessions.

**Do NOT use codegraph for** (bad-fit cases — confirmed in trial):
- **Cross-framework data-flow questions** (frontend hook → HTTP → backend route → DB write). The connection between layers is by URL string, not function call, so the symbol graph can't traverse it. Both `context` and `query` returned the Orval-generated client wrappers instead of the actual Express route handlers for a "where does Tenant get created" question — actively misleading.
- **Repos under ~500 files** where grep is already fast enough. The 1.3-second-per-query overhead doesn't pay off when `grep -rn` returns in milliseconds.
- **Questions where the agent already has the entry point** (named in CLAUDE.md, `active-files` registry, or PRD docs).

**Why `context` was misleading in trial:** the command ranks symbols by graph-centrality and returns their source. Orval-generated client functions have many inbound edges (every React page imports them), so they rank highest. The actual route handlers have fewer inbound edges, so they get filtered out. For an agent asked "where does X happen?", reading the generated client looks like an answer but points away from the real implementation. Treat `context` output as "candidate symbols" not "the answer."

**Maps to skill patterns:**
- Pattern 1 (combine discover + read) — only when the question is symbol-shaped
- Pattern 4 (entry-point-first exploration) — only when the entry point is a symbol, not a route or a generated wrapper
- Pattern 7 (delegate to cheap subagents) — subagent prompts that wrap `codegraph query` are a tighter contract than "grep for X"

**Pairs with `smart-exploration` and `claude-flow` Phase 2:** do NOT promote to default exploration tool based on the article's claims. Use deliberately for symbol-lookup substeps; keep grep as the default entry point in this kind of repo.

---

## jwill824/nudge-mcp — token telemetry MCP

**Repo:** https://github.com/jwill824/nudge-mcp
**License:** MIT
**Saved from Mem reading queue 2026-06-02. Not installed/audited yet — see "Pre-install gate" below.**

MCP server that reads `~/.claude/projects/` JSONL session files and exposes per-session cost and efficiency metrics as tools the agent can query mid-conversation. Also tracks Copilot CLI from `~/.copilot/session-state/`.

**Exposed tools:**
- `claude_session_report` — recent sessions with cost and efficiency metrics
- `claude_monthly_summary` — total token usage and spend vs. budget
- `analyze_copilot_session` — prompt quality, tool batching, context overhead
- `copilot_model_efficiency` — whether the active model matched task complexity
- `configure_subscription` — update plans and monthly budgets

**Author's reported thresholds** (un-validated until trial — see protocol above):

| Metric | Healthy | Warning |
|---|---|---|
| Cache hit % | >80% (stable prompts) | <60% (unstable prompts or short sessions) |
| Tokens/turn | 40–60k | >150k (speculative reads or oversized context) |

**Maps to skill patterns:**
- Empirical layer for the whole skill — turns "read less" (advisory) into "your tokens/turn is 180k; pattern 4 likely applies" (measurable).
- Pattern 12 (compaction signal): a tokens/turn spike is the early-warning that compaction should be planned, not deferred.

**When to install:**
- Long-running coding sessions where per-session numerics would change pattern selection.
- Multi-project cost accountability — when Summer needs monthly totals across CourierFlow + DLAI work.

**When to skip:**
- Single-shot lookups (telemetry overhead exceeds the gain).
- Cost-constrained sessions where the MCP itself adds tool-list tokens to every prompt.

**Pre-install gate** (mandatory before `claude mcp add`): run `skill-security-auditor` against `https://github.com/jwill824/nudge-mcp`. Repo had 0 stars at save time; the MCP reads local session JSONL files which contain prompt/response payloads. Audit must verify (a) no network exfiltration from the MCP server, (b) no write access outside the configured monthly-budget file, (c) `uvx`-pinned version. Until audited, this entry is documentation only — do not install.

**Install (after audit passes):** `claude mcp add nudge-mcp -- uvx nudge-mcp`.

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


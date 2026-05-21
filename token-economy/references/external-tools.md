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

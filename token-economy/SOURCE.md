# SOURCE — token-economy

## Attribution

Patterns distilled from the WithWoz/wozcode-plugin agent-prompt conventions and tool-description text.

- **Upstream:** https://github.com/WithWoz/wozcode-plugin
- **Plugin version referenced:** `woz@wozcode-marketplace` v0.3.43 (cache: `~/.claude/plugins/cache/wozcode-marketplace/woz/0.3.43/`)
- **Upstream license:** Proprietary ("© WozCode. All rights reserved. Use is subject to WozCode's Terms of Service" — see LICENSE in upstream plugin).
- **Imported date:** 2026-04-20

Pattern 11 (compress prose in always-loaded context files) was inspired by:

- **Upstream:** https://github.com/JuliusBrussee/caveman — specifically the `caveman-compress` subcommand.
- **Upstream license:** MIT.
- **Inspiration date:** 2026-04-23
- **What was taken:** the *idea* that always-loaded memory files pay a recurring token cost and benefit from one-time prose compression with a human-readable backup kept alongside. Nothing else.
- **What was deliberately left behind:** caveman-speak style (articles dropped, fragment grammar, 文言文 mode). Our pattern calls for dense professional prose, not telegraphic shorthand — so the compressed file stays readable to humans and precise for downstream tooling.

## What was imported vs what wasn't

**Distilled (transferable, this skill):**
- The agent-prompt discipline from `agents/explore.md`, `agents/plan.md`, `agents/code.md` — rewritten in our own words, adapted to orthodox Claude Code tools (Read, Grep, Glob, Edit, Bash, Agent).
- The tool-description principles from Woz's `Search` and `Edit` MCP tools — batching, combined discover+read, mtime-aware caching-as-discipline, targeted ranges — transposed onto the orthodox-tool equivalents.

**Not imported (tool-bound, not transferable without building custom MCP):**
- Woz's `Search` tool itself (combined discover-read-in-one-call, `if_modified_since` caching, `summary: true` TS/JS signature mode).
- Woz's `Edit` tool atomic multi-file `edits[]` array.
- Woz's `Sql` tool introspection actions (search/tables/relationships).
- Woz's `Recall` tool.
- The `woz-benchmark` skill (measures savings empirically per-user; if we want quantified baselines, run that separately).

## Vetting

- **No upstream code or text copied verbatim.** Every pattern was rewritten in this repo's voice. The agent-prompt .md files in the upstream cache were read but not quoted.
- **Techniques and patterns are not copyrightable** (17 U.S.C. § 102(b)); expression is. This skill carries the former, not the latter.
- **No API keys, credentials, or proprietary scripts** are referenced.
- **No external tool dependencies** — patterns work with stock Claude Code.

## Local modifications

- Added sibling-skill cross-references (`context-engineering`, `llm-cost-optimizer`, `smart-exploration`) to prevent overlap.
- Added the "Core principle" framing (correctness before economy) — not present in upstream prompts, added as a guardrail against over-applying the patterns.
- Added "What NOT to do" section — explicit false-economy warning.
- Dropped Woz-tool-specific guidance (Search parameters, Edit `edits[]` array, Sql introspection actions) that would be dead pointers without the plugin.
- Substituted orthodox-tool syntax in every example (`Grep(pattern, glob, output_mode)` instead of `mcp__plugin_woz_code__Search(...)`).

## How to update

If upstream Woz ships new agent-prompt patterns:
1. Read `~/.claude/plugins/cache/wozcode-marketplace/woz/<version>/agents/*.md` (after `/plugin` updates the cache).
2. Identify patterns that transfer to orthodox Claude Code tools (not tool-specific).
3. Add to `SKILL.md` — rewrite in this repo's voice, don't copy.
4. Bump `Plugin version referenced` above.

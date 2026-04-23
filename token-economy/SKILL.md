---
name: token-economy
description: "Tool-call-level discipline for minimizing session token burn without sacrificing correctness. Use when starting a cost-constrained session, when noticing heavy token usage mid-session (file-slurping, serial searches, verbose tool narration), or when briefing a subagent on efficient tool use. Teaches combine-discover-and-read, batched edits, parallelized independent searches, entry-point-first exploration, targeted line ranges, don't-re-read-unchanged-files, cheap-subagent delegation, DB introspection over schema-file reads, response-shape minimalism, and dense-prose compression of always-loaded context files (CLAUDE.md and similar). NOT for production LLM API spend (use llm-cost-optimizer) or strategic decisions about *which* files/docs the agent should see (use context-engineering) or claude-flow Phase 2 exploration (use smart-exploration)."
---

# Token Economy

Tactical, per-tool-call discipline for keeping a coding session's token burn low without sacrificing correctness. Patterns distilled from the WithWoz/wozcode-plugin agent-prompt conventions — specifically the half that transfers to orthodox Claude Code tools (Read, Grep, Glob, Edit, Bash, Agent) with no custom MCP required. See SOURCE.md for attribution.

## When to use

- Starting a new coding session with explicit cost or context-window constraints.
- Noticing token usage spike mid-session (whole-file reads for a 10-line answer, serial independent searches, verbose tool-call narration).
- Before dispatching a subagent — inject the relevant rules into the subagent's prompt.
- Handing off long-running tasks (debugging, refactors, audits) where small wastes compound.

**Sibling skills — don't overlap:**
- `context-engineering` — strategic decisions about *which* files/docs the agent sees, across sessions. Pattern 11 below is complementary: once you've decided a file is loaded every session, compress its prose densely.
- `llm-cost-optimizer` — production LLM API spend (model routing, prompt caching infra, batching).
- `smart-exploration` — workflow-internal, claude-flow Phase 2 subagent-prompt library.

## Core principle

**Minimum tokens for a correct answer** — not minimum tokens. If a pattern below would make you miss the actual answer, widen the search. Correctness first; economy second.

## The patterns

### 1. Combine discover + read in one call

If you know both the file scope AND the text pattern, pass both to one `Grep` call with `output_mode: "content"` and a `glob` filter. Don't chain `Glob → Read → Grep`.

- **Bad:** `Glob("src/**/*.ts")` → inspect list → `Read` each candidate → `Grep` for the symbol.
- **Good:** `Grep(pattern: "useAuth|auth\\.uid", glob: "src/**/*.{ts,tsx}", output_mode: "content")`.

Three round-trips collapse into one. The savings compound on every exploratory question.

### 2. Batch edits in a single turn

Identify every file that needs changing from your initial read, then emit all `Edit` calls in one assistant turn. No interleaved reads, no "let me think" between edits.

- **Bad:** Edit A → narrate → Edit B → narrate → Edit C.
- **Good:** One assistant message containing Edit A + Edit B + Edit C as parallel tool calls.

If Edit B's `old_string` depends on the result of Edit A, they can't be parallel — but that's the exception, not the rule.

### 3. Parallelize independent tool calls in the same turn

Any two Reads, Greps, Bashes, or WebFetches that don't depend on each other go in one tool-call block. Serial chains waste turns, roundtrip latency, AND the cache-warm window.

**Default rule:** if two tool calls could run in parallel, they must, unless you need call A's output to construct call B's input.

### 4. Entry-point-first exploration — don't slurp files

Before reading any file body:
1. Search filename patterns (`*.config.*`, `main.*`, `index.*`, `schema.*`).
2. Search imports with a content regex to map the architecture (`^import|^from .* import`).
3. Only then read the specific files that matter — and only the relevant range (see #5).

Reading a 2000-line file hoping to stumble on the answer is the #1 token bleed in typical sessions. Context helps only after you've found the right starting point.

### 5. Targeted line ranges, not whole files

When you know the symbol is near line N, use `Read(file_path, offset: N-20, limit: 40)`, not the whole file. When a search tool supports range syntax (`foo.ts#100-200`), use it.

**Exception:** read the whole file when you're about to materially rewrite it — false economy to reread it three times during one refactor.

### 6. Don't re-read unchanged files

If a file is already in your context and hasn't been edited since you read it, don't read it again. Trust the context. When you must verify, check `git status` or file mtime — cheaper than a full re-read.

### 7. Delegate exploration to cheap subagents

For open-ended codebase questions ("how does X work?", "find everything that touches Y"), dispatch a haiku-model subagent via the `Agent` tool with:

- A tight tool-call budget (3–5, stated explicitly in the prompt).
- **"Return results immediately after the tool call that found them. Do NOT emit commentary between tool calls."**
- A read-only tool allowlist (Grep, Glob, Read — no Edit, Write).
- A specific question, not a research mandate.
- A report word-count cap ("under 200 words").

Haiku is ~10–20× cheaper than Opus for tool-driven exploration. Every explored file that never enters your main-thread context is pure savings.

### 8. Introspect the live DB — don't read `schemas/` or `migrations/`

If the task is "does column X exist?" or "what tables reference Y?", query the live DB's information schema (`\d+ tablename` via psql, or a DB MCP's table-introspection action). Reading the full migrations history to reconstruct schema costs 10–100× more tokens and is often wrong (migrations can be reverted, renamed, or stacked).

### 9. Response-shape minimalism

After a tool call, don't re-document what the tool already showed. After an edit, one sentence — *"Updated `auth.ts` to normalize email casing."* — is enough. Skip:

- "What stands out" sections.
- Follow-up-question menus ("Would you like me to...?").
- Recapping code you just wrote.
- Restating the user's request back at them.

The user reads the diff. You explain decisions that aren't visible in the diff.

### 10. Inject discipline into subagent prompts

When you dispatch a subagent, paste this verbatim into the prompt:

> Return results immediately after the tool call that found them. Do NOT emit commentary between tool calls. Report under [N] words. If you can't answer with the budget given, say so in one sentence — don't speculate or explore beyond budget.

Subagents inherit none of the orchestrator's discipline unless you tell them. A 300-word rambling subagent report costs more than the search that produced it.

### 11. Compress prose in always-loaded context files

`CLAUDE.md`, memory indexes, and rule files load on every session start — their token cost multiplies by session count. Rewrite prose sections densely *once*; the payoff compounds across every future read. A well-compressed `CLAUDE.md` is 30–50% smaller with zero semantic loss.

**Compress:** paragraphs that hedge or restate, filler adverbs (`just`, `really`, `basically`, `essentially`), pleasantries ("please remember", "as a general rule"), multi-sentence rules that collapse to one line with a `Why:` / `How:` tail.

**Never touch (lossless-only zones):** code blocks, commands, file paths, URLs, regex, exact identifiers, dates, version numbers, CVE/ticket IDs, config keys, headings (navigation anchors), or quoted user instructions (rewording changes the rule).

**Workflow:**
1. Keep an editable original alongside the compressed file: `CLAUDE.md` = agent-read (compressed), `CLAUDE.original.md` = human-edit (readable). Edit the original, regenerate the compressed copy.
2. Recompress when the original changes materially.
3. Measure with `wc -w` before/after. Target 30–50% reduction on prose-heavy files. Under 20% means it was already tight — leave it.

**Skip if:** the file is mostly code/commands (no prose to squeeze), precision loss risks a bug (legal text, step-by-step setup where ambiguity breaks), or the file loads rarely (ROI comes from load frequency).

**Keep it professional, not stylized.** The goal is *dense prose*, not *telegraphic shorthand* — a reader unfamiliar with the compression should still parse it on first read.

## How to apply in a session

1. **At session start** for a read-heavy task, mentally flag patterns 1, 3, 4, 5.
2. **Before dispatching a subagent**, apply 7 + 10.
3. **Mid-session, if token usage spikes**, check against this list. The usual offenders: #1 (Glob then Read), #3 (serial when parallel was possible), #9 (verbose narration).
4. **When the answer is in a DB**, reach for #8 before opening a single migration file.
5. **Once per project** (not per session), apply #11 to `CLAUDE.md` and other always-loaded files. One-time prep, compounds forever.

## What NOT to do

Don't apply this skill at the expense of correctness. Saving 500 tokens by reading lines 100–140 when the bug is on line 95 is a false economy that costs you a second round-trip AND a wrong fix.

If a pattern above would make you miss the actual answer, widen the search. The goal is not fewer tokens — the goal is fewer **wasted** tokens.

---
name: token-economy
description: "Tool-call-level discipline for minimizing session token burn without sacrificing correctness. Use at the start of a cost-constrained session, on heavy mid-session burn (file-slurping, serial searches, verbose narration), before /compact or handoff, or when briefing a subagent on efficient tool use. Teaches combine-discover-and-read, batched edits, parallelized searches, entry-point-first exploration, targeted line ranges, cheap-subagent delegation, DB introspection over schema-file reads, dense-prose compression of always-loaded context files, and preserve-vs-drop compaction categories. NOT for production LLM API spend (use llm-cost-optimizer), choosing which files the agent sees (use context-engineering), or claude-flow Phase 2 exploration (use smart-exploration)."
---

# Token Economy

Tactical, per-tool-call discipline for keeping a coding session's token burn low without sacrificing correctness. Patterns distilled from the WithWoz/wozcode-plugin agent-prompt conventions — specifically the half that transfers to orthodox Claude Code tools (Read, Grep, Glob, Edit, Bash, Agent) with no custom MCP required. See the repo-root `NOTICE.md` for attribution.

## When to use

- Starting a new coding session with explicit cost or context-window constraints.
- Noticing token usage spike mid-session (whole-file reads for a 10-line answer, serial independent searches, verbose tool-call narration).
- Before dispatching a subagent — inject the relevant rules into the subagent's prompt.
- Handing off long-running tasks (debugging, refactors, audits) where small wastes compound.

**Skip on trivial/tiny tasks.** The discipline has a fixed overhead that only amortizes over enough tool calls: in a 2026-07-18 SkillsBench A/B, the with-skill arm used ~70% MORE tokens than baseline on a small single-lookup task (recorded: henry ledger #160). Apply above a rough task-size floor — multi-step or long-session work — not universally.

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

### 7.5 Skip subagent dispatch when the controller already has the full spec

`subagent-driven-development` defaults to dispatching even content-write tasks (markdown reference files, doc pages) to per-task subagents. When the orchestrator already holds the full spec for all N files in its current context — and the writes are sequential markdown with no independent exploration needed — the per-subagent briefing tokens exceed the savings, and there's no parallelism gain (each subagent re-pays the spec cost).

- **Dispatch when:** files need independent exploration, the spec is large enough you'd re-paste it per subagent, or writes can genuinely parallelize on distinct surfaces (e.g. tests in unrelated modules).
- **Stay main-thread when:** the controller drafted the spec this turn, files are pure content (no code execution), and writes are batchable as parallel `Write` calls in one assistant turn (see #2).

Validated 2026-05-28 building [`sme-voice`](../sme-voice/SKILL.md): 4 reference markdown files written main-thread from the in-context plan; dispatching 4 subagents would have re-paid ~2K briefing tokens each for zero parallelism gain.

### 7.6 Combine spec + quality review in one dispatch for tightly-spec'd phases

When a phase's tasks are individually small (≤50 LoC each) AND the spec is concrete (test bodies given verbatim), dispatch ONE reviewer subagent that does BOTH passes — spec-compliance first, then code-quality — in clearly separated sections of one prompt. Reviewer re-pays the diff-read cost once instead of twice. Stay split when reviews need distinct viewpoints (e.g. security vs perf) or when spec divergence is a likely outcome that should short-circuit the quality pass.

Validated 2026-06-02 on [claude-skills PR #149](https://github.com/sumrae412/claude-skills/pull/149) `off-market` Phase 2 (5 signal modules, ~50 LoC each, test bodies in the brief verbatim) — saved ~40% on reviewer tokens vs split, caught the same leap-year off-by-one bug.

### 7.7 Surgical fixup dispatch BETWEEN phases prevents compounded broken state

When live-smoke surfaces a phase-N bug whose fix is one file + one signal, dispatch a focused fixup BEFORE moving to phase N+1. Bundling the fix into the next phase's PR loses bisect-ability and the fix dies in review noise. Pattern: one fix → one commit → one re-run → next phase. The fixup's brief is ~½ a normal phase brief (just the bug + verification command), and the cost beats discovering N+1 was built on a broken N.

Validated 2026-06-02 on [claude-skills PR #149](https://github.com/sumrae412/claude-skills/pull/149) `off-market` — WPRDC server-side zip pushdown + comma-before-zip regex fixup between Phase 6 and Phase 7 took candidates surfaced from 0 to 4 on real 15217 data.

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

### 12. Preserve high-signal categories during compaction / handoff

When context shrinks — `/compact`, session handoff, summarizing for a fresh session, or briefing a subagent on prior work — some categories carry irreplaceable signal and others carry bulk that can be dropped without loss.

**Preserve verbatim** (don't summarize away):
- Skill outputs (a skill's resolved guidance — re-deriving costs another invocation).
- TodoWrite state (current task list and statuses).
- Write / Edit results (the actual change that landed; the diff is the truth).
- Plan content (decisions already made — paraphrasing risks drift).
- The user's literal instructions and explicit corrections.

**Drop first** (high bulk, low residual signal):
- **Errored tool inputs** — keep the error message, drop the input payload. A 10K-line file that failed to parse: the error tells you what went wrong; the file body adds nothing once you know the call failed. Same for failed Bash output, failed migrations, failed API calls.
- Stale file reads of files you've since edited (the post-edit state is what matters).
- Verbose tool narration ("I'm going to read X, then Y, then…").
- Duplicated tool calls — if you ran the same Grep twice with the same args, only the latest output matters.

**Why:** compression decisions made under pressure default to "summarize everything proportionally," which is the wrong shape — high-signal items get diluted and bulk items get retained at lower density. Pre-decide the categories.

## How to apply in a session

1. **At session start** for a read-heavy task, mentally flag patterns 1, 3, 4, 5.
2. **Before dispatching a subagent**, apply 7 + 10.
3. **Mid-session, if token usage spikes**, check against this list. The usual offenders: #1 (Glob then Read), #3 (serial when parallel was possible), #9 (verbose narration).
4. **When the answer is in a DB**, reach for #8 before opening a single migration file.
5. **Once per project** (not per session), apply #11 to `CLAUDE.md` and other always-loaded files. One-time prep, compounds forever.
6. **Before `/compact` or session handoff**, apply #12: pre-decide what's preserved (skills, todos, edits, plans, user instructions) vs dropped first (errored tool inputs, stale reads, verbose narration).

## What NOT to do

Don't apply this skill at the expense of correctness. Saving 500 tokens by reading lines 100–140 when the bug is on line 95 is a false economy that costs you a second round-trip AND a wrong fix.

If a pattern above would make you miss the actual answer, widen the search. The goal is not fewer tokens — the goal is fewer **wasted** tokens.

## External tools

See [`references/external-tools.md`](references/external-tools.md) for external infrastructure that automates patterns from this skill (e.g., `rtk-ai/rtk` operationalizes Pattern 9 for CLI output).

## Built-in tool cost notes

A few harness tools have invocation costs worth knowing about, since they don't show in the patterns list but compound across a session:

- **`Skill` tool re-emits the full skills list** as a system reminder on each invocation. The reminder block can be 5–10K tokens depending on the installed plugin set. Invoke `Skill` deliberately for a known target — don't probe-fire it to see what's available. When you're unsure which skill fits, invoke `skill-discovery` once and act on its output rather than calling `Skill` multiple times with guesses.
- **Background `Agent` dispatches with `run_in_background: true`** keep the subagent's full JSONL transcript in a temp file the harness warns you not to `cat`. The completion notification carries the agent's final summary — that's the canonical record; don't try to re-read the transcript for "more detail."
- **`AskUserQuestion`** is cheap on the user's end but each call breaks model flow. Batch related questions into one call (up to 4 questions) rather than firing sequentially.
- **Idle MCP servers tax every message.** Each connected MCP server loads its full tool definitions into context on *every* message, used or not — one server can add ~17,600 tokens/message (Cursor-measured — a different harness than Claude Code, so the absolute number is illustrative-of-mechanism, not a Claude Code measurement; [source](https://medium.com/@grvharariya/cursor-token-optimization-a-data-driven-investigation-176ae06bb247)). Disable MCP servers you aren't using this session. The same study found ~97.9% of a typical request was context and only ~2.1% was the generated answer — context, not generation, is where the budget goes.
- **Subagent fan-out costs ~7–10× a single-agent session** (same source) — an *architecture* cost separate from per-model price (each subagent re-pays its briefing + tool-discovery context). Fan out only when the work genuinely parallelizes or needs isolation, not as a reflex.

# SOURCE.md — model-router

Principles and structural patterns distilled from these sources. No verbatim code or proprietary phrasing was copied; ideas are not copyrightable per 17 U.S.C. § 102(b). Per memory `external_skill_distillation_principles_only.md`, attribution is by principle, not by line.

## musistudio/claude-code-router (MIT, 34K★)

URL: https://github.com/musistudio/claude-code-router

**Principles lifted:**
- Named routing scenarios (default / background / think / longContext / webSearch) as the primary classification axis, in preference to a single complexity score
- `longContextThreshold` concept — explicit context-size cutoff that overrides other classification
- Subagent-routing tag pattern (their `<CCR-SUBAGENT-MODEL>`) — adapted into our "specify `model:` per-subagent" recommendation
- Fallback chain concept — primary model fails → recommend a backup tier
- Project-level default override pattern — adapted into our CLAUDE.md pattern

**Deliberately left behind:** proxy/daemon infrastructure (`ccr code`, `ccr ui`, `ccr restart`), multi-provider routing (DeepSeek, Gemini, OpenRouter, Ollama, GLM), transformer system, tiktoken counting, custom JS router file format, preset export/import, `.env` and API-key management.

## AURA FROG model-router spec (user-provided)

**Principles lifted:**
- 4-tier complexity classification (trivial / simple / complex / architectural) — separates "simple bug fix" from "multi-file new feature" even when both → Sonnet
- Weighted-signal scoring with sum-threshold tier assignment
- Override rules table (explicit user request, security, production deployment)
- Context modifiers as a second-pass adjustment layer
- Output card single-line format with 🎯 marker

**Deliberately left behind:** AURA FROG branding/banner, agent-detector integration, metrics-tracking infrastructure, references to AURA-specific files and agent names.

## buildtolaunch substack — "Claude Code Token Optimization"

URL: https://buildtolaunch.substack.com/p/claude-code-token-optimization

**Principles lifted:**
- Verbatim Haiku/Sonnet/Opus tier phrasings (mechanical / implementation + daily work / architecture + complex)
- Cost ratio anchor: Haiku cheaper than Opus by a meaningful multiple (article quoted ~5× input, but actual ratio under current Anthropic pricing is closer to ~15× input — SKILL.md uses the current 15× figure; article anchored the *concept* of input-cost stratification, not the exact multiplier)
- Adjacent levers: `/effort low`, `MAX_THINKING_TOKENS=8000`, `/compact` vs `/clear`, CLAUDE.md under 500 tokens

**Deliberately left behind:** `.claudeignore` recipe (belongs in context-engineering), personal cost anecdote, `/compact` vs `/clear` deep dive (belongs in token-economy).

## dev.to/lakshmisravyavedantham — agent-hub skill

URL: https://dev.to/lakshmisravyavedantham/i-built-a-skill-so-claude-automatically-routes-tasks-to-free-tier-ai-providers-1m10

**Principles lifted:**
- Verb-cluster classification pattern (mapping action verbs to task tiers)
- First-match precedence rule for ambiguous classification ("if matches multiple types, use first in table order")
- Output sequencing: status/decision card displays BEFORE the action

**Deliberately left behind:** provider-routing architecture (wrong target — they route Codex / Gemini / MiniMax / Groq, we route Anthropic models), usage.json token-budget tracker, status-bar rendering, infrastructure for API-key management, hard-stop handling.

## danielmiessler/Personal_AI_Infrastructure discussion #714

URL: https://github.com/danielmiessler/Personal_AI_Infrastructure/discussions/714

**Principles lifted:**
- Agent-role-based default tiers (Explore → Haiku, Engineer/Research → Sonnet, Architect → Opus, Council → tiered)
- Quality-floor rule: "Red Team specifically needs Sonnet or better — Haiku produces shallow critiques"
- Sharper cost split: Opus OUTPUT cost ~5× Sonnet (matters for long-output tasks like doc writing)

**Deliberately left behind:** CapabilityRecommender hook idea (out of scope for advisory skill), DORA/PAI tooling references, SKILL.md restructuring technique (already covered by progressive-disclosure pattern in CLAUDE.md).

## Claude Code official docs (verified via code.claude.com/docs)

URL: https://code.claude.com/docs/en/slash-commands

**Principles lifted:**
- Skill `model:` frontmatter field — pin a model per-skill; "Accepts the same values as `/model`, or `inherit` to keep the active model"
- Skill `effort:` frontmatter field — `low` / `medium` / `high` / `xhigh` / `max`; available levels depend on model
- `${CLAUDE_EFFORT}` substitution variable for in-skill adaptation
- Auto-compaction behavior on long sessions (informs the long-context threshold rationale)

These are the canonical first-party mechanisms; the skill recommends them in the Adjacent Levers section as the verified path for skill-level pinning.

## `/model opusplan` — initial verification miss, then confirmed

URL: https://www.mindstudio.ai/blog/save-tokens-claude-code-opus-plan-mode (user-shared, May 2026)

**Original claim:** MindStudio article referred to the command as `/model opus-plan` (hyphenated). I searched for that spelling against `code.claude.com/docs/en/slash-commands` and did not find it; flagged as unverified and did not propagate.

**Resolution:** User provided a screenshot showing the actual command is `/model opusplan` (one word, no hyphen). The interactive picker labels it **"Use Opus in plan mode, Sonnet otherwise."** Keyboard shortcuts to open the picker: **Option+P** (Mac), **Alt+P** (Windows).

**Outcome:** The command IS a real first-party Claude Code feature. The verification miss was a spelling miss — `opus-plan` vs `opusplan`. Now propagated as the canonical implementation of the Executor/Advisor pattern in the Plan-Mode Pattern section of SKILL.md.

**Lesson for future verification:** when a third-party article cites a command name, try both hyphenated and unhyphenated spellings (and concatenated, e.g. `opus_plan`, `opusPlan`) against official docs before flagging as unverified. The negative-result search needs to cover spelling variants of the same name.

## MindStudio "Karpathy LLM Wiki Pattern" and "18 Token Management Hacks"

URLs:
- https://www.mindstudio.ai/blog/karpathy-llm-wiki-pattern-cut-claude-token-usage-95-percent
- https://www.mindstudio.ai/blog/claude-code-token-management-hacks

**Verdict:** Wrong surface for this skill. The wiki pattern is a knowledge-base structure (`raw/` + `wiki/` + `index.md`) that belongs in `context-engineering` or `rag-architect`. The 18 hacks are all tool-call and context discipline patterns that belong in `token-economy`. Neither addresses model selection.

**Action:** No principles lifted. Documented here for trace-back so a future maintainer doesn't re-evaluate the same sources.

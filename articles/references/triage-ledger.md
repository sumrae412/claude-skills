# /articles triage ledger

One line per triaged item, appended at the end of every run (step 5). Checked at the top of step 2 — a title or canonical-URL match here means "already triaged": report the prior verdict in one line, archive the note, do NOT re-fetch or re-triage.

Why this exists: the same piece routinely gets captured twice (two newsletters, two weeks apart, different tracking redirects). Without a ledger, the second capture pays full triage cost — including a transcript pull for a video already transcribed — to reach the verdict we already had.

**Matching rules**
- Match on canonical URL first (exact), then on normalized title (lowercased, punctuation stripped) — a redirect URL never matches anything, so title is the workhorse for body-less captures.
- A match is a stop, not a hint: emit `**Already triaged** YYYY-MM-DD as <verdict> — <one-line why>`, add the note to the archive batch, move on.
- If the new capture plainly supersedes the old (the first was title-only, this one carries a full body), re-triage anyway and append a second ledger line noting the upgrade. Say so in the article's section.

**Format**

`- YYYY-MM-DD | <verdict> | <title> | <canonical URL or note_id>`

Verdict is one of `high-value`, `some-value`, `skip`. Append repeats and skips too — a skip that isn't recorded gets re-triaged forever, which is the exact cost this file removes.

<!-- entries below -->
- 2026-07-29 | some-value | How to Evaluate an LLM Feature (4-part course) | 32650cca-a80d-4956-bceb-f7c94da411f4
- 2026-07-29 | high-value | Agent Memory — usage-reinforced decay engine (Ebbinghaus) | ca580404-24b0-4329-9ebc-789c4816becb
- 2026-07-29 | high-value | Agentic Patterns — three-layer memory + LangGraph | 8a8090db-dfaa-4c14-bece-d84905dad713
- 2026-07-29 | high-value | DeepTutor — agent-native learning workspace (L1/L2/L3 memory) | 5154f737-be00-4b03-91a3-6203047bbe6a
- 2026-07-29 | high-value | Ryan Carson — managing 5-10 parallel agents (agent factory) | 04b786b9-36c3-430c-ab31-a42076e31d66
- 2026-07-29 | high-value | Parallel Code — multi-agent via git worktrees | 1c8a7f6f-eaa6-4eca-a88f-216e856fc998
- 2026-07-29 | high-value | Solo agency with Claude Code (Ronin blueprint) | cbc3b7ca-96e4-488a-918b-b39ea2a930fc
- 2026-07-29 | high-value | Claude Code Loops (/goal, /loop patterns) | 1dccb909-bbea-411d-8eeb-1b83a23a65e3
- 2026-07-29 | high-value | Long-running autonomous coding agents (24h+ auto-permissions) | 84d0e111-a2a5-4d4d-ba4f-3798bedbd0f9
- 2026-07-29 | high-value | RAPTOR — autonomous vulnerability hunting (gen-judge-verify) | 89adc7aa-8501-4795-80f2-baa102d17d98
- 2026-07-29 | high-value | Self-improving agents with Codex & production traces | be3bf035-7733-4a57-8109-d6506aa304e8
- 2026-07-29 | high-value | Massive parallel QA workflow (Codex/Sol, 12 subagents) | 073240a5-d441-4832-a277-fc74f0ac31c5
- 2026-07-29 | high-value | Company Brain — knowledge base for coding agents | d0c5c885-e59b-4ea6-8693-6835be0f0da6
- 2026-07-29 | high-value | Code Review Standards (10-point checklist + risk-lane) | 485b2790-2158-4426-905d-84c8a7dcaa6a
- 2026-07-29 | high-value | Anthropic SDLC Security — multi-agent review, closed-loop security | 4e2a8174-a0fe-4afe-92ad-7f2f6f199583
- 2026-07-29 | high-value | Context Engineering for Claude 5 — progressive disclosure | c5684415-af86-4c4e-a5de-fc04b374361b
- 2026-07-29 | high-value | Graph Engineering — parallel agent workflows (graphs > chains) | e577451b-51b3-40b5-bb88-82e4b4a1176b
- 2026-07-29 | high-value | Agentic Workflows — one-person business, Rulings Note pattern | aecfbe1c-c055-45d1-9cae-37e85f669495
- 2026-07-29 | high-value | DESIGN.md — AI-readable design systems (Refero, 2000+ patterns) | b02c798e-a437-4865-8782-df077591ed59
- 2026-07-29 | high-value | crowdmind — persona panels + MCP server | 76800379-e17c-4b64-b67b-c4c7e7066fc6
- 2026-07-29 | high-value | Foglamp — open-source telemetry for Vercel AI SDK (costs/traces) | 539e133d-87f0-4998-8688-3f1b2e8a9eda
- 2026-07-29 | high-value | Tolaria — AI-first knowledge management (AGENTS file patterns) | da4b668f-18b1-4dc9-876f-8fe714ea2590
- 2026-07-29 | some-value | Cognee — open-source AI memory platform | 59acdfcc-4bfe-450c-b4e1-1831f63ba715
- 2026-07-29 | some-value | AI agents owning land via DAO/LLC (BetterBurgh) | 3224239b-b37a-477e-9ca5-dad2764cac1d
- 2026-07-29 | some-value | Agent skills for UI/UX reviews (quick/full mode) | 77ddb6fd-4c70-4117-b02f-aa0106d7202b
- 2026-07-29 | some-value | NVIDIA Nemotron 3 Ultra & LangChain — harness tuning | ca9013e5-28e3-4f2c-a6fc-849a93ad7827
- 2026-07-29 | some-value | you.bot — multi-model API aggregator (cost savings) | 3a0cf988-7a6e-4844-9b21-f619969a4a9c
- 2026-07-29 | some-value | Celeris — diffusion-based inference (15x faster) | 29436c28-adf3-4197-a6b9-0ab064760e9c
- 2026-07-29 | some-value | Inkling — open-weights MoE model with controllable reasoning | 1103f4ee-fb49-4601-802a-ab3302b2870b
- 2026-07-29 | some-value | Agentic RL (RLVR/GRPO) — evals reference | 96da6854-acd1-48c7-95d4-bc9e1be5e0f6
- 2026-07-29 | some-value | Swamp Workflows — deterministic coordination > agentic loops | 6824d6fe-3cc2-4cbd-a293-45f45fccc75a
- 2026-07-29 | some-value | Company Brain — three-layer memory model | e113cf23-eac7-42a8-95d0-7dd1a2c3cfbd
- 2026-07-29 | some-value | Flint — visualization language (MCP server pattern) | 22f1bf7c-2a73-4098-81f6-fff9adf68f4d
- 2026-07-29 | some-value | Renting is stressful (a16z) — CourierFlow market context | 8249f2a0-83fc-4e2f-9000-e412aec54659
- 2026-07-29 | some-value | Safe Database Rollback — CourierFlow migration reference | ba6cc2e3-abf8-4efd-8bc2-4e8e24cc4c9a
- 2026-07-29 | some-value | Clean Code Cookbook — AI coding tips validation | 5d2c7c89-3423-4f6e-a366-e15212da3940
- 2026-07-29 | skip | 40 personal/meeting/non-technical notes (speech therapy, meetings, personal docs) | batch
- 2026-07-29 | skip | 7 notes not found in Mem API (evals/security titles may be deleted) | batch
- 2026-07-29 | skip | 14 low-relevance article notes (Flue, OS model, agent-run companies, etc.) | batch

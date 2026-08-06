---
name: llm-cost-optimizer
description: "Use when you need to reduce LLM API spend, control token usage, route between models by cost/quality, implement prompt caching, or build cost observability for AI features. Triggers: 'my AI costs are too high', 'optimize token usage', 'which model should I use', 'LLM spend is out of control', 'implement prompt caching'. NOT for RAG pipeline design (use rag-architect)."
---

# LLM Cost Optimizer

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad exploration, repeated file reads, multi-file scans, or heavy reference loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant patterns inline instead of loading extra material.


> Originally contributed by [chad848](https://github.com/chad848) — enhanced and integrated by the claude-skills team.

You are an expert in LLM cost engineering with deep experience reducing AI API spend at scale. Your goal is to cut LLM costs by 40-80% without degrading user-facing quality -- using model routing, caching, prompt compression, and observability to make every token count.

AI API costs are engineering costs. Treat them like database query costs: measure first, optimize second, monitor always.

## Measure ROT, Not Just Cost

Return on Tokens: `ROT = (Value of Output − Cost of Tokens) / Cost of Tokens × 100`. Cost-side optimization (everything below) only matters relative to the value the tokens produce — a feature with negative ROT should be redesigned or cut, not just made cheaper. During a cost audit, estimate value per feature (revenue attribution, time saved, tickets deflected) alongside spend so the top optimization targets rank by ROT, not raw spend. Source: [Return on Tokens (ROT), Not Boring, 2026-06](https://www.notboring.co/p/return-on-tokens-rot).

**Compile-to-deterministic-code pattern:** for repetitive, high-accuracy work, the highest-ROT move is often eliminating the per-request LLM call entirely — use the LLM once to learn the rule, then refactor it into deterministic code that runs free and only changes when the world changes. Agents improvise; that's the wrong runtime for work that needs consistent quality at volume. Worked example: [courierflow_beta PR #140](https://github.com/sumrae412/courierflow_beta/pull/140) — a regex grader superseded an LLM judge once the spec collapsed to a single verifiable clause (1.00 on 10 calibration items, zero recurring judge spend).

## Keep Costs Flat While Usage Grows (policy posture)

When usage is growing, the goal is flat spend through infrastructure, not usage
caps. Five levers, in the order Coinbase reported applying them at scale
(Brian Armstrong, X, 2026-06): (1) cheaper open-weight defaults for
non-judgment traffic (e.g. GLM/Kimi tiers — matches the eval-iteration tier
pattern below); (2) prompt-preprocessing routing (see `model-router`);
(3) cache-aware request shaping — their reported cache-hit move was 5%→60%;
(4) lean context + disconnecting unused tools per request; (5) **visibility
over suppression** — tie spend to feature-level impact (the ROT framing above)
and alert on anomalies, rather than hard-capping users. Suppression hides
demand signal; visibility converts it into routing decisions.

## Before Starting

**Check for context first:** If project-context.md exists, read it before asking questions. Pull the tech stack, architecture, and AI feature details already there.

Gather this context (ask in one shot):

### 1. Current State
- Which LLM providers and models are you using today?
- What is your monthly spend? Which features/endpoints drive it?
- Do you have token usage logging? Cost-per-request visibility?

### 2. Goals
- Target cost reduction? (e.g., "cut spend by 50%", "stay under $X/month")
- Latency constraints? (caching and routing tradeoffs)
- Quality floor? (what degradation is acceptable?)

### 3. Workload Profile
- Request volume and distribution (p50, p95, p99 token counts)?
- Repeated/similar prompts? (caching potential)
- Mix of task types? (classification vs. generation vs. reasoning)

## How This Skill Works

### Mode 1: Cost Audit
You have spend but no clear picture of where it goes. Instrument, measure, and identify the top cost drivers before touching a single prompt.

### Mode 2: Optimize Existing System
Cost drivers are known. Apply targeted techniques: model routing, caching, compression, batching. Measure impact of each change.

### Mode 3: Design Cost-Efficient Architecture
Building new AI features. Design cost controls in from the start -- budget envelopes, routing logic, caching strategy, and cost alerts before launch.

---

## Mode 1: Cost Audit

**Step 1 -- Instrument Every Request**

Log per-request: model, input tokens, output tokens, latency, endpoint/feature, user segment, cost (calculated).

Build a per-request cost breakdown from your logs: group by feature, model, and token count to identify top spend drivers.

**Step 2 -- Find the 20% Causing 80% of Spend**

Sort by: feature x model x token count. Usually 2-3 endpoints drive the majority of cost. Target those first.

**Step 3 -- Classify Requests by Complexity**

| Complexity | Characteristics | Right Model Tier |
|---|---|---|
| Simple | Classification, extraction, yes/no, short output | Small (Haiku, GPT-5-mini, Gemini Flash) |
| Medium | Summarization, structured output, moderate reasoning | Mid (Sonnet, GPT-5) |
| Complex | Multi-step reasoning, code gen, long context | Large (Opus, Fable, GPT-5, o3) |

---

## Mode 2: Optimize Existing System

Apply techniques in this order (highest ROI first):

### 1. Model Routing (typically 60-80% cost reduction on routed traffic)

Route by task complexity, not by default. Use a lightweight classifier or rule engine.

For the executor+advisor pairing pattern (cheap model executes, stronger model advises mid-generation via Anthropic's beta advisor tool) — see [`model-router`'s Advisor Tool section](../model-router/SKILL.md#advisor-tool-executoradvisor-pairing).

Decision framework:
- **Use small models** for: classification, extraction, simple Q&A, formatting, short summaries
- **Use mid models** for: structured output, moderate summarization, code completion
- **Use large models** for: complex reasoning, long-context analysis, agentic tasks, code generation

### 2. Prompt Caching (40-90% reduction on cacheable traffic)

Supported by: Anthropic (cache_control), OpenAI (prompt caching, automatic on some models), Google (context caching).

Cache-eligible content: system prompts, static context, document chunks, few-shot examples.

Cache hit rates to target: >60% for document Q&A, >40% for chatbots with static system prompts.

**Anthropic `cache_control` minimum:** Writes silently no-op if the cached block is under 1024 tokens (Sonnet/Opus) / 2048 (Haiku). This minimum is NOT surfaced in the top-level caching guide — you'll see `cache_creation=0, cache_read=0` in usage and no error. Before wiring caching, measure your system prompt + cached context with a tokenizer; if under the threshold, either inline more static context into the cached block or skip caching entirely.

**Pre-flight checklist:** (1) Token-count the candidate cache block. (2) Run one live call and assert `usage.cache_creation_input_tokens > 0`. (3) Run a second call and assert `usage.cache_read_input_tokens > 0`. Unit tests cannot verify this — only live traffic shows cache fields populated.

**Tool-use wrinkle:** With beta tool schemas (e.g. advisor-tool), each call may write a fresh cache instead of reading a prior one — verify `cache_read > 0` across consecutive calls, not just `cache_creation > 0` on the first.

**Breakpoint placement depends on which client library owns the call — check FIRST.** On raw Anthropic Messages API calls you build yourself: one breakpoint on the LAST block of the stable prefix caches everything before it (a marker on `system` covers tools+system), so avoid redundant double markers. On the Vercel AI SDK path (`@ai-sdk/anthropic` via `wrapLanguageModel`/`streamText`/`generateText`): `cache_control` is read independently per block — tools via `prepareTools()`, system via `convertToAnthropicMessagesPrompt()`'s `case "system"` — so a tools-only marker leaves `system` uncached on every call with NO error (looks wired, isn't). There you need TWO breakpoints: one on the last tool, one on the system message's `providerOptions.anthropic.cacheControl`. Validated 2026-07-02 on courierflow_beta: [PR #564](https://github.com/sumrae412/courierflow_beta/pull/564) applied the raw-API guidance on an AI-SDK path, leaving a ~21.7K-token system prompt uncached; [PR #567](https://github.com/sumrae412/courierflow_beta/pull/567) traced the vendor source and added the second breakpoint. Pair with a `--validate-cache` preflight CLI (mirror the `--validate-grader` pattern from deterministic-grader work): 2 probe calls asserting `cache_creation > 0` then `cache_read > 0`, exit non-zero on miss — catches the 4 silent-fail modes (under-minimum block, SDK wrapper strip, missing `anthropic-beta` header, per-call payload variability) that all produce `cache_creation=0` with NO error. **How to apply:** any eval/agent loop resending a ≥1K-token stable prefix every call gets caching + preflight + per-call telemetry logging (`cache_creation_input_tokens` / `cache_read_input_tokens` → `cacheHitRate` + `estimatedSavingsUsd` rollup) in the SAME PR — "wired" and "working" are different claims. Validated 2026-05-30 on [courierflow_beta PR #147](https://github.com/sumrae412/courierflow_beta/pull/147) (~80% Layer B nightly cost cut from ~$8.46/run baseline).

### 3. Output Length Control (20-40% reduction)

LLMs over-generate by default. Force conciseness:

- Explicit length instructions: "Respond in 3 sentences or fewer."
- Schema-constrained output: JSON with defined fields beats free-text
- max_tokens hard caps: Set per-endpoint, not globally
- Stop sequences: Define terminators for list/structured outputs

### 4. Prompt Compression (15-30% input token reduction)

Remove filler without losing meaning. Audit each prompt for token efficiency by comparing instruction length to actual task requirements.

| Before | After |
|---|---|
| "Please carefully analyze the following text and provide..." | "Analyze:" |
| "It is important that you remember to always..." | "Always:" |
| Repeating context already in system prompt | Remove |
| HTML/markdown when plain text works | Strip tags |

### 5. Semantic Caching (30-60% hit rate on repeated queries)

Cache LLM responses keyed by embedding similarity, not exact match. Serve cached responses for semantically equivalent questions.

Tools: GPTCache, LangChain cache, custom Redis + embedding lookup.

Threshold guidance: cosine similarity >0.95 = safe to serve cached response.

### 6. Request Batching (10-25% reduction via amortized overhead)

Batch non-latency-sensitive requests. Process async queues off-peak.

---

## Mode 3: Design Cost-Efficient Architecture

Build these controls in before launch:

**Budget Envelopes** -- per feature, per user tier, per day. Set hard limits and soft alerts at 80% of limit.

**Routing Layer** -- classify then route then call. Never call the large model by default.

**Cost Observability** -- dashboard with: spend by feature, spend by model, cost per active user, week-over-week trend, anomaly alerts.

**Graceful Degradation** -- when budget exceeded: switch to smaller model, return cached response, queue for async processing.

---

## Proactive Triggers

Surface these without being asked:

- **No per-feature cost breakdown** -- You cannot optimize what you cannot see. Instrument logging before any other change.
- **All requests hitting the same model** -- Model monoculture is the #1 overspend pattern. Even 20% routing to a cheaper model cuts spend significantly.
- **System prompt >2,000 tokens sent on every request** -- This is a caching opportunity worth flagging immediately.
- **Output max_tokens not set** -- LLMs pad outputs. Every uncapped endpoint is a cost leak.
- **No cost alerts configured** -- Spend spikes go undetected for days. Set p95 cost-per-request alerts on every AI endpoint.
- **Free tier users consuming same model as paid** -- Tier your model access. Free users do not need the most expensive model.

---

## Output Artifacts

| When you ask for... | You get... |
|---|---|
| Cost audit | Per-feature spend breakdown with top 3 optimization targets and projected savings |
| Model routing design | Routing decision tree with model recommendations per task type and estimated cost delta |
| Caching strategy | Which content to cache, cache key design, expected hit rate, implementation pattern |
| Prompt optimization | Token-by-token audit with compression suggestions and before/after token counts |
| Architecture review | Cost-efficiency scorecard (0-100) with prioritized fixes and projected monthly savings |

---

## Communication

All output follows the structured standard:
- **Bottom line first** -- cost impact before explanation
- **What + Why + How** -- every finding includes all three
- **Actions have owners and deadlines** -- no "consider optimizing..."
- **Confidence tagging** -- verified / medium / assumed

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|---|---|---|
| Using the largest model for every request | 80%+ of requests are simple tasks that a smaller model handles equally well, wasting 5-10x on cost | Implement a routing layer that classifies request complexity and selects the cheapest adequate model |
| Optimizing prompts without measuring first | You cannot know what to optimize without per-feature spend visibility | Instrument token logging and cost-per-request before making any changes |
| Caching by exact string match only | Minor phrasing differences cause cache misses on semantically identical queries | Use embedding-based semantic caching with a cosine similarity threshold |
| Setting a single global max_tokens | Some endpoints need 2000 tokens, others need 50 — a global cap either wastes or truncates | Set max_tokens per endpoint based on measured p95 output length |
| Ignoring system prompt size | A 3000-token system prompt sent on every request is a hidden cost multiplier | Use prompt caching for static system prompts and strip unnecessary instructions |
| Treating cost optimization as a one-time project | Model pricing changes, traffic patterns shift, and new features launch — costs drift | Set up continuous cost monitoring with weekly spend reports and anomaly alerts |
| Compressing prompts to the point of ambiguity | Over-compressed prompts cause the model to hallucinate or produce low-quality output, requiring retries | Compress filler words and redundant context but preserve all task-critical instructions |
| Gating routing-change promotion on cross-provider agreement | Two correctly-functioning providers can disagree 2x on the same input — they emphasize different signals and calibrate severity differently. Agreement measures similarity, not correctness. Empirical 2026-05-20: Anthropic Sonnet 49 findings (13 CRITICAL) vs NVIDIA kimi-k2.6 23 findings (4 CRITICAL) on same PR diff | Build a small hand-labeled gold set (~30-50 representative inputs). Measure baseline accuracy on current provider. Promote candidate provider only if its gold-set accuracy ≥ baseline − 5pp tolerance |
| Synthetic-only A/B before committing to a routing change | Synthetic prompts miss the real call-site framing, prompt-cache shape, and downstream parsing — the actual savings/regression delta only appears on real traffic | If a pr-reviewer-style tool already runs the surface, do a 1-PR A/B in existing infra (~$0.10, <1min wall) as the first eval. Use it to size the calibration gap before designing the gold set |
| Treating peer coding agents (OpenCode, Aider, Cline, Claude Code) as model providers | Coding agents *consume* model APIs — they don't expose one. They have no `complete(messages)` endpoint a router can call. Wrapping a peer agent inside another agent adds latency and constraints without adding capability | If the goal is free-tier model routing, add another model provider (Groq, Together, Cerebras, OpenRouter free models) next to NVIDIA in the router. If the goal is to offload human work, use the peer agent separately — workflow change, not code change |

### Cost gates that meter only one call path are theater

Any `--max-cost-usd` / cost-ceiling flag on an LLM eval or batch runner MUST tally cumulative spend across EVERY API call the run makes — both the system-under-test (SUT) calls and the judge calls. A gate that meters one path while another path bills uncapped reads "$0 used" at the threshold while real spend mounts elsewhere.

**Validated 2026-05-30 on courierflow_beta [PR #157](https://github.com/sumrae412/courierflow_beta/pull/157):** `tools/phoenix/run_evals.py --max-cost-usd` gated the Haiku judge cost only; SUT (Sonnet `/api/eval/chat`) spend was unmetered. Memory-depth replays did ~175 SUT calls/run @ ~$8/run uncapped while the gate said "$0 used." Day's burn: ~$60. Fix landed a combined judge+SUT meter on the same ceiling.

**How to apply:** when adding a cost ceiling to any LLM eval/batch runner, enumerate EVERY `messages.create()` / `complete()` call site — judge, SUT, structured-output, repair retries, multi-sample — and confirm each one adds to the same cumulative tally before the threshold-check fires. If the runner spawns a subprocess (e.g. backend route call), the cost meter needs the subprocess to return its spend back to the runner (header, JSON field, or shared file), not just count requests.

## Reranker caveats

- **Haiku-as-reranker on small candidate sets can degrade ranking.** Validated 2026-04-29 (claude-flow scale experiment): Haiku reranking BM25 top-3 produced more reordering noise than signal vs. raw BM25 ordering. Threshold for rerank to help: candidate set should be large enough that BM25 top-K loses real signal at K (typically K≥10 over a corpus of hundreds).

## Related Skills

- **rag-architect**: Use when designing retrieval pipelines. NOT for cost optimization of the LLM calls within RAG (that is this skill).
- **evals**: Use for regression gates and production sampling. Pairs with this skill — eval gates catch quality regressions when you route to cheaper models.
- **claude-api**: Use when building/tuning Anthropic SDK apps. Pairs with this skill for prompt-cache-aware implementations.
- **brevity**: Complementary at a different layer. `llm-cost-optimizer` audits SDK call patterns (caching, batching, model tier) inside an AI product. `brevity` trims the outer Claude session's output. Use both together: tune SDK calls with this skill, invoke `brevity` on the Claude session iterating on the code.

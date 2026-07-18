---
name: model-router
description: "Pick the optimal Claude model (Haiku / Sonnet / Opus / Fable) for the current task — two-layer router: mode detection (longContext, background, think, subagent-fleet, webSearch, default) plus weighted complexity scoring. Outputs a one-line recommendation card with model, mode, complexity, reasoning, cost anchor, and the `/model` or `claude --model` command. Use at session start, before dispatching parallel subagents (model choice multiplies cost across N agents), when paying Opus prices on mechanical work, or on 'which model should I use'. NOT for production LLM API spend (use llm-cost-optimizer), PR-reviewer mode (use pr-reviewer-mode), or picking skills (use skill-discovery)."
user-invocable: true
allowed-tools: Read, Grep, Glob
---

# Model Router — Pick the Right Claude Model

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad exploration, repeated file reads, multi-file scans, or heavy reference loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant patterns inline instead of loading extra material.


Model choice is the largest single cost lever in Claude Code: Opus ≈ 5× Sonnet ≈ 3× Haiku. Mechanical work on Opus burns budget; architectural work on Haiku produces shallow output that costs more in rework. This skill picks the right tier in under ten seconds using mode detection upstream of complexity scoring.

## When to use

- Starting a new session or switching task class
- Before dispatching N parallel subagents (cost multiplies across the fleet)
- When the active model feels mismatched to the task (Opus on a typo fix, Haiku on architecture)
- When the user explicitly asks ("which model", "use opus", "minimize cost", "thorough")
- When context is approaching the long-context threshold (~60K tokens)

## When NOT to use

- User has already specified a model this turn — respect the choice
- Mid-multi-turn conversation on the same task — maintain model consistency; switching mid-stream loses cached context
- Task is ambiguous — ask one clarifying question first, then route
- For production LLM API spend → use `llm-cost-optimizer`
- For picking PR-reviewer execution mode → use `pr-reviewer-mode`
- For picking which skill or tool to use → use `skill-discovery`
- For session-context strategy (what to load) → use `context-engineering` (strategic) or `token-economy` (tactical)

---

## Decision Algorithm

Routing runs in four steps. Step 0 is a hard pre-check; Steps 1–4 are layered, with first-match precedence at each layer.

### Step 0 — Context-size pre-check (force long-context mode)

If current context exceeds the long-context threshold, jump straight to `longContext` mode and skip the remaining steps. Haiku's quality drops noticeably on long inputs even when the task itself is simple, so context size dominates other classification.

- **`longContextThreshold` default:** 60,000 tokens
- **How to check:** `/context` displays a colored grid of current context-window usage
- Adjustable per project — pin a different threshold in CLAUDE.md if your typical sessions run hotter or cooler

### Step 1 — Mode detection

| Mode | Signals | Recommended model | Notes |
|---|---|---|---|
| `longContext` | context > 60K tokens (check via `/context`) | Sonnet 5 (Opus 4.8 if reasoning-heavy) | Haiku quality drops on long inputs |
| `background` | non-interactive, batch, `--print` flag, scripted, CI | Haiku 4.5 | Speed and throughput matter more than depth |
| `subagent-fleet` | dispatching 2+ parallel agents via Task / Agent tool | per-role (see Subagent Fleet Routing) | Highest-leverage decision — cost multiplies across the fleet; placed before `think` so fleet routing wins for parallel-agent dispatches that also look like thinking tasks |
| `think` | Plan Mode active (via `/plan`, **Shift+Tab**, or Claude auto-detection), "think carefully", architecture work, multi-model debate | Opus 4.8 + adaptive thinking — Fable 5 for the most demanding long-horizon reasoning (2× Opus cost) — or `/model opusplan` for two-model workflow (see Plan-Mode Pattern below) | Reasoning depth justifies the cost |
| `webSearch` | research / web-fetch heavy, `useful-for` triage, `synthesis-brief`, link-chasing | Sonnet 5 | Opus wastes tokens on synthesis steps |
| `default` | everything else | drop to Step 2 |

**First-match precedence:** if a task matches multiple modes, use the first match in table order. `longContext` always wins, then `background`, then `subagent-fleet`, then `think`, then `webSearch`, then `default`. This keeps the router deterministic when signals overlap — a parallel-subagent run that also looks like a thinking task is `subagent-fleet`, because fleet routing decides model per-agent rather than for the orchestrator.

### Step 2 — Complexity scoring (for `default` mode only)

Classify the task into one of four tiers, then route to the corresponding model:

| Tier | What it looks like | Model | Cost (vs Haiku, input/output) |
|---|---|---|---|
| trivial | typo, rename, format, lint, single-file mechanical edit | Haiku 4.5 ($1/$5 per MTok) | 1× |
| simple | bug fix, validation, refactor one function, write a test | Sonnet 5 ($3/$15) | 3× |
| complex | new feature, multi-file change, new API endpoint, migration | Sonnet 5 ($3/$15) | 3× |
| architectural | system design, security audit, major refactor, breaking change | Opus 4.8 ($5/$25) | 5× Haiku / ~1.7× Sonnet |
| frontier | hardest long-horizon agentic runs, deepest multi-constraint reasoning — only when Opus demonstrably falls short | Fable 5 ($10/$50) | 10× Haiku / 2× Opus |

**First-match precedence within tier:** evaluate trivial → simple → complex → architectural. Mixed signals bias toward cheaper models — escalation after the fact is cheaper than over-spend.

**Fast disambiguator — the rubric-gradability test.** When a task sits on the boundary between mechanical and judgment work (the trivial/simple vs. architectural split), ask one question: *could you write a rubric a machine could grade the output against?* If yes — the success criteria are enumerable in advance (matches a spec, passes named tests, follows a fixed format, transforms data to a defined shape) — route to the cheap tier; the work is execution, not judgment. If no — success depends on taste, tradeoff reasoning, or "I'll know it when I see it" — it needs Opus. This mirrors the orchestrator/executor split (Opus decides *what* and grades the result; the cheap tier executes the rubric-gradable steps) and `claude-flow`'s Rule 5 (use the model only for judgment calls; route deterministic transforms to code or the cheap tier). The test is decisive on the ~20% of cases where the tier table is ambiguous — if you're hesitating between Sonnet and Opus, a clean rubric you could hand to a grader is the signal to drop a tier.

**For ambiguous cases, the full weighted-signal table, and worked examples of edge cases, see [`references/signal-scoring.md`](references/signal-scoring.md).** Load it only when the tier isn't obvious from the lookup above (~20% of cases).

### Step 3 — Override rules (force-model, regardless of tier)

Some conditions are non-negotiable. They override any score from Step 2.

| Condition | Force | Reason |
|---|---|---|
| User says "use opus" | Opus | Explicit request |
| User says "use sonnet" | Sonnet | Explicit request |
| User says "use haiku" | Haiku | Explicit request |
| User says "cheap / fast / quick" | Haiku | Cost preference |
| User says "thorough / careful / deep" | Opus | Quality preference |
| Security or vulnerability task | Opus | Safety-critical — undercosting is the wrong failure mode |
| Production deployment, irreversible change | Opus | Risk management — Opus reasoning on the diff before merge is cheap insurance |
| Schema migration, data deletion | Opus | Stakes — wrong call is hard to reverse |

### Step 4 — Context modifiers (±1 tier shift)

After Steps 1–3 land on a tier, apply at most one modifier (the most relevant). Modifiers nudge the tier up or down based on situational context.

| Context | Adjustment | Reason |
|---|---|---|
| Unfamiliar codebase | −1 complexity (escalate one tier) | Need more exploration depth and pattern-matching |
| Well-documented project, established conventions | +1 complexity (down-shift one tier) | Can work faster with less context-loading |
| Critical-path / production code | −1 complexity (escalate one tier) | Need more care; bugs are expensive downstream |
| Test / mock / throwaway code | +1 complexity (down-shift one tier) | Lower stakes; iteration is cheap |
| Long output expected (>4K tokens) | Penalize Opus (output cost ~5× Sonnet) | Output cost dominates total spend; consider Sonnet unless reasoning truly requires Opus |

Modifiers cap at one tier in either direction — don't chain them. The point is a single nudge, not a re-ranking.

---

## Live pricing data (optional upgrade)

The tier tables above hardcode the Claude price ratios. When routing decisions
need cross-provider or up-to-the-day data (a GLM-vs-Haiku eval tier call, a
"cheapest model above quality bar X" question), the **OpenRouter MCP** exposes
live per-provider pricing, latency, and benchmark scores for 400+ models —
query it instead of trusting a stale table. Not installed by default; connect
it only for sessions that genuinely need cross-provider routing, and treat its
benchmark scores as one signal, not the verdict. (Surfaced 2026-07-04 via
/articles triage; static tables remain the default path.)

## Subagent Fleet Routing

**Highest-leverage section.** When dispatching 2+ parallel agents, model choice multiplies across the fleet — a 5-agent Opus dispatch costs 5× more than a 5-agent Sonnet dispatch, and the marginal recall from Opus on file-search tasks is near zero. Conversely, dispatching Haiku reviewers for a security audit is false economy: each one produces shallow critiques and the orchestrator has to redo the work on Opus anyway.

### Role → default tier

| Subagent role | Default tier | Quality floor |
|---|---|---|
| Explorer / file-search / lookup / grep | Haiku 4.5 | — |
| Executor / code-writer / refactor | Sonnet 5 | — |
| Architect / planner / system-design | Opus 4.8 | Sonnet 5 |
| Reviewer / red-team / security-audit / critic | Opus 4.8 | **Sonnet 5 (Haiku banned — produces shallow critiques)** |
| Council / decision / judgment-call | Sonnet routine, Opus high-stakes | Sonnet 5 |
| Research / synthesis / explain | Sonnet 5 | — |

**Dispatch pattern:** specify the model per-subagent in the Agent tool's `model` parameter. The orchestrator's model is independent of the fleet's models — dispatch a Haiku swarm from a Sonnet orchestrator, or an Opus reviewer from a Sonnet orchestrator.

**Quality floor rule:** never go below the floor for that role. Red-team and critique roles fail silently on Haiku — the agent produces grammatical, plausible-looking output that doesn't actually catch the issues you dispatched it to find (Daniel Miessler's PAI observation, validated across multiple agent frameworks). If budget can't cover the floor, the right move is fewer subagents at the right tier, not more subagents at a too-low tier.

**Evidence notes (2026-07):**

- **A pricier high-judgment orchestrator can be net-cheaper when it delegates.** [Joon Lee's Fable-vs-Opus benchmark](https://x.com/joon_h_lee/status/2076714221837173097) (sidekick-enabled runs): Fable 5 + sidekick $1.86/run vs Opus 4.8 + sidekick $2.04 despite ~2× per-token price — 11.5 vs 26.5 lead-model turns, ~1/3 the input tokens (545k vs 1,679k), and the lead made zero code edits in 81% of Fable runs vs 24% of Opus runs. The cost driver is turns + dragged context + what the lead declines to do itself, not the per-token rate. Reported third-party numbers, not internally reproduced — treat as directional support for orchestrator-delegates / executors-write, which this table already encodes.
- **A small fixed tier set is the right shape.** [arXiv:2607.09197](https://arxiv.org/abs/2607.09197) ("When is Routing Meaningful?", abstract verified 2026-07-18): a curated subset of fewer than ten models recovers most available diversity of a large pool, and learned (KNN) routers gain accuracy but collapse in robustness under query perturbation while prompted routing stays stable. This skill's fixed Haiku/Sonnet/Opus/Fable set with prompted, rule-based routing is the robust end of that trade — don't replace it with a learned router.

---

## Advisor Tool (executor+advisor pairing)

Anthropic's advisor tool (beta, header `advisor-tool-2026-03-01`; Claude API + AWS Claude Platform only — not Bedrock/GCP/Foundry) is a routing primitive distinct from subagent fleets and `opusplan`: a cheap **executor** model consults a stronger **advisor** mid-generation. The advisor sees the full transcript server-side and returns plan/course-correction text — near-advisor-quality output at executor generation rates, without a second full model pass. See [Anthropic docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool).

**When to route to it:**

| Situation | Move |
|---|---|
| Sonnet handling a complex task | Add an Opus advisor for a quality lift at similar-or-lower cost than upgrading the executor to Opus outright |
| Haiku needing a step up | Opus advisor beats upgrading the executor tier — cheaper than running Sonnet/Opus end-to-end |

**Pairing rule:** advisor must be ≥ executor capability (API-enforced — invalid pairs 400); valid advisors are Opus 4.8 or 4.7, and an Opus 4.8 executor accepts only an Opus 4.8 advisor.

**Weak fit — don't reach for this:** single-turn Q&A, pass-through model pickers, or any task needing advisor-grade output on every turn (at that point just run the advisor as the executor).

**Cost knobs (tested):**
- `max_tokens: 2048` on the advisor tool definition — ~7× less advisor output vs. no cap, no measured quality loss. Below `1024` truncates guidance (~10% loss).
- A user-message steer line ("Advisor: please keep your guidance under 80 words...") shrinks advisor turns further.
- Advisor-side prompt caching (`{type: ephemeral, ttl: 5m}`) breaks even at ≥3 advisor calls per conversation — don't bother caching below that.
- Sonnet executor at medium effort + Opus advisor ≈ Sonnet-at-default-effort quality, at lower cost than either straight Sonnet-high-effort or straight Opus.

**Billing gotcha:** advisor tokens land in `usage.iterations[]` at advisor rates and are **excluded from top-level usage totals** — any cost-tracking code reading only the top-level `usage` block will silently undercount. Read `iterations[]` explicitly.

**Failure mode:** advisor errors degrade gracefully — the executor continues without advice rather than failing the turn. Don't add manual fallback handling for this; it's built in.

**Budget cap:** to bound advisor calls per conversation, count them client-side. At the cap, remove the advisor tool AND strip prior `advisor_tool_result` blocks from history — leaving stale advisor blocks in context after the tool is removed will error on the next call.

For production cost-observability once this is wired into a shipped feature (not an in-session Claude Code decision), see `llm-cost-optimizer`.

---

## Output Card Format

Print the card BEFORE the model switch is suggested or applied. The user sees the decision and can override before any action is taken — this supports the advisory framing and lets the user redirect mid-stream.

```
🎯 Model: Sonnet 5 │ Mode: default │ Complexity: simple
   Why:       <one line — task class + cost rationale>
   Apply:     /model sonnet     (or:  claude --model claude-sonnet-5)
   Fallback:  <Haiku if Sonnet rate-limited (acceptable for this complexity)>
   Adjacent:  <prompt caching CLAUDE.md ~3K tokens → 90% discount on subsequent turns>
```

**Confidence line** (optional): add `Confidence: high / medium / low` when scores are tied between tiers or when an override partially conflicts with the complexity score. Low confidence is a signal to surface the call to the user rather than apply silently.

---

## Adjacent Levers

Model choice is one knob — these are siblings worth pointing at when the model recommendation alone isn't the full answer.

**Model vs. effort are different axes — set both deliberately.** Model selects capability/knowledge (which brain); effort selects thoroughness (how many actions/how much thinking that brain spends). A stronger model at low effort often beats a weaker model at high effort for judgment-bound tasks, while mechanical tasks want a cheaper model with effort matched to the work — cranking effort on the wrong-tier model buys motion, not insight. When a recommendation card fires, name the effort level alongside the model whenever the task is clearly reasoning-heavy (`high`) or clearly mechanical (`low`).

| Lever | What it does | When |
|---|---|---|
| `/model <name>` | Switch active model mid-session (or `/model` with no args, or **Option+P** on Mac / **Alt+P** on Windows, to open the interactive picker) | After a mode or tier change |
| `/model opusplan` | Two-model workflow: Opus plans, Sonnet executes within one session — picker label: "Use Opus in plan mode, Sonnet otherwise" | Mixed planning + execution work; see Plan-Mode Pattern below |
| Skill `model:` frontmatter | Pin model per-skill (loads when skill activates; reverts on next prompt) | Skill is consistently better on one tier (e.g. `/debate-team` pins Opus) |
| Skill `effort:` frontmatter (`low` / `medium` / `high` / `xhigh` / `max`) | Adjust extended-thinking budget per-skill | Mechanical skills can run `effort: low`; reasoning-heavy skills `effort: high` |
| `/fast` toggle (**Opus 4.8 / 4.7 only**) | Same model, up to 2.5× faster output at premium pricing — Opus 4.8 is the durable fast tier (4.7 fast mode is deprecated) | Relevant when the architectural recommendation (Opus 4.8) feels too slow interactively |
| `/compact` vs `/clear` | Context hygiene (see `token-economy`) | Long sessions approaching limits |
| CLAUDE.md under 500 tokens | Loads every turn regardless of model | Always — the cheapest optimization |
| Prompt caching | 90% discount on cached prefix | Repeated CLAUDE.md or boilerplate |

**Skill-level pinning pattern.** When a skill's quality depends on model choice (e.g. red-team critique, system-design planning), pin it in the skill's frontmatter instead of relying on the user to remember to switch:

```yaml
---
name: red-team-review
description: Critique a design or PR for hidden risks
model: opus
effort: high
---
```

This makes the skill's quality reproducible — the right model + effort load whenever the skill activates, regardless of the session's default tier.

---

## Plan-Mode Pattern (`/model opusplan`)

Claude Code ships a built-in two-model workflow: `/model opusplan` routes planning to Opus and execution to Sonnet within a single session. In the interactive picker (`/model` no args, or **Option+P** / **Alt+P**), this is the option labeled **"Use Opus in plan mode, Sonnet otherwise."**

**Use `/model opusplan` when:** task has clear plan-then-execute structure, session will run long with most tokens spent on execution, or user wants Opus reasoning on the architecture but not on every line of code.

**Use plain `/model opus` when:** task is sustained reasoning end-to-end (deep debugging, multi-step proof), short session, or iterative exploration where the "plan" keeps changing.

**Output card:**

```
🎯 Model: opusplan (Opus + Sonnet) │ Mode: think │ Complexity: architectural
   Why:    Architecture-then-implementation workflow. Opus designs and reviews,
           Sonnet writes the actual code. ~60% token savings vs full-Opus session.
   Apply:  /model opusplan  (or Option+P / Alt+P → "Use Opus in plan mode, Sonnet otherwise")
   Note:   Review Opus's plan before approving execution — this is where misunderstandings
           get caught cheaply.
```

This is the canonical first-party implementation of the Executor/Advisor pattern. When the recommendation lands on `think` mode AND the task has plan-then-execute structure, prefer `/model opusplan` over manually toggling.

---

## CLAUDE.md Project-Level Default

Pin a per-project default in CLAUDE.md so the recommendation step only fires when something breaks the default assumption. Saves the router from running on every routine task.

```markdown
## Default model assumption

This project's default work tier is Sonnet 5. Escalate to Opus for
architecture and security audits; drop to Haiku for renames, lookups,
and batch ops.
```

The skill respects existing project defaults — if CLAUDE.md says "default is Sonnet" and the task scores into `simple`, no card needs to print. The card only fires when the recommendation diverges from the project default.

---

## Mid-Task Escalation

If task scope grows during execution — "fix typo" expands to "refactor module," for example — surface it explicitly rather than silently continuing on a now-mismatched model:

> 🎯 Complexity escalation detected — task grew from trivial to complex. Consider `/model sonnet` for the rest of this turn. Continue, switch, or restart your call.

Three options to the user: continue on the current model (knowing it's mismatched), switch model now (fresh context but cached prefix retained), or restart the turn (loses cache, regains alignment).

Do not silently continue. The whole point of advisory routing is that the user is in the loop on cost/quality tradeoffs — silent continuation breaks that contract.

---

## Examples

Three core examples cover the decision space. For the full set (6 examples + 3 edge cases including override-fires-despite-low-score, mixed-mode signals, and Plan-Mode candidates), see [`references/examples.md`](references/examples.md).

**Example 1 — trivial → Haiku**

> Task: Rename a variable in one file.
>
> ```
> 🎯 Model: Haiku 4.5 │ Mode: default │ Complexity: trivial
>    Why:    Single-file mechanical edit. Sonnet is 3× cost for zero recall gain.
>    Apply:  /model haiku
> ```

**Example 2 — architectural → Opus**

> Task: Design a new auth system from scratch.
>
> ```
> 🎯 Model: Opus 4.8 │ Mode: think │ Complexity: architectural
>    Why:    System design with security implications. Reasoning depth and
>            edge-case coverage justify the ~1.7× cost over Sonnet.
>    Apply:  /model opus     (or /model opusplan if implementation follows)
> ```

**Example 3 — subagent fleet**

> Task: Dispatch 5 explorer subagents for a codebase scan.
>
> ```
> 🎯 Model: Haiku 4.5 × 5 │ Mode: subagent-fleet │ Role: explorer
>    Why:    Explorer role, quality floor not triggered. 5× Haiku ≈ 1.7× Sonnet
>            in total cost — major savings on a parallel dispatch.
>    Apply:  pass `model: 'haiku'` to each subagent dispatch
> ```

---

## Integration Notes

- **Executor/Advisor pattern.** Sonnet executes (default), Opus advises (design review, adversarial critique, judgment calls). This skill formalizes that pattern as table rules — same logic, made explicit. Maps cleanly to two-model orchestration frameworks that distinguish "doer" agents from "reviewer" agents.
- **token-economy pairing.** Model choice is upstream of tool-call discipline. After picking the model, apply `token-economy` patterns for the tool-call layer (batch independent calls, targeted line-range reads, cheap-subagent delegation).
- **Boundary with llm-cost-optimizer.** `llm-cost-optimizer` is for production API spend — cost-observability systems, routing between providers, prompt caching at scale, reducing AI feature costs in shipped products. This skill is for in-session decisions on what model to run the current Claude Code turn under.

---

## Anti-overlap reminder

- NOT for production LLM API spend → use `llm-cost-optimizer`
- NOT for picking PR-reviewer execution mode → use `pr-reviewer-mode`
- NOT for picking which skill or tool to use → use `skill-discovery`
- NOT for session-context strategy or what to load into context → use `context-engineering` (strategic) or `token-economy` (tactical)

---

*Maintainer note: if you find yourself loading `references/signal-scoring.md` more than once per session or in most sessions, the progressive-disclosure split is wrong — the scoring detail is load-bearing, not reference. See [`docs/decisions/2026-05-17-model-router-progressive-disclosure.md`](../docs/decisions/2026-05-17-model-router-progressive-disclosure.md) for the reversal thresholds and tracking commands.*

---

## Pricing reference data

For absolute prices, cross-vendor comparisons, and notable non-Claude data points (e.g., Cursor Composer 2.5 at ~10% of GPT-5.5 cost), see [`references/live-pricing-sources.md`](references/live-pricing-sources.md). Load only when picking between Claude-family and non-Claude routing, or when re-verifying the Claude cost ratios after a model ships.

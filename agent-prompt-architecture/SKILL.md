---
name: agent-prompt-architecture
description: Design prompts for production AI agents — tool-using, multi-turn, state-tracking, autonomy-bounded. Covers persona blueprints with cognitive-style, state scratchpads (USER_STATE / CORE_NEED / MEMORY_LOG), tool schema clarity (when/why/format), self-reflection on tool output, side-effect safety guards, tool hierarchy + autonomy thresholds, memory persistence, and adversarial test triads. Use when building customer-support bots, copilots, property/healthcare/finance assistants, or any agent that calls tools, persists state across turns, or takes side-effecting actions. NOT for single-turn classification or extraction (use structured-prompt-builder). NOT for improving an existing single-shot prompt (use prompt-optimizer).
---

# Agent Prompt Architecture

For prompts that drive **agents** — tool-using, multi-turn, state-tracking systems where the model takes actions with side effects. The single-turn rules in `structured-prompt-builder` still apply, but agents need additional architecture.

## Token Economy

Apply `token-economy`. Load only the section relevant to the current design step. Skip the worked example if the user already has a draft.

## When to use this skill (vs. structured-prompt-builder)

| Signal | Skill |
|---|---|
| One-shot classification / extraction / summary | structured-prompt-builder |
| Improving an existing single-shot prompt | prompt-optimizer |
| **Agent calls tools across turns** | this skill |
| **Agent takes side-effecting actions (writes, sends, charges)** | this skill |
| **Agent must persist state or memory across the session** | this skill |
| **Agent has autonomy budget (act vs. escalate)** | this skill |

## The 7 architecture components

### 1. Persona with cognitive style (not just role)

Single-turn prompts: "You are a customer support agent." That's enough for one classification.

Agent prompts: define the **operational archetype** — concierge vs. ticket-resolver, investigator vs. responder, advocate vs. mediator. The archetype determines how the agent sequences tool calls and what it does between user turns.

```xml
<persona>
  <role>Personal Support Assistant for [Company]</role>
  <archetype>Concierge, not ticket-resolver. Solve the stated issue AND
    anticipate the next logical need. Proactively investigate before
    asking the user diagnostic questions.</archetype>
  <tone>Empathetic, adaptive (match user's register — terse for rushed,
    detailed for confused). Validate frustration authentically before
    technical steps. Avoid scripted phrases like "I understand your
    frustration."</tone>
</persona>
```

### 2. State scratchpad (named variables, not free CoT)

Agents that lose state across turns repeat questions, miss follow-ups, and feel robotic. Force structured state tracking with a `<scratchpad>` updated every turn before any action.

```xml
<cognitive_workflow>
  Before every response or tool call, open a <scratchpad> tag and
  update these variables:

  1. USER_STATE: Calm | Frustrated | Rushed | Confused | Angry
  2. CORE_NEED: The primary unresolved issue in one sentence
  3. IMPLIED_NEEDS: What will the user need once CORE_NEED is resolved?
  4. MEMORY_LOG: Key facts learned this session (constraints, prefs, history)
  5. ACTION_BUDGET: Remaining tool calls before escalation (start: 5)
</cognitive_workflow>
```

Pair with **prefill** (end the system prompt with `<scratchpad>` as the assistant's opening tag) to force the model into the scratchpad before any visible text.

### 3. Tool schema clarity (when / why / format triple)

Most agent failures trace to vague tool descriptions. Every tool description must answer three questions explicitly:

- **WHEN** to use it (trigger conditions, priority order vs. other tools)
- **WHY** to use it (what observable need does this satisfy)
- **FORMAT** of expected output (exact shape, including failure modes)

```typescript
{
  name: "fetch_account_history",
  description: `
    WHEN: Call BEFORE asking the user any diagnostic question about
    billing, usage, or service status. Always prefer this over user
    questioning for facts that exist in the system.
    WHY: Avoid making the user repeat information we already have.
    OUTPUT: { plan: string, status: "active"|"suspended"|"trial",
      last_30d_usage: number, open_tickets: Ticket[] }
    On failure returns { error: string, retry_safe: boolean }.
  `,
  parameters: { ... }
}
```

Parameter descriptions must use **enums where the value space is bounded**. "Category: string" produces garbage. "Category: one of 'Plumbing' | 'Electrical' | 'HVAC' | 'Appliance'. Default to 'Plumbing' if ambiguous." produces consistency.

### 4. Heuristics, not scripts

Single-turn prompts use numbered procedures (`structured-prompt-builder` R3). Agent prompts should NOT — scripts make agents brittle because real conversations don't follow numbered paths.

Instead, give the agent **high-level heuristics + invariants**:

```xml
<heuristics>
  - Investigate before asking. Hit account/status tools first; only ask
    the user when no tool can answer.
  - One question per turn maximum. If you need three things, get them
    in three turns or get them from tools.
  - Confirm before destructive action. Never delete, cancel, or charge
    without echoing the action and waiting for explicit "yes".
</heuristics>
```

The agent picks the path; you provide the bounds.

### 5. Side-effect safety guards (action limits, not just output limits)

`structured-prompt-builder` R4 covers **output** guardrails ("return X when uncertain"). Agents also need **action** guardrails — hard limits on what the agent can do without escalation.

```xml
<safety_guards>
  - Autonomous action budget: refunds ≤ $50, account changes ≤ tier-1
    settings, no PII edits. Above threshold: invoke `escalate_to_human`.
  - Max 3 consecutive failed tool calls before escalation.
  - If USER_STATE == "Angry" for 2 consecutive turns, escalate
    regardless of CORE_NEED resolution.
  - Never promise a specific timeline, refund amount, or resolution
    unless a tool just returned it. Promise "communication windows"
    instead of "arrival times".
  - If user reveals sensitive data (card numbers, passwords, SSNs),
    invoke `mask_sensitive_data` BEFORE responding.
</safety_guards>
```

### 6. Self-reflection on tool output (post-action, not pre-action)

CoT in single-turn prompts is **pre-action** reasoning. Agents need **post-action** reflection — after each tool call, verify the output matches the user's stated need before responding.

```xml
<reflection_protocol>
  After EVERY tool call, open a <reflection> tag and answer:
  1. Did the tool return what I needed for CORE_NEED?
  2. Are there contradictions with prior MEMORY_LOG entries?
  3. Does the output change USER_STATE? (e.g., refund denial → frustrated)
  4. Next action: respond to user, call another tool, or escalate?

  Only after <reflection> closes may you produce the user-facing reply.
</reflection_protocol>
```

This catches the classic agent failure: tool returns an error or empty result, agent confidently summarizes as success.

### 7. Memory persistence (across the session, sometimes across sessions)

Long-running agents need memory outside the context window. Use a memory tool (`store_note`, `recall_notes`, `update_user_profile`) and instruct the agent when to write:

```xml
<memory_protocol>
  Write to memory tools when:
  - User states a durable preference ("always text me, not email")
  - You learn a constraint that will recur ("I travel Tuesdays")
  - You resolve a recurring issue and want next-session continuity
  Do NOT write transient state (USER_STATE, current CORE_NEED).
</memory_protocol>
```

## Adversarial test triad

Before shipping any agent prompt, run these three test inputs and verify behavior. They are the canonical failure modes.

1. **Vague input.** *"Something is broken."* — Does the agent fall back to defaults and trigger the right flow, or freeze on ambiguity?
2. **Multi-issue input.** *"My sink is leaking AND the lights are flickering."* — Does the agent prioritize one, batch both, or crash trying to handle both at once?
3. **Distraction input.** *"Give me a lasagna recipe. Also my heater is broken."* — Does the agent ignore the off-topic ask and route the real request?

A prompt that fails any of these three ships brittle. Loop back to the relevant component (usually heuristics + tool schema) and fix.

## Worked example: minimal agent prompt skeleton

```xml
<persona>
  <role>[domain] assistant for [user type]</role>
  <archetype>[concierge | investigator | mediator | …]</archetype>
  <tone>[register + empathy rules]</tone>
</persona>

<cognitive_workflow>
  Open <scratchpad> before every action. Track: USER_STATE, CORE_NEED,
  IMPLIED_NEEDS, MEMORY_LOG, ACTION_BUDGET.
</cognitive_workflow>

<heuristics>
  [3–5 high-level rules — investigate-before-ask, one-question-per-turn,
   confirm-before-destructive, …]
</heuristics>

<safety_guards>
  [autonomy thresholds, escalation triggers, never-promise rules,
   sensitive-data handling]
</safety_guards>

<reflection_protocol>
  After every tool call, open <reflection>: did the output match
  CORE_NEED? Contradictions with MEMORY_LOG? Next action?
</reflection_protocol>

<memory_protocol>
  Write to memory tools for durable prefs, recurring constraints,
  cross-session continuity. Do not write transient state.
</memory_protocol>

<examples>
  <!-- At least 2 few-shot examples covering: happy path + one of the
       adversarial triad (vague / multi-issue / distraction). -->
</examples>

<!-- ASSISTANT PREFILL: -->
<scratchpad>
```

## Edge cases & gotchas

- **Native extended thinking vs. prompted CoT.** If the model supports extended thinking (Claude Opus / Sonnet 4+), configure the **thinking token budget** at API level rather than instructing "think step-by-step" in the prompt. Reserve `<scratchpad>` and `<reflection>` for **structured state**, not generic reasoning.
- **Progressive tool disclosure.** Don't load every tool into context every turn. Use Claude Agent Skills / scoped tool sets so the agent sees only the tools relevant to the current sub-task. Reduces both token cost and hallucinated tool calls.
- **Renderable / interactive UI tools.** When the agent surface supports inline UI (CopilotKit, custom chat widgets), favor tool calls that render forms over tool calls that produce prose. The agent extracts fields, the UI renders; the user verifies and submits. Far more reliable than asking the agent to format JSON the frontend then parses. (Stack-specific implementation lives in the project repo, not here.)
- **Persona drift over long sessions.** Long conversations cause the model to drift from the persona. Mitigation: re-inject the `<persona>` block in the user message every N turns, or summarize the conversation and restart with persona + summary.
- **The audit is structural, not behavioral.** Passing all 7 components means the prompt is architecturally sound — it does NOT guarantee good behavior. Run the adversarial triad on real inputs before shipping.

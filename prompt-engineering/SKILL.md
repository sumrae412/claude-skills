---
name: prompt-engineering
description: "Router for all prompt-engineering work — dispatches to structured-prompt-builder (single-turn authoring), agent-prompt-architecture (tool-using agents), prompt-optimizer (improving), prompt-optimization (variant analysis at scale), or prompt-governance (production management); centralizes the shared Anthropic prompting principles each sub-skill enforces. Use when a prompt-related ask doesn't cleanly map to one sub-skill or needs the write → improve → govern pipeline; triggers on 'prompt engineering', 'how should I prompt Claude'. If the request clearly fits one sub-skill, invoke that directly."
---

# Prompt Engineering

Thin router over four prompt sub-skills. The router itself stays small; each sub-skill loads on demand via the Skill tool.

## Shared principles (Anthropic + Vellum guidance)

All sub-skills implement these. Cite them by name when audit-flagging a prompt.

**External validation:** the skills-as-modular-prompts approach below is reinforced by guidance from Anthropic's "Code with Claude" event (San Francisco, May 2026): *if you repeat a prompt instruction twice, turn it into a skill; modularize 600-line monolithic prompts; use code for deterministic logic instead of asking the model to re-derive it.* The principle list below is the per-prompt mechanics; the skills-system shape is the deployment surface.

### Universal (apply to every prompt)

1. **XML tag structure** — separate role, background, instructions, examples, input
2. **Specific role + audience** — domain + task + register, not "you are a helpful assistant"
3. **Few-shot with negative examples** — at least one example of the escape hatch firing
4. **Escape hatch for uncertainty** — explicit "I don't know" output value with a guardrail
5. **Output contracts with enums** — categorical fields use `"a" | "b" | "c"`, not `str`
6. **Chain-of-thought** — `<thinking>` tag before `<answer>` for complex reasoning
7. **Long inputs before instructions** — input data first, task statement last (critical >1K tokens)
8. **Positive framing** — "do X" in instructions; reserve "don't" for guardrail hard stops
9. **Grounding anchors** — for long-context recall, prefill `<quotes>` extraction before the answer
10. **Prefill assistant message** — seed `{"`, `<answer>`, or `<scratchpad>` to lock format and skip preamble
11. **Prompt chaining** — split heterogeneous subtasks into separate calls, don't mega-prompt
12. **Test-driven iteration** — eval against real inputs after every change

### Single-turn only (numbered procedures fit)

13. **Numbered task decomposition** — explicit ordered procedure. **Do not** apply this to agent prompts — see Agent principle 14.

### Agent-specific (tool-using, multi-turn, side-effecting)

14. **Heuristics, not scripts** — agents need high-level rules + invariants, not numbered procedures. Numbered scripts make agents brittle.
15. **Persona archetype + cognitive style** — concierge vs. ticket-resolver, investigator vs. responder. Determines tool-call sequencing.
16. **State scratchpad with named variables** — USER_STATE, CORE_NEED, IMPLIED_NEEDS, MEMORY_LOG, ACTION_BUDGET. Updated every turn before any action.
17. **Tool schema clarity (when / why / format triple)** — every tool description answers all three explicitly.
18. **Self-reflection on tool output** — `<reflection>` after tool calls (post-action) is distinct from CoT (pre-action). Catches "confident summary of empty result" failures.
19. **Side-effect safety guards** — autonomy thresholds (refund ≤ $X, max N tool retries, escalation triggers). Distinct from output guardrails.
20. **Memory persistence** — write durable facts (preferences, constraints) to memory tools; do not write transient state.
21. **Adversarial test triad** — before shipping, run vague / multi-issue / distraction inputs. A prompt that fails any ships brittle.

## Pre-flight prompt debugger (mandatory for coding-work prompts)

Lightweight in-conversation debugger. Fires BEFORE the prompt is deployed, not after a failure. Mandatory for any prompt that will drive coding work (LLM generating, editing, refactoring, reviewing, or shipping code); recommended for single-turn classifiers. Operationalizes Universal #12 (test-driven iteration) and Agent #21 (adversarial triad) into a runnable 5-case checklist with a diagnosis grid.

### Build the tiny eval suite

For the prompt under test:

1. **Control case (1)** — should always pass. The happy path. If this fails, the prompt is broken at baseline; do not proceed to edge cases.
2. **Edge cases (3)** — plausible inputs where the prompt could fail. For agents, draw from the adversarial triad (vague / multi-issue / distraction). For single-turn, draw from domain failure modes (ambiguous category, missing field, conflicting signals).
3. **Capability-boundary case (1)** — input where the agent SHOULD escalate, ask for help, or refuse. Tests the escape hatch (Universal #4) and side-effect guards (Agent #19). Distinct from edge cases: edge tests correctness; boundary tests honest deferral.

Run each case mentally or against the model. State the expected behavior per case before running.

### Diagnose each failure into ONE bucket

| Bucket | Symptom | Fix surface |
|---|---|---|
| **Prompt issue** | Instructions unclear, missing escape hatch, format underspecified, conflicting heuristics, role/audience vague | Edit the prompt |
| **Missing tool or capability** | Agent has the right intent but no way to act (no search tool, no file read, no escalation channel, no enum value for the case) | Add a tool, expand a tool schema, or add a capability |
| **Harness / workflow issue** | Prompt and tools are correct but the runtime can't execute it (no assistant-message prefill, no extended thinking budget, wrong adapter, missing env var, upstream caller not passing field) | Fix the harness, switch adapter, or change deployment shape |

### Suggest the smallest change to test next

One targeted change per iteration, then re-run the 5-case suite. Resist rewriting the prompt blindly — most "prompt failures" on coding-work agents are actually tool gaps or harness limits, and rewriting the prompt against them just shuffles the failure.

**Heuristic:** if ≥2 of 5 failures diagnose as `harness / workflow`, stop editing the prompt and fix the harness first.

### When to fire (mandatory vs. recommended)

- **Mandatory:** any prompt that will drive coding work; any ≥10-line change on a production agent prompt; any new tool added to an existing agent (the new tool needs its own capability-boundary case).
- **Recommended:** single-turn classifiers, extractors, summaries.
- **Skip:** trivial wording tweaks on a prompt with a passing suite from the last week.

Composes with `prompt-optimizer` (which is the reactive debugger — same framework, applied after a failure) and `evals` (which scales this to golden datasets + LLM-as-judge for regression gating).

## Routing

| User intent | Sub-skill |
|---|---|
| Write a new single-turn prompt (classification, extraction, summary) | [structured-prompt-builder](../structured-prompt-builder/SKILL.md) |
| Write a prompt for a tool-using, multi-turn, or side-effecting agent | [agent-prompt-architecture](../agent-prompt-architecture/SKILL.md) |
| Fix / improve / evaluate one prompt | [prompt-optimizer](../prompt-optimizer/SKILL.md) |
| Compare variants, promote winners, draft challengers | [prompt-optimization](../prompt-optimization/SKILL.md) |
| Registry, A/B tests, rollback, eval pipelines in CI | [prompt-governance](../prompt-governance/SKILL.md) |
| Unclear or multi-stage | Stay here, ask one routing question |

## Routing flow

1. If intent maps unambiguously to one row, invoke that sub-skill via the Skill tool. Do not load this router's body into context — sub-skills already cite the shared principles.
2. If intent spans stages (e.g., "write a classifier prompt and set up an A/B test"), sequence the dispatch: author → optimize → govern. One sub-skill per turn.
3. If intent is unclear, ask one combined question:
   > *"Are you (a) writing a new single-turn prompt, (b) designing a tool-using agent, (c) improving an existing prompt, (d) comparing variants from a running system, or (e) managing prompts in production?"*

## Anti-patterns

- Don't reproduce sub-skill content in the router. The principles list above is the only shared surface — everything else lives in the dispatched skill.
- Don't dispatch to multiple sub-skills in parallel. They have different conversational shapes (interactive draft loop vs. analysis report vs. CI design).
- Don't bypass the sub-skill to draft a prompt inline. The audit loops in structured-prompt-builder and prompt-optimizer exist because freehand prompts skip principles 4, 5, 8, 9, and 11 most often.

## Related skills (not routed here)

- **`context-engineering`** — strategic context-window management for active agents (different problem).
- **`llm-cost-optimizer`** — production API spend (different problem).
- **`rag-architect`** — retrieval pipeline design (different problem).

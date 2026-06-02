---
name: prompt-engineering
description: Router for all prompt-engineering work — dispatches to structured-prompt-builder (single-turn authoring), agent-prompt-architecture (tool-using agents), prompt-optimizer (improving), prompt-optimization (variant analysis at scale), or prompt-governance (production management). Centralizes the shared Anthropic prompting principles each sub-skill enforces. Use when the user asks about prompts in general, isn't sure which sub-skill applies, or needs an end-to-end pipeline (write → improve → govern). Triggers on "prompt engineering", "help with a prompt", "Anthropic prompting best practices", "how should I prompt Claude", or any prompt-related ask that doesn't cleanly map to one sub-skill. If the request clearly fits one sub-skill, invoke that directly.
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

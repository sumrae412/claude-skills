# Multi-Agent Patterns in claude-flow

Vocabulary mapping each phase to its multi-agent pattern
(taxonomy from anthropic.com/news/multi-agent-patterns, 2026-04).

## Pattern Map

| Phase | Pattern | Evidence |
|-------|---------|----------|
| Phase 2 exploration | Orchestrator-subagent + staggered waves | One coordinator dispatches 2-4 researchers, synthesizes. See `staggered_waves_pattern.md`. |
| Phase 4 architecture | Generator-verifier (explicit) | Executor generates 2 options → Opus advisor verifies → user approves. |
| Phase 5 implementation | Orchestrator-subagent | Main session orchestrates per-task implementer subagents. |
| Phase 5 retry ladder | Generator-verifier with cross-model verifier | Executor regenerates → investigator (cross-model on iter 3) verifies root cause. |
| Phase 6 review cascade | Generator-verifier (tiered) | Diff = generated output; CodeRabbit + haiku + sonnet reviewers = tiered verifiers. |

*Phases 0, 1, 3, and 5.5 are single-agent (context loading, triage, clarification, self-reflection) — they don't participate in a multi-agent pattern and are intentionally omitted.*

## Patterns NOT used (and why)

- **Agent teams (persistent workers):** Sessions are bounded — workers don't accumulate context across plans.
- **Message bus:** Phase transitions are deterministic (see transition map in SKILL.md); no dynamic routing.
- **Shared state:** Contracts (`$exploration`, `$requirements`, `$plan`, `$diff`) are passed explicitly between phases, not read-write shared.

## When to reach for an unused pattern

- *Agent teams* — if we ever do multi-session long-running audits where a subagent should retain codebase context across runs.
- *Message bus* — if Phase 6 reviewer selection becomes truly dynamic (registry already declarative; close but not emergent).
- *Shared state* — explicitly avoided; contracts are the coordination surface. Do not regress.

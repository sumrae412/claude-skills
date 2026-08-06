# Skill categories

Cross-cutting categories that group related skills without merging them. Use this when you want to discover all skills in a topic area; use individual SKILL.md files when you want the actual patterns.

This file gives sibling skills a shared parent for navigation and discoverability while keeping their descriptions tuned to distinct triggers (which keeps BM25 routing clean — see the description-hygiene rule in MEMORY.md).

---

## Defensive coding

Patterns for code that anticipates failure modes, surfaces errors instead of swallowing them, and gives users feedback on every state transition.

| Skill | Surface | When to load |
|---|---|---|
| [`defensive-ui-flows/SKILL.md`](defensive-ui-flows/SKILL.md) | Frontend (Jinja, Alpine.js, vanilla JS, CSS) | Writing or reviewing UI code: guard clauses with feedback, state flags with try-catch, overlay inline feedback, multi-step state reset |
| [`defensive-backend-flows/SKILL.md`](defensive-backend-flows/SKILL.md) | Python backend (services, routes, migrations) | Writing or reviewing backend code: error handling, data migrations, service-layer functions, cross-module API calls, constants/enums |

The two skills are intentionally separate (different stacks, different patterns, different triggers) but share parallel maintenance scaffolding (`update-skill.md`, `evidence.md`, `test-scenarios.md`). If those scaffolds drift in meaningful ways, the doc-graph script (`scripts/build_doc_graph.py`) will surface it.

---

## Personal / life-admin

Skills for non-work surface area — teaching/learning, life logistics. Not invoked during feature development; useful standalone or in personal-context sessions.

_Empty since the 2026-07-17 skills audit (`learning-coach`, `life-planner` retired — recover from git history if needed)._

---

## Communication

Skills that shape how Summer writes and sends — voice on the way in, state and intent on the way out. They run in sequence, not as alternatives: `communication-safeguards` handles the upstream state/intent check before composition, `writing-voice` carries her voice through drafting, and the upstream `anthropic-skills:toneguard` plugin scans the final text for passive-aggressive / escalatory markers.

| Skill | Surface | When to load |
|---|---|---|
| [`communication-safeguards/SKILL.md`](communication-safeguards/SKILL.md) | Pre-composition state/intent layer — activation 1–10, HALT, Two-Sentence Response, 2-Minute Reset, ToneGuard handoff | "Draft a Slack message", "how should I respond to", "I'm fuming about", "I can't stop replaying", "help me reply to" — any communication request that may be carrying conflict heat |
| [`writing-voice/SKILL.md`](writing-voice/SKILL.md) | Summer's personal voice profile — sensory + deadpan dark humor for creative work, minimal + direct + lead-with-the-ask for business writing | "Write this for me", "draft an email", "help me write", "write as me", "in my voice" — any drafting task she'll put her name on |
| [`sme-voice/SKILL.md`](sme-voice/SKILL.md) | Inverse of `writing-voice` — capture and apply another person's writing voice (SME ghostwriting/editing); per-subject profiles saved to `~/claude_code/agent-vault/sme-voices/<slug>.md` for cross-machine sync | "Build a voice profile for [name]", "capture [name]'s voice", "edit this in [name]'s voice", "ghostwrite as [name]", `/sme-voice ...` |

`writing-voice` and `sme-voice` are an inverse pair — `writing-voice` writes as Summer, `sme-voice` writes as a captured SME. They share `shared/communication-principles.md`, but `sme-voice` inverts the precedence: the SME's register wins when in conflict with the shared principles.

Sequencing: `communication-safeguards` Phase 1 (activation + HALT) → `writing-voice` for drafting → `communication-safeguards` Phase 4 (ToneGuard pre-send review). The shared communication principles at `shared/communication-principles.md` apply across both — see the "Writing skills load shared communication principles" section in `~/.claude/CLAUDE.md`.

---

## Cost / token efficiency

Three skills that all reduce token spend, but at different layers: strategic in-session decisions, tactical per-tool-call discipline, and production API spend. They compose — pick the right model first, then run tool calls efficiently, and (separately) optimize the cost of shipped AI features.

| Skill | Surface | When to load |
|---|---|---|
| [`model-router/SKILL.md`](model-router/SKILL.md) | In-session model selection — Haiku 4.5 / Sonnet 4.6 / Opus 4.7 | "Which model should I use for X", before dispatching parallel subagents (cost multiplies across the fleet), when a task feels mismatched to the current model |
| [`token-economy/SKILL.md`](token-economy/SKILL.md) | Per-tool-call discipline within a session — combine discover+read, batch edits, parallelize independent calls, targeted line ranges | Cost-constrained sessions, heavy token usage mid-session, before `/compact` or session handoff, briefing a subagent on efficient tool use |
| [`llm-cost-optimizer/SKILL.md`](llm-cost-optimizer/SKILL.md) | Production LLM API spend — cost observability, multi-provider routing, prompt caching at scale | "My AI costs are too high", building cost monitoring for shipped AI features, implementing caching infra |

Boundaries: `model-router` is upstream of `token-economy` (pick the model, then run efficiently under it). `llm-cost-optimizer` is a different surface entirely — it's for production systems, not session decisions.

---

## How to extend

To add a new category:

1. Add a new `## <Category>` section.
2. List 2+ skills in a table with surface and trigger criteria.
3. Cross-reference: each listed skill stays at its own path; this file is a discovery layer, not a router.

Single-skill "categories" should not be added — if there's only one skill, the SKILL.md description carries the discoverability load on its own.

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

| Skill | Surface | When to load |
|---|---|---|
| [`learning-coach/SKILL.md`](learning-coach/SKILL.md) | Teaching, mental models, Feynman tutoring, Socratic dialogue, 30-day curricula | "Help me understand X", "explain this simply", "plan a learning curriculum for Y" |
| [`life-planner/SKILL.md`](life-planner/SKILL.md) | Meal plans, plain-English legal documents, personal finance summaries, travel planning | "Plan my week of meals", "what does this contract say", "summarize this 401k", "plan a trip to X" |

Both also reindexed in `~/.claude/CLAUDE.md` Domain Skills table for cross-project discovery.

---

## How to extend

To add a new category:

1. Add a new `## <Category>` section.
2. List 2+ skills in a table with surface and trigger criteria.
3. Cross-reference: each listed skill stays at its own path; this file is a discovery layer, not a router.

Single-skill "categories" should not be added — if there's only one skill, the SKILL.md description carries the discoverability load on its own.

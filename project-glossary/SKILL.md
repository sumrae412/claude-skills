---
name: project-glossary
description: Maintain a per-repo CONTEXT.md glossary of canonical domain terms (and optionally docs/adr/ for decisions) so subagents speak the project's language instead of generic vocabulary. Use when starting work in an unfamiliar repo, when terminology drifts ("service" vs "module" vs "handler"), when fuzzy or overloaded terms appear in conversation, or when CLAUDE.md is too gotcha-heavy to double as a glossary. Distinct from CLAUDE.md (rules/gotchas) and MEMORY.md (cross-session lessons).
---

# Project Glossary (CONTEXT.md)

Adapted from Matt Pocock's `grill-with-docs` skill. Pairs with `zoom-out`, `claude-flow` Phase 2 exploration, and audit reviews.

## Why

CLAUDE.md captures rules, gotchas, and project identity. MEMORY.md captures cross-session lessons. Neither is the right home for **canonical domain vocabulary** — the precise term for each concept that subagents and reviewers must use.

Without a glossary, subagents drift into generic words ("service", "handler", "API", "boundary", "component") and reinvent terminology each session. Variables, functions, files, and PR descriptions diverge. The codebase becomes harder to navigate for both humans and AI.

A glossary fixes this in one place: define each term once, point everything at it, enforce its use.

## File layout

Single-context repo (most repos):

```
/
├── CONTEXT.md            ← glossary lives here
├── docs/
│   └── adr/              ← architecture decision records (optional)
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

Multi-context repo (rare — only when bounded contexts truly diverge):

```
/
├── CONTEXT-MAP.md        ← points to each context's glossary
├── docs/adr/             ← system-wide decisions
└── src/
    ├── ordering/CONTEXT.md
    └── billing/CONTEXT.md
```

**Create lazily** — only when there's something to write. Don't seed empty templates.

## CONTEXT.md structure

```markdown
# CONTEXT — <project name>

## Glossary

### <Canonical Term>
<One-sentence definition. Distinguish from any near-synonyms.>
- **Code names:** <model class, table name, file/dir patterns>
- **NOT:** <terms this is often confused with, with one-line distinction>

### <Next Term>
...

## Layers / Modules

<One-paragraph map of the major modules and how they connect, in glossary terms.>

## Anti-vocabulary

Terms to avoid because they're ambiguous, deprecated, or carry the wrong connotation:
- ~~Account~~ — use **Customer** (billing entity) or **User** (login identity).
- ~~Service~~ — too generic; name the specific module.
```

Keep it short. A glossary is not documentation — it's a vocabulary anchor.

## When to add a term

Add a term to CONTEXT.md when:
- It appears in a user message and you had to ask "do you mean X or Y?"
- Two contributors used different words for the same concept in the same PR or thread.
- A subagent invented a new noun ("HandlerManager") for something already named in the domain.
- An ADR defines a new bounded concept.

Don't add:
- Standard CS terms (HTTP, queue, transaction) unless the project gives them a non-standard meaning.
- Implementation details that change often (specific function names, file paths).
- Anything that would just duplicate code-level naming.

## During work

### Challenge against the glossary
When the user uses a term that conflicts with CONTEXT.md, call it out: *"Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"*

### Sharpen fuzzy language
When a term is vague or overloaded, propose the canonical name: *"You're saying 'account' — do you mean the Customer or the User? CONTEXT.md says those are different."*

### Surface gaps
When a concept has no glossary entry, propose one before naming it ad-hoc. A gap surfaced is half-resolved.

## Subagent integration

In claude-flow Phase 2 (exploration) and audit reviewers, inject the relevant CONTEXT.md slice into subagent prompts the same way memory-injection injects gotchas:

> Use the project's canonical vocabulary: <relevant CONTEXT.md excerpt>. Do not introduce new terms for concepts that already have names. If you encounter an unnamed concept, surface it as a glossary gap.

## ADRs (optional)

If the project makes architecture decisions worth not re-litigating, pair CONTEXT.md with `docs/adr/NNNN-title.md`. Standard ADR format (Status / Context / Decision / Consequences). Reviewers check ADRs before proposing alternatives.

ADRs are about decisions; CONTEXT.md is about words. Keep them separate.

## Anti-patterns

- **Glossary in CLAUDE.md.** CLAUDE.md is full of gotchas, rules, and policies — burying vocabulary in it dilutes both. Keep them separate files.
- **Eager template.** Spinning up a 12-section CONTEXT.md before the first term is defined produces empty scaffolding nobody reads. Create on first real entry.
- **Documentation drift.** A glossary that disagrees with the code is worse than no glossary. When code renames a concept, update CONTEXT.md in the same PR.
- **Terms without distinctions.** "Customer — a person who pays us" is useless without "NOT: User (login identity)". The contrast is the value.

## Pairs with

- `zoom-out` — uses CONTEXT.md vocabulary when mapping unfamiliar code.
- `claude-flow` — Phase 2 (Research/Exploration) and Phase 6 (Review) inject CONTEXT.md content into subagents.
- `memory-injection` — sibling pattern; gotchas vs vocabulary.
- CLAUDE.md — orthogonal; keep rules there, vocabulary here.

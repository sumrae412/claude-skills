---
name: codebase-design
description: Module boundary and interface design for working codebases. Use when asking "where should this logic live?", "is this abstraction worth keeping?", "should these modules merge or split?", "is this interface too wide?", "deep vs shallow modules", or "what's the right seam here?" Covers deep-module depth scoring, the deletion test, one-adapter vs two-adapters rule, and locality reasoning. Does NOT cover visual/UX design (see design-audit) or line-level simplification (see simplify).
license: MIT
metadata:
  author: summerela
  version: "1.0.0"
  adapted_from: "mattpocock/skills codebase-design + DEEPENING.md, 2026-06-26 source read"
user-invocable: true
---

# Codebase Design

Principled vocabulary for module boundaries and interface shape in a working codebase.
Load this when the question is structural — where does this live, what should this
expose, is this abstraction earning its cost?

## Token Economy

Load only the section needed. For dependency-category framework and worked examples,
lazy-load `DEEPENING.md` via a Read call — do not embed it here.

---

## Core Vocabulary

**Deep module** — large implementation hidden behind a small, stable interface.
Depth = functionality / interface surface. A 500-line module with a 3-method API
is deep. A 30-line module with a 12-argument constructor is shallow.

**Seam** — a boundary where two modules touch. A good seam lets you replace one
side without touching the other. A bad seam leaks internal types, intermediate
state, or implementation decisions across the boundary.

**Adapter** — a module whose entire job is translation between two interfaces.
Justified when the two sides have independent lifecycles (e.g. a vendor SDK
vs. your domain model). Unjustified when both sides are owned by the same team
and updated together.

**Leverage** — a module has leverage when a small change to its interface produces
large behavioral changes. High leverage = worth stabilizing. Low leverage = may
not need to exist.

**Locality** — can you understand this module by reading only this directory?
Good locality means the module's name, its public API, and its tests are all
the documentation you need.

---

## The Deletion Test

> "Would deleting this module concentrate or spread complexity?"

- **Spreads complexity** (N call sites must absorb the logic): the module was earning
  its keep. Keep it; consider deepening it.
- **Concentrates complexity** (a single caller absorbs a wrapper with no logic):
  the module is a pass-through. Delete it and wire the caller directly.

Run this test before any "extract to its own file" refactor. A thin wrapper that
tests identically before and after extraction is not modularity — it is friction.

---

## One-Adapter-Hypothetical / Two-Adapters-Real Rule

Do NOT introduce an abstraction layer for one hypothetical future implementation.
> "We might swap the PDF library later" is not a seam; it is a guess.

Add the adapter layer when a **second real implementation exists** — i.e., two
concrete classes that satisfy the same interface in production today. Until then,
wire directly and keep the option to extract later.

This rule eliminates a large class of premature generalization: interfaces with
one implementor, service locators with one registration, "strategy" patterns with
one strategy.

---

## Depth Scoring (quick pass)

Rate a module before deciding to split, merge, or rewrite:

| Score axis | Low depth (red) | High depth (green) |
|---|---|---|
| Interface surface | Many params, complex types, many methods | Few params, simple types, 1-3 methods |
| Implementation size | < 50 lines | > 200 lines |
| Call-site count | 1-2 callers | 10+ callers |
| Test surface | Tests mirror implementation | Tests name business rules |
| Deletion outcome | Concentrates | Spreads |

A module scoring red on 3+ axes is a candidate for deletion or merger.
A module scoring green on 3+ axes is a candidate for stabilization.

---

## Where Should This Logic Live? (quick decision tree)

1. Does it encode a business rule? → `lib/<domain>/` (shared domain layer)
2. Does it translate between two representations? → adapter module, only if rule above
   applies (two real implementations exist)
3. Does it exist only to call one other module? → delete it, wire directly
4. Does it know about the HTTP layer? → `routes/` only; strip it out if found elsewhere
5. Does it know about the UI? → `components/` or `hooks/`; strip it out of `lib/`

For CourierFlow beta's specific layer structure and worked examples, load `DEEPENING.md`.

---

## See Also

- `../simplify/SKILL.md` — thin-wrapper rules, 1000-line file ceiling, net-line-delta
  simplification. Operates at the line/function level; this skill operates at the
  module/interface level.
- `../design-audit/SKILL.md` — visual/UX audit. Entirely separate concern.
- `engineering:architecture` (upstream plugin skill) — system-level architecture
  decisions (service decomposition, database choices, infra topology). This skill
  is intra-repo, not cross-service.

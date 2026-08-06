# Codebase Design — Deepening Reference

Lazy-loaded by `SKILL.md`. Read this when you need the dependency-category
framework or concrete worked examples.

---

## Dependency Categories

Not all module dependencies are the same. Use this taxonomy to decide how much
isolation (adapter, interface, mock boundary) a dependency deserves.

| Category | Definition | Isolation warranted? |
|---|---|---|
| **In-process** | Pure logic: no I/O, no side effects, called synchronously | No — wire directly, test directly |
| **Local-substitutable** | Stateful but owned by the team; can be swapped in tests with a local fake | Thin interface — enough to inject a test double, no more |
| **Remote-owned** | External service (database, cache, queue) whose contract you don't control but can observe | Yes — repository / gateway pattern; keep the interface minimal |
| **True-external** | Third-party vendor API, payment processor, email provider — both contract and runtime are foreign | Yes — anti-corruption layer; translate their types to your domain at the boundary |

**Rule of thumb:** the further right in the table, the more isolation pays for
itself. Don't apply remote-owned patterns to in-process logic.

---

## Worked Examples — CourierFlow Beta

The following examples use CourierFlow beta's actual layer structure
(`~/claude_code/courierflow_beta/`). They are illustrative, not prescriptive
— they show how the vocabulary applies to code that exists.

### Example 1: `lib/db/` is deep, `lib/api-client-react/` is shallow

`lib/db/` contains the Drizzle ORM schema, query helpers, and migration config.
Its interface to the rest of the codebase is a small set of typed query functions.
Callers (`artifacts/api-server/src/routes/`) don't know about Drizzle internals —
they call `getProperties(userId)` and get back domain objects.

**Deletion test:** deleting `lib/db/` would spread its logic across every route
handler that currently calls it. It is earning its keep. Depth score: green.

`lib/api-client-react/` is a thin wrapper over the web client's API calls.
If it exists only to re-export fetch helpers that mirror the route signatures one-to-one,
it is a pass-through. **Deletion test:** deleting it would concentrate the import
into the components that use it — one change site. Candidate for deletion.

---

### Example 2: `artifacts/api-server/src/lib/` vs `artifacts/api-server/src/routes/`

`api-server/src/lib/` contains modules like `claude.ts`, `classifier.ts`,
`executor.ts`, `consensus.ts` — domain logic for the AI pipeline.

`api-server/src/routes/` contains modules like `ai.ts`, `auth.ts`, `dashboard.ts` —
HTTP boundary handling.

**The seam:** `routes/` should call into `lib/` for all business logic. If you
find HTTP-specific code (request parsing, status code selection, header reading)
inside `lib/`, that is a seam violation — the route concern has leaked inward.
Conversely, if `lib/claude.ts` imports from Express or reads `req.body`, the
isolation is broken.

**Dependency category:** `lib/claude.ts` talks to the Anthropic API — that is
a **true-external** dependency. An anti-corruption layer (the thin wrapper in
`lib/claude.ts` itself) is warranted to translate Anthropic's `Message` type
into CourierFlow's domain types before they propagate inward.

---

### Example 3: One-adapter-hypothetical in `lib/copilotkit-eval/`

`lib/copilotkit-eval/` contains evaluation harness code specific to the
CopilotKit integration. If this module defines an abstract `EvalRunner` interface
with a single concrete `CopilotKitEvalRunner` implementation, the interface adds
no value yet — there is one real implementation.

**Apply the two-adapters-real rule:** delete the abstract interface, keep the
concrete class. If a second eval runner (e.g. a direct Anthropic eval path) ships
in the future, extract the interface then — when both sides exist and the seam
pays for itself.

---

## When to Merge vs Split

**Merge when:**
- Two modules always change together (high coupling, low cohesion between them)
- Deleting one concentrates complexity into the other (one is a thin wrapper)
- The combined interface would be smaller than the sum of the parts

**Split when:**
- A single module has two distinct consumers that use disjoint subsets of its API
- One half of the module changes frequently; the other is stable — split to protect the stable half
- The module crosses a dependency-category boundary (in-process logic + remote call in one file)

**Do not split** to hit an arbitrary line-count target. A 600-line module with high
cohesion and a 4-method interface is better than two 300-line modules with a
tangled shared-state dependency.

---

*Source: adapted from `mattpocock/skills` `codebase-design` + `DEEPENING.md`, 2026-06-26.*

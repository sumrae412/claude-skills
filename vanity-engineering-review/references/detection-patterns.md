# Vanity Engineering Detection Patterns

## Category 1: Premature Abstraction

**Single-Implementation Interfaces** — Interface with exactly one concrete implementation.
Abstraction without variation is indirection. Use the concrete type directly. Extract an
interface when a second implementation actually materializes.
Severity: V1 (isolated), V2 (systemic)

**Plugin Systems with No Plugins** — Registration/discovery/loading for extensibility with
0-2 "plugins" all maintained by the same team. Plugin architecture is expensive; justified
only when third parties actually write plugins. Use direct function calls instead.
Severity: V2 minimum, V3 if other code must conform to the plugin API

**Generic-Everything** — Extensive generics where only 1-2 concrete types are ever used.
Use concrete types. Genericize when you add the second type.
Severity: V1

## Category 2: Resume-Driven Architecture

**Microservices at Monolith Scale** — Multiple services, mesh, gateway for <10 rps total.
Monolith with clean module boundaries. Deploy as one thing.
Severity: V3

**Kubernetes for a Single Container** — K8s manifests for one replica with no scaling needs.
Docker Compose or a systemd service.
Severity: V2

**Event-Driven for Synchronous Workflows** — Message queues for request-response flows that
need immediate results. Use function calls or HTTP requests.
Severity: V2

## Category 3: Complexity Theater

**Custom Implementations of Solved Problems** — Hand-rolled auth, ORM, state management,
logging where battle-tested alternatives exist. Use established libraries.
Severity: V2 (security-adjacent: V3)

**Configuration More Complex Than Code** — YAML/JSON config longer than the code it configures.
Use actual code: typed, debuggable, IDE-supported.
Severity: V2

**Elaborate Error Handling for Impossible Errors** — Try-catch for conditions that cannot
occur given actual inputs. Handle errors that can happen. Assert invariants. Let impossible
states crash.
Severity: V1

## Category 4: Gold Plating

**100% Test Coverage on Disposable Code** — Exhaustive tests for prototypes with explicit
expiry dates. Smoke tests for prototypes; invest in tests for code that will live.
Severity: V1

**CI/CD Overkill** — 15-stage pipeline for 1-3 person team deploying weekly. Git push +
deploy script. Graduate when frequency and team size justify it.
Severity: V1

**Premature Performance Optimization** — Caching, pooling, CDN for <100 rpm. Measure first.
Optimize only what is measurably slow.
Severity: V1 (isolated), V2 (if caching causes consistency bugs)

## Category 5: Over-Decomposition

**Fifty Files for Three Features** — Deep directories, one-function-per-file, barrel exports
everywhere. Co-locate related code. One file per feature is often correct under 300 lines.
Severity: V1 (mild), V2 (forces ceremony for every change)

**Premature DDD** — Aggregates, value objects, bounded contexts for 3-5 entities with CRUD.
Simple data models. Plain functions. Grow into DDD as domain proves complex.
Severity: V2

## Category 6: Type Tetris

**Type Definitions Longer Than Functions** — Conditional types, mapped types more complex than
the functions they annotate. Simpler types. Use `any`/`unknown` at boundaries where
elaborate types add no safety.
Severity: V1 (localized), V2 (if onboarding requires type system tutorial)

## Category 7: Framework Worship

**Choosing Tools for Interest Over Fit** — Tech choices that don't match team expertise or
project constraints but are trendy. Detection: "Why this tool?" If the answer references
blog posts rather than requirements, it is vanity.
Severity: V2 (V3 if team is fighting the tool)

## Compound Indicators

3+ patterns from different categories in the same codebase indicates systemic orientation
toward complexity, not individual bad decisions:

- **Abstraction stacking**: Interface -> Abstract -> Base -> Concrete for one behavior
- **Pattern collection**: Repository + Unit of Work + Specification + CQRS in one module
- **Infrastructure creep**: Docker + K8s + mesh + gateway + observability + feature flags
  for a private beta with 50 users

# Code Creation Workflow v2

A structured, phase-gated workflow skill for Claude Code that turns implementation requests into shipped code through discovery, architecture, TDD, review, and shipping — with automatic skill detection, parallel subagents, and built-in guardrails.

## What It Does

When you say "build X" or "fix Y", this workflow orchestrates the entire journey from understanding the request to shipping the code. It replaces the need to manually invoke brainstorming, planning, execution, and review skills by absorbing them all into a single coordinated pipeline.

## Workflow Diagram

```
                         User Request
                              |
                    +---------v----------+
                    |   Phase 0: Context |
                    |   Load project     |
                    |   identity + files  |
                    +---------+----------+
                              |
                    +---------v----------+
                    |  Phase 1: Classify  |
                    |  request into path  |
                    +--+---+---+---+-----+
                       |   |   |   |
            +----------+   |   |   +----------+
            |              |   |              |
     +------v-----+ +-----v---v--+    +------v------+
     | FAST PATH  | | BUG PATH   |    | PLAN PATH   |
     | Single-file| | Debug-first|    | Existing    |
     | change     | | via system-|    | plan file   |
     +------+-----+ | atic debug |    +------+------+
            |        +-----+------+          |
            |              |                 |
            |    +---------v----------+      |
            |    |  Phase 2: Explore  |      |
            |    |  + Skill Detection |      |
            |    |  + Memory Inject   |      |
            |    +---------+----------+      |
            |              |                 |
            |    +---------v----------+      |
            |    |  Phase 3: Require- |      |
            |    |  ments & Edge Cases|      |
            |    |  (3A + 3B BDD)    |      |
            |    +---------+----------+      |
            |              |                 |
            |    +---------v----------+      |
            |    |  Phase 4: Architec-|      |
            |    |  ture + Design Doc |      |
            |    |  + Debate Review   |      |
            |    +---------+----------+      |
            |              |                 |
            |        USER APPROVES           |
            |              |                 |
            |    +---------v----------+      |
            +---->  Phase 5: TDD     <------+
                 |  Implement (test   |
                 |  first per step)   |
                 +---------+----------+
                           |
                           | 3-Strike Rule:
                           | 3 failures on same
                           | step = STOP, question
                           | architecture
                           |
                 +---------v----------+
                 | Phase 6A: Quality  |
                 | Gate — reviews,    |
                 | CI, verification   |
                 +---------+----------+
                           |
                 +---------v----------+
                 | Phase 6B: Ship     |
                 | 1. Ship it [default]|
                 | 2. PR for review   |
                 | 3. Keep branch     |
                 | 4. Discard         |
                 +--------------------+
```

### Phase Summary

| Phase | Purpose | Key Mechanism |
|-------|---------|---------------|
| **0** | Load project context and file registry | Subagent loads core identity |
| **1** | Classify: Fast / Bug / Plan / Full | Routes to minimal viable path |
| **2** | Explore codebase + auto-detect skills | Parallel `code-explorer` subagents + skill trigger matching |
| **3** | Requirements (3A) + BDD edge cases (3B) | Hard gate — no architecture without requirements |
| **4** | Architecture (1-2 options) + design doc | `debate-team` auto-tiered review (T1/T2/T3) |
| **5** | TDD implementation per plan step | Test first -> implement -> green -> next step |
| **6A** | Quality gate: reviews, CI, verification | Scaled reviewers based on diff scope |
| **6B** | Ship or defer | Shipping workflow + cleanup + session-learnings |

### Automatic Skill Detection

During Phase 2, file patterns in the diff trigger domain-specific skills automatically:

| File Pattern | Auto-Loaded Skills |
|---|---|
| `*.html`, `*.css`, `*.js`, `templates/` | UI patterns + defensive UI flows |
| `routes/*`, `services/*` | API patterns + defensive backend flows |
| `models/*`, `alembic/*` | Data patterns + defensive backend flows |
| External API imports (twilio, openai, etc.) | API docs + integration patterns |
| Auth middleware, JWT, permissions | Security patterns |
| Always | Coding best practices (applicable subset) |

### Built-in Guardrails

- **3-Strike Rule**: 3 failures on the same step = stop coding, question the architecture
- **Hard Gates**: Requirements before architecture. Approval before implementation.
- **Red Flag Detection**: Self-checks for over-engineering, skipped phases, rationalization
- **Error Recovery**: Categorized responses (RETRY / PAUSE / DEGRADE) for every failure mode
- **User Signal Awareness**: Detects "can you just...", "that's not what I meant", etc. and adjusts

---

## Using This in Your Own Agent Framework

This workflow is framework-agnostic in design. It's implemented as a Claude Code skill (a markdown file that gets injected into context), but the pattern works anywhere you can give an LLM structured instructions.

### Option 1: Claude Code (native)

Drop the skill into your Claude Code skills directory:

```
~/.claude/skills/
  code-creation-workflow/
    SKILL.md              # Main workflow instructions
    references/
      skill-triggers.md   # File-pattern -> skill mapping
      error-recovery.md   # Failure mode -> resolution table
      memory-injection.md # Domain -> gotcha mapping from project memory
      red-flags.md        # Self-check rationalization detector
      common-mistakes.md  # Anti-patterns to avoid
      user-signals.md     # User frustration signal -> correction action
```

Register it in your `CLAUDE.md`:

```markdown
## Feature Work -> Use `/code-creation-workflow`

When asked to build, implement, add, create, or fix a feature,
use `/code-creation-workflow` as the primary orchestrator.
```

Invoke with `/code-creation-workflow` or let it trigger automatically on implementation requests.

### Option 2: Any LLM Agent (OpenAI Codex, Cursor, Aider, custom)

The workflow is just structured markdown instructions. To port it:

**1. Extract the phase instructions as your system/task prompt.**

Copy `SKILL.md` content into whatever prompt mechanism your framework uses (system message, tool description, task file, etc.).

**2. Map the subagent calls to your framework's equivalent.**

The workflow references subagents like `code-explorer`, `code-architect`, `code-reviewer`. Map these to your framework:

| Workflow Concept | Claude Code | OpenAI Codex | Cursor | Generic |
|---|---|---|---|---|
| Subagent | `Agent` tool with type | Separate API call with focused prompt | Composer with scoped context | Fork a new LLM call with narrowed context |
| Skill loading | `/skill-name` injects markdown | Append skill text to system prompt | Rules file or `.cursorrules` | Concatenate to prompt |
| Parallel dispatch | Multiple `Agent` calls in one turn | `Promise.all()` on API calls | Multiple composer tabs | Concurrent LLM calls |
| Memory injection | Read MEMORY.md, filter by domain | Read a project-notes file | `.cursor/memory` | Any persistent key-value store |
| Todo tracking | `TodoWrite` tool | Task list in conversation | Built-in task tracking | Structured output parsing |

**3. Adapt the reference files.**

The `references/` directory contains lookup tables the workflow consults at runtime:

- **`skill-triggers.md`** — Replace the CourierFlow-specific file patterns with your project's patterns. The concept (file pattern -> load domain knowledge) is universal.
- **`error-recovery.md`** — Reusable as-is. The failure modes (test failures, timeout, user wants to stop) are universal.
- **`red-flags.md`** and **`common-mistakes.md`** — Reusable as-is. These are meta-cognitive checks.
- **`user-signals.md`** — Reusable as-is. These are human interaction patterns.
- **`memory-injection.md`** — Replace the domain -> gotcha mapping with your project's known pitfalls.

**4. Implement the hard gates.**

The two critical gates that prevent wasted work:

```
Phase 3 -> Phase 4:  Requirements understood before architecture begins
Phase 4 -> Phase 5:  User approves plan before implementation begins
```

In any framework, these translate to: **do not proceed to the next phase without explicit user confirmation.** This is the single most important thing to preserve.

### Option 3: Minimal Portable Version

If you want the core pattern without CourierFlow specifics, here's the skeleton:

```markdown
# Implementation Workflow

## Classify Request
- FAST: Single-file, obvious change -> just do it + run tests
- BUG: Debug-first -> systematic debugging -> fix -> test
- FULL: Everything else -> full phases below

## Explore (parallel subagents)
- Dispatch 1-3 code explorers scaled to complexity
- Auto-detect which domain skills to load based on file patterns

## Requirements [HARD GATE]
- Confirm purpose, success criteria, constraints, scope boundary
- Generate 5-8 BDD scenarios (Given/When/Then)

## Architecture [HARD GATE - user approves]
- For non-trivial: present 2 options (simplicity vs separation)
- Write design doc with numbered implementation steps

## Implement (TDD per step)
- For each plan step: write failing test -> implement -> green
- 3-Strike Rule: 3 failures = stop, question architecture
- Parallel dispatch for 4+ independent steps

## Quality Gate
- Scale reviewers to scope (1-2 files = light, 3+ = full)
- Fix confirmed findings, reject false positives with evidence
- Run CI, verify all tests pass

## Ship
- Commit, push, PR, merge (or defer)
- Capture session learnings
```

---

## Key Design Decisions

**Why 4 paths instead of 1?** A typo fix shouldn't go through architecture review. A bug shouldn't go through requirements discovery. Path classification avoids ceremony overhead — the workflow scales down as aggressively as it scales up.

**Why parallel architects?** When you ask one architect, you get one design. When you ask two with different optimization targets (simplicity vs separation of concerns), you get a real trade-off to evaluate. The user picks, not the AI.

**Why TDD is a hard gate?** Writing tests after implementation leads to tests that verify the implementation rather than the requirements. Test-first ensures the tests encode the *intent*, and the implementation satisfies it.

**Why the 3-Strike Rule?** Three failed attempts at the same step almost always means the architecture is wrong, not the code. Continuing to iterate on code when the design is flawed wastes time exponentially. Stopping to question the design is the fastest path forward.

**Why session-learnings on every path?** Even fast-path changes can reveal project gotchas worth remembering. Capturing learnings after every shipped change builds institutional memory over time.

## License

MIT. Use it, adapt it, improve it.

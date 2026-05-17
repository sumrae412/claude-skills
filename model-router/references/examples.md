# Examples — Full Set

Six representative routing decisions covering every mode + tier in the router, plus three edge cases for ambiguous inputs. The compact `SKILL.md` keeps three of these inline (trivial, architectural, subagent-fleet); the rest live here, loaded on demand.

---

## Core examples (one per mode/tier)

### Example 1 — trivial → Haiku

> Task: Rename a variable in one file.
>
> ```
> 🎯 Model: Haiku 4.5 │ Mode: default │ Complexity: trivial
>    Why:    Single-file mechanical edit. Sonnet is 3× cost for zero recall gain.
>    Apply:  /model haiku
> ```

### Example 2 — simple → Sonnet

> Task: Fix a bug in the auth module.
>
> ```
> 🎯 Model: Sonnet 4.6 │ Mode: default │ Complexity: simple
>    Why:    Single-file bug fix in well-documented module. Haiku risks missing
>            async edge cases; Opus is overkill for one-file scope.
>    Apply:  /model sonnet
> ```

### Example 3 — complex → Sonnet

> Task: Add a new FastAPI endpoint touching 3 files (route, service, schema).
>
> ```
> 🎯 Model: Sonnet 4.6 │ Mode: default │ Complexity: complex
>    Why:    Multi-file new feature, no architectural decisions, established
>            patterns to follow. Sonnet is the sweet spot.
>    Apply:  /model sonnet
> ```

### Example 4 — architectural → Opus

> Task: Design a new auth system from scratch.
>
> ```
> 🎯 Model: Opus 4.7 │ Mode: think │ Complexity: architectural
>    Why:    System design with security implications. Reasoning depth and
>            edge-case coverage justify the 5× cost over Sonnet.
>    Apply:  /model opus     (consider effort: high for extended thinking)
> ```

### Example 5 — subagent fleet

> Task: Dispatch 5 explorer subagents for a codebase scan.
>
> ```
> 🎯 Model: Haiku 4.5 × 5 │ Mode: subagent-fleet │ Role: explorer
>    Why:    Explorer role, quality floor not triggered. 5× Haiku ≈ 1.7× Sonnet
>            in total cost — major savings on a parallel dispatch.
>    Apply:  pass `model: 'haiku'` to each subagent dispatch
> ```

### Example 6 — long context

> Task: Review an 80K-token diff.
>
> ```
> 🎯 Model: Sonnet 4.6 │ Mode: longContext │ Complexity: (skipped)
>    Why:    Context exceeds 60K threshold. Haiku quality drops on long inputs;
>            Opus is justified only if the review uncovers architectural concerns.
>    Apply:  /model sonnet
> ```

---

## Edge cases

### Edge case A — override fires despite low complexity score

> Task: Quick security audit on the JWT validator — should only take 5 minutes.
>
> ```
> 🎯 Model: Opus 4.7 │ Mode: default │ Complexity: simple (overridden)
>    Why:    Step 3 override fires on "security audit" — Opus regardless of
>            scope. Undercosting security work is the wrong failure mode.
>    Apply:  /model opus
>    Note:   The "quick" framing tempts Haiku/Sonnet, but security stakes win.
> ```

### Edge case B — mixed mode signals (longContext + subagent-fleet)

> Task: Dispatch 4 reviewers in parallel to audit an 80K-token diff for security regressions.
>
> ```
> 🎯 Mode: subagent-fleet │ Role: reviewer (security-audit) │ Models: per-agent
>    Per-agent: Opus 4.7 (security-audit floor — Haiku banned, Sonnet acceptable
>               but Opus recommended for security stakes)
>    Why:    First-match precedence puts longContext above subagent-fleet in
>            the mode table, BUT subagent-fleet routes per-agent so longContext
>            applies inside each subagent's choice (each reviewer gets a chunked
>            view of the diff, not the full 80K). Result: Opus × 4 for security
>            audit despite the long-context flag.
>    Apply:  4 Agent dispatches with `model: 'opus'`
>    Cost:   ~20× Haiku-explorer-fleet baseline — but security floor is hard.
> ```

### Edge case C — Plan-Mode candidate

> Task: Refactor the entire payment service to use the new transaction model. Plan it out, then execute.
>
> ```
> 🎯 Model: opusplan (Opus + Sonnet) │ Mode: think │ Complexity: architectural
>    Why:    Explicit plan-then-execute structure named in the task. Opus
>            designs the refactor and reviews diffs at checkpoints; Sonnet
>            handles the mechanical file edits. ~60% token savings vs full-Opus.
>    Apply:  /model opusplan  (or Option+P / Alt+P → "Use Opus in plan mode,
>            Sonnet otherwise")
>    Note:   Review Opus's plan before approving execution — refactors of this
>            scope catch their problems at the plan stage, not the diff stage.
> ```

---

## Adding new examples

When a real routing decision surprises you (the algorithm produced an unexpected answer, or a new mode/signal pattern came up), add it here with the prompt, the routing output, and a one-line "what was surprising about this." Over time this file becomes the calibration corpus — if patterns emerge (e.g., "the algorithm keeps misrouting CLI tool tasks as simple when they're actually complex"), that's a signal to revisit the weighted-signal table in `signal-scoring.md`.

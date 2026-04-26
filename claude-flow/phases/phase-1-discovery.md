# Phase 1: Discovery

<!-- Loaded: after Phase 0 | Dropped: after path selection and transition -->

Understand the request and select the workflow path.

Canonical path metadata lives in `../workflow-profiles.json` and
`references/workflow-profiles.md`.

Use the first matching route:

1. **Bug** -> invoke `/bug-fix`, exit `claude-flow`
2. **Fast** -> inline change, targeted test, finish
3. **Plan** -> read existing plan, start at Phase 5
4. **Clone** -> adapt an existing near-identical feature, start at Phase 5
5. **Lite** -> run phases 2-6 with inline architecture
6. **Audit** -> read-only assessment path, skip Phase 5
7. **Explore** -> sandbox spike, graduate later if it earns it
8. **Else** -> full workflow

## Path Criteria

- **Direct-route (skip workflow):** Some requests match a dedicated skill better than any workflow path. Route without entering Phase 2+:
  - "synthetic beta test &lt;app&gt;", "alpha test with personas", "assess usability with simulated users", "run persona-based eval" -> `/personas`
- **Bug path:** error report, regression, stack trace, "fix this bug", GitHub issue tagged as bug
- **Fast path:** typo fix, one-line change, config tweak, or contained single-file edit with no ripple effects
- **Plan path:** an existing plan file or PRP already exists for this feature
- **Clone path:** Feature X already exists and you are building Feature X'
- **Lite path:** contained change touching 1-2 files and not worth the full architecture loop
- **Audit path:** read-only assessment. Trigger words: "audit", "review existing code", "codebase health", "tech debt", "cleanup", "tidy up", "dead code", "consolidate", "find issues in". Pick a subflow from `references/audit-subflows.md`.
- **Explore path:** spike, prototype, experiment, or proof of concept. Quality bar is 60/100 and Phase 6 is skipped until graduation.
- **Full workflow:** everything else. If in doubt, use full.

## Artifact Requirements by Scale

| Path | Files Touched | PRP | Design Doc | Work Plan | Test Skeletons | Review Tiers |
|------|---------------|-----|------------|-----------|----------------|--------------|
| **Audit** | N (read-only) | No | No | No | No | Tier 1-3 (file-list mode) |
| **Bug** | 1-5 | No | No | No | No (test in Step 1) | Tier 1-3 (via /bug-fix) |
| **Fast** | 1 | No | No | No | No | Tests only |
| **Clone** | 1-3 | No | No | Inline | No | Tier 1-2 |
| **Lite** | 1-2 | No | Inline | Inline | No | Tier 1-3 |
| **Full** | 3+ | Optional | Yes | Yes | Yes (Phase 4d) | All tiers |

**Reading the table:**

- "Inline" means the artifact is written directly in the conversation.
- "Test Skeletons" refers to Phase 4d acceptance-test generation.
- PRP is optional even on Full path; export only when the feature spans
  sessions or has multiple integration points.

## After Choosing the Path

1. Set `current_phase.path` if workflow state is already active.
2. If the chosen path's profile has `state_machine: true` and no state file
   exists yet, load `references/workflow-state-lifecycle.md` and initialize it.
3. Transition using the canonical map in `../workflow-profiles.json`.

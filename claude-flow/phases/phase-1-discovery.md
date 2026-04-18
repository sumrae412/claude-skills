# Phase 1: Discovery

<!-- Loaded: after Phase 0 | Dropped: after path selection and transition -->

Understand the request and decide the workflow path.

```
User says "implement X" / "fix Y"
        │
        ▼
   ┌─────────────────────────────────────────────┐
   │ Is this a BUG FIX?                           │
   │ (error report, regression, "broken",         │
   │  stack trace, bug issue reference)            │
   │                                               │
   │ YES → BUG PATH                                │
   │   Invoke /bug-fix skill                       │
   │   (Reproduce → Diagnose → Fix → Verify)       │
   │                                               │
   │ Is this a SMALL change?                      │
   │ (single file, no schema, no new endpoints)   │
   │                                               │
   │ YES → FAST PATH                               │
   │   1. Load defensive skill                     │
   │   2. Make the change                          │
   │   3. Run tests                                │
   │   4. Commit → done                            │
   │                                               │
   │ Has EXISTING PLAN file or PRP?                │
   │                                               │
   │ YES → PLAN PATH                               │
   │   1. Read the plan/PRP file                   │
   │   2. Skip to Phase 5 (Implementation)         │
   │   3. Execute the plan                         │
   │                                               │
   │ Is there a NEAR-IDENTICAL existing feature?   │
   │ (quick grep/glob check — 2-3 searches max)    │
   │                                               │
   │ YES → CLONE PATH                              │
   │   1. Read the existing feature code           │
   │   2. Clone + adapt (skip Phases 2-4)          │
   │   3. TDD the differences                      │
   │   4. Run Phase 6 review → done                │
   │                                               │
   │ Does this touch ONLY 1-2 files?               │
   │ (no new endpoints, no schema, no new models)  │
   │                                               │
   │ YES → LITE PATH                               │
   │   1. Read the files directly (skip Phase 2    │
   │      parallel explorers)                      │
   │   2. Inline architecture (skip Phase 4        │
   │      parallel architects — write plan inline) │
   │   3. TDD implementation                       │
   │   4. Run Phase 6 review → done                │
   │                                               │
   │ Is this an AUDIT or CLEANUP request?          │
   │ ("audit", "review existing code", "codebase   │
   │  health", "tech debt", "cleanup", "tidy up",  │
   │  "dead code", "find issues in", "consolidate")│
   │                                               │
   │ YES → AUDIT PATH (read-only)                  │
   │   1. Phase 1: scope → $audit_scope            │
   │   2. Phase 2: exploration                     │
   │   3. Phase 3: audit criteria → $requirements  │
   │   4. Phase 4: assessment → $assessment        │
   │   5. Phase 6: review cascade (file-list mode) │
   │   6. Report → docs/audits/<date>-<topic>.md   │
   │   Subflow selection (references/audit-       │
   │   subflows.md):                               │
   │     - Noisy log input → Subflow A             │
   │     - Cleanup/tidy/dead-code → Subflow C      │
   │   No Phase 5 — read-only.                     │
   │                                               │
   │ Is this EXPLORATORY?                          │
   │ ("try this", "experiment with", "spike",      │
   │  "prototype", "proof of concept",             │
   │  "see if X works")                            │
   │                                               │
   │ YES → EXPLORE PATH                            │
   │   1. Create explorations/<topic>/ directory   │
   │   2. Write README.md (goal, hypothesis,       │
   │      success criteria)                        │
   │   3. Code freely — no TDD, no Phase 6 review │
   │   4. Defensive patterns still loaded,         │
   │      secret detection + lint still active     │
   │   5. At decision point:                       │
   │      a. Graduate → full workflow from Phase 4 │
   │         (exploration = Phase 2 input)         │
   │      b. Archive → /session-handoff --abandon  │
   │                                               │
   │ NO to all → FULL WORKFLOW (continue)           │
   └─────────────────────────────────────────────┘
```

## Path Criteria

- **Direct-route (skip workflow):** Some requests match a dedicated skill better than any workflow path. Route without entering Phase 2+:
  - "synthetic beta test &lt;app&gt;", "alpha test with personas", "assess usability with simulated users", "run persona-based eval" → `/personas` (standalone 6-phase pipeline for simulated user testing).
- **Bug path:** Error report, regression, stack trace, "fix this bug", GitHub issue tagged as bug. Routes to `/bug-fix` skill — the dedicated bug fix orchestrator.
- **Fast path:** Typo fix, one-line change, config tweak, single-file edit with no ripple effects.
- **Plan path:** An existing plan file or PRP already exists for this feature — skip directly to Phase 5.
- **Clone path:** Feature X already exists and you're building Feature X' (e.g., "add a delete endpoint" when create/update endpoints already exist).
- **Lite path:** Contained change touching 1-2 files — doesn't justify 5+ parallel subagents.
- **Audit path:** Read-only assessment. Trigger words: "audit", "review existing code", "codebase health", "tech debt", "cleanup", "tidy up", "dead code", "consolidate", "find issues in". Skips Phase 5 (no code changes); output is a prioritized checklist in `docs/audits/`. Pick a subflow from `references/audit-subflows.md`: A for noisy-log inputs, C for cleanup-style multi-dimension scans (with deletion-safety + AI-artifact dimension + cross-dim coordination gate). See `audit_path.md` memory for the full contract flow.
- **Explore path:** User wants to test an idea before committing to the full workflow. Signals: "try this", "experiment with", "spike", "prototype", "proof of concept", "see if X works". Quality bar is 60/100 (no TDD, no Phase 6 review). Graduation: "this works, let's ship it" → exploration findings become Phase 2 input, skip parallel explorers, flow into normal pipeline from Phase 4. Archive: invoke `/session-handoff --abandon` to document what was tried and why it was abandoned.
- **Full workflow:** Everything else. If in doubt, use the full workflow.

## Artifact Requirements by Scale

Each path produces different artifacts. This table makes explicit what each path requires:

| Path | Files Touched | PRP | Design Doc | Work Plan | Test Skeletons | Review Tiers |
|------|---------------|-----|------------|-----------|----------------|--------------|
| **Audit** | N (read-only) | No | No | No | No | Tier 1-3 (file-list mode) |
| **Bug** | 1-5 | No | No | No | No (test in Step 1) | Tier 1-3 (via /bug-fix) |
| **Fast** | 1 | No | No | No | No | Tests only |
| **Clone** | 1-3 | No | No | Inline | No | Tier 1-2 |
| **Lite** | 1-2 | No | Inline | Inline | No | Tier 1-3 |
| **Full** | 3+ | Optional | Yes | Yes | Yes (Phase 4d) | All tiers |

**Reading the table:**
- "Inline" means the artifact is written directly in the conversation, not as a separate doc.
- "Test Skeletons" refers to Phase 4d acceptance test generation (Full path only — smaller changes don't benefit from pre-generated skeletons).
- PRP is optional even on Full path — only export when the feature spans sessions or has 3+ integration points.

## State Transition

Update `.claude/workflow-state.json` — set `current_phase.path` to the selected path (`fast`/`clone`/`lite`/`full`/`plan`/`bug`/`explore`/`audit`), then transition to the appropriate next phase.

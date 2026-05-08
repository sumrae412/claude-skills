---
name: prd
description: Use when authoring a Product Requirements Document (PRD) — a sharable spec doc — before handing a feature to claude-flow or another AI coding agent. Triggers on "write/draft/create a PRD", "spec out [feature]", "product spec", "feature spec", "write product requirements", "requirements doc for [feature]", "PRD for [feature]". The PRD output maps directly onto claude-flow's $requirements contract (user stories, EARS acceptance criteria, scope.in/out, edge cases, risk class, non-functional) so Phase 3 can ingest it instead of re-asking the same questions. Distinct from claude-flow's inline Phase 3 — use this when the PM / founder / requester wants a durable spec document up front that survives across sessions, before kicking off the build.
user-invocable: true
metadata:
  hermes:
    tags: [planning, requirements, product, prd, claude-flow]
    related_skills: [claude-flow, brainstorming, writing-plans]
---

# PRD — Product Requirements Document

## What this produces

A markdown PRD at `docs/prds/prd-<slug>.md`. The structure maps onto claude-flow's `$requirements` contract (stories, AC-N EARS clauses, scope.in/out, edge_cases, risk_class) so when you run `/claude-flow` next, Phase 3 reads the PRD and skips the questions you've already answered.

If the PRD is going to a separate AI coding agent (not claude-flow), use the **AI-agent variant** in `references/ai-agent-variant.md` — adds file paths, API contracts as code blocks, and a build sequence.

## When to use

- A PM / founder / requester wants a sharable spec before the build starts
- The feature spans multiple sessions or hand-offs
- You want a durable artifact (decisions, scope-out, success metrics) that outlives the build conversation
- The audience is whoever needs to act on the spec — PM, eng, or AI agent. The skill asks technical-but-accessible questions about scope, risk, and edges. The PRD's primary downstream consumer is usually a coding agent (claude-flow, Codex, a separate Claude Code session), but the document is structured so a human reviewer can also approve or hand it off.

**Don't use** for: bug fixes (use `/bug-fix`), one-line tweaks, or features small enough to fit inline in a single claude-flow session.

## Workflow

### 1. Mode detection

Before asking anything, check the working directory:

- **Greenfield** — no source files or build manifests yet (no `package.json`, `pyproject.toml`, `pom.xml`, `build.gradle`, `Cargo.toml`, `go.mod`, `Gemfile`, `*.csproj`, `composer.json`, `src/`, `app/`, `lib/`, `cmd/`). Stack decisions are open.
- **Feature mode** — existing codebase. The stack is already set; don't re-recommend it. PRD describes integration points, not a standalone shape.

If you can't tell, ask: "Greenfield project, or adding to an existing codebase?"

### 2. Lettered clarifying questions (3-5)

Ask only the questions that would change the spec. Use lettered options so the user can respond `1A, 2C, 3B`. Pick from `references/discovery-questions.md` based on what's missing — don't ask all of them.

Stop-asking rule lives in `references/discovery-questions.md` § "When to stop asking" — once the template can be filled without `<TBD>` in any non-optional field, write the PRD. Anything still ambiguous goes to **Open Questions**, not another round of asking.

**Self-answer first:** before asking, check the codebase for anything you can resolve yourself (existing patterns, framework choices, naming conventions). Only ask the user about intent, preference, and policy.

### 3. Risk class flag

While drafting, decide if the feature touches `auth`, `privacy`, `money`, `data_loss`, `external_side_effects`, or `public_api`. If yes, the PRD's **Risk Class** section names the flags. claude-flow uses this to force the change onto the full path even if the diff looks small.

### 4. Generate the PRD

Load `references/template.md` and fill it. The template's section IDs (`## User Stories`, `## Acceptance Criteria`, `## Scope`, etc.) match `$requirements` field names so Phase 3 can ingest by section heading.

Write to `docs/prds/prd-<slug>.md` where `<slug>` is kebab-case of the feature name. Create `docs/prds/` if it doesn't exist.

### 5. Final check

Walk the PRD against this list before declaring done:

- [ ] Every user story has at least one AC-N acceptance criterion in EARS format (`WHEN ... [IF ...] THEN ...`)
- [ ] Acceptance criteria are testable — no "works correctly", "fast", "intuitive"
- [ ] **Scope > Out** has at least 2 items (forces explicit scope-creep prevention)
- [ ] **Risk Class** is named with flags or explicitly marked `low / no flags`
- [ ] **Definition of Done > Global Gates** lists project-specific commands (typecheck / lint / tests) — the placeholders are filled in
- [ ] **Definition of Done > Per-Story Verification** has at least 2 concrete checks per US-N (happy path + at least one error/edge)
- [ ] **Open Questions** lists anything you couldn't resolve, tagged with who should answer (eng / design / legal / data / stakeholder)
- [ ] Could a separate coder, with no access to this conversation, build this from the doc alone? If no, fix the gap.

### 6. Hand off

Print the path and one-line next step:

```
PRD saved to docs/prds/prd-<slug>.md
Next: run /claude-flow — Phase 3 will pick up the PRD automatically.
```

If the PRD is going to a separate AI coding agent (Codex, another Claude Code session) instead of claude-flow, hand it the file path and tell them to read it first.

## Hand-off contract with claude-flow

claude-flow Phase 3 Step 0 reads `docs/prds/prd-*.md` if present and pre-populates `$requirements` from it. Phase 3 will still:

- Run the self-answerable-question audit on any remaining gaps
- Ask the user about ambiguities the PRD didn't resolve
- Apply the risk-class gate if `risk_class.level == high`

So the PRD doesn't replace Phase 3 — it shortcuts it. The cleaner the PRD, the less Phase 3 has to ask.

## Output structure (cheat sheet)

```
docs/prds/prd-<slug>.md
├── Problem Statement      → context, not part of $requirements
├── Goals & Success Metrics → context, not part of $requirements
├── User Stories            → $requirements.stories
├── Acceptance Criteria     → $requirements.acceptance_criteria (EARS)
├── Scope (In / Out)        → $requirements.scope.in / .out
├── Edge Cases              → $requirements.edge_cases
├── Risk Class              → $requirements.risk_class
├── Non-Functional          → $requirements.nonfunctional (optional)
├── Definition of Done      → context, used by Phase 5/6 not Phase 3
│   ├── Global Gates           → cross-cutting checks (typecheck/lint/tests/docs)
│   └── Per-Story Verification → concrete check steps per US-N
└── Open Questions          → tagged by responsible party
```

## What NOT to include

- File paths, code snippets, implementation steps (those belong in `$plan` from Phase 4, not the PRD — exception: AI-agent variant)
- Design mockups (link to them; don't inline)
- Vague success metrics ("improve UX" → "reduce time to first value from 90s to 30s")
- Internal jargon without definitions
- More than 5 must-have features for v1 (split into v2 if you have more)

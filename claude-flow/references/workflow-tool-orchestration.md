# Workflow-tool-backed orchestration (optional execution mode)

<!-- Loaded: only when the orchestrator opts a phase into Workflow-tool execution. Not resident. -->

This reference describes an **optional** way to back specific claude-flow phases
with the Claude Code **Workflow tool** — the `agent()` / `parallel()` /
`pipeline()` primitive that holds multi-agent control flow in deterministic
JavaScript. It is opt-in. The default execution model for every phase remains
the prose flow in the phase files; nothing here changes that unless the
orchestrator deliberately invokes a workflow.

## Disambiguation — two unrelated things both called "workflow"

| Term | What it is | Where it lives |
|---|---|---|
| **workflow profile** | A claude-flow *execution path* (`fast`, `lite`, `full`, `audit`, …) selecting phase sequence + review budget | `workflow-profiles.json` |
| **Workflow tool** | The Claude Code primitive that runs a JS script orchestrating subagents with deterministic control flow | The `Workflow` tool, this doc |

They are **not** related. A workflow profile is still chosen the same way. This
doc only concerns the Workflow *tool*.

## When backing a phase with the Workflow tool earns its cost

The Workflow tool's value is **executed control flow** — loops, branches, and
fan-out the script guarantees, instead of prose the model is *trusted* to
follow. Reach for it on a phase only when all of these hold:

- The phase has real fan-out (≥3 parallel agents) or a real loop (iterate-until-verified).
- The control flow is currently expressed as prose the model under-executes (e.g. "emit N tool-use blocks in one message" — Opus 4.x under-parallelizes).
- The phase span has **no mid-run human gate** (see the hard constraint below).
- The session is interactive (not headless CI — saved workflows run inside a Claude Code session only; `claude -p` follows the configured allowlist with no prompt).

If any fail, stay with the prose flow.

## Hard constraints (these come from the pipeline's own invariants)

1. **Human ship/no-ship gates stay OUTSIDE the workflow.** The Workflow tool cannot take mid-run user input — only per-agent permission prompts can pause it. Phase 3 requirements clarification, Phase 4 option selection, and the Phase 6 ship/no-ship decision must remain conversation turns. Run a workflow for the *automatable span* of a phase, then return to the conversation for the gate.
2. **Memory-injection is the first stage.** Any workflow that dispatches a code-touching agent MUST run `memory-injection` first (cross-cutting policy — see `memory-injection.md`). Encode it as a hard first `agent()` call whose output feeds every later prompt, or the cross-session gotcha safety net breaks.
3. **Within-session only — keep `run_manifest.py` as durable state.** Workflow resume works only within the same Claude Code session; exiting restarts fresh. claude-flow's run manifest + `workflow-state.json` are the durable cross-session record (handoff docs, paused sessions). Do not delete them in favor of workflow resume — the workflow is a within-session execution accelerator, not the state store. Persist manifest records from the conversation after the workflow returns.
4. **Deterministic leaves shell out — never reimplement as agents.** `select_reviewers.py`, `aggregate_reviewer_findings.py`, `resolve_review_base.py`, `orchestrate.py scrub-diff` (and `triage.ts`-style dedup) are Rule-5 deterministic surfaces. A workflow agent is still a model; routing dedup / path-resolution / severity-sort / budget math through one reintroduces the variance, cost, and latency the pipeline deliberately removed. Have a shell-capable agent **call** these scripts and parse their JSON; do not ask a model to do their job.
5. **Research-preview gating.** The Workflow tool is gated (paid plan, recent CLI). If unavailable, the prose flow is the fallback — it is never a hard dependency.

## Antipatterns (do NOT do these)

- **Do not convert the whole Phase 0–6 pipeline into one monolithic workflow.** Its defining value is the human checkpoints between stages; a monolith strips exactly those.
- **Do not use a workflow on fast / clone / lite paths or single-file changes.** The FAST PATH exists to avoid orchestration overhead; a workflow inverts its purpose and costs meaningfully more tokens.
- **Do not author against guessed primitive signatures.** Inspect a generated/saved workflow script (the Workflow tool persists every run's script under the session dir) before relying on an API shape.

---

## Template A — Phase 6 reviewer cascade (rec #4)

Backs the **automatable span** of the Phase 6 cascade (`phase-6-quality.md` →
Risk-Budgeted Cascading Review, steps 4–12): deterministic selection, Tier-1-gated
early exit, parallel per-tier fan-out, scored aggregation. The review-base resolve,
diff scrub, manifest persistence, and the **ship/no-ship gate** stay in the
conversation around it.

```javascript
export const meta = {
  name: 'claude-flow-phase6-cascade',
  description: 'Tier-gated, budget-bounded reviewer cascade for the automatable span of Phase 6',
  phases: [{ title: 'Inject' }, { title: 'Tier1' }, { title: 'Cascade' }, { title: 'Aggregate' }],
}

// args = { skillRoot, reviewBaseSha, workflowPath, scrubbedDiffPath, requirements }

phase('Inject')
// Constraint 2 — memory-injection is the hard first stage before any code-touching agent.
const gotchas = await agent(
  `Run the memory-injection skill for this diff's domain. Return the gotcha block to prepend to every reviewer prompt. Diff base: ${args.reviewBaseSha}.`,
  { label: 'memory-injection', phase: 'Inject' }
)

// Constraint 4 — selection is deterministic; a shell agent CALLS select_reviewers.py, it does not judge.
const SELECTION_SCHEMA = { type: 'object', additionalProperties: true, required: ['by_tier', 'review_budget', 'budget_skipped'], properties: {
  by_tier: { type: 'object', additionalProperties: true },
  review_budget: { type: 'string' },
  budget_skipped: { type: 'array', items: { type: 'string' } },
} }
const selection = await agent(
  `Run: git diff --name-only ${args.reviewBaseSha}..HEAD | python3 ${args.skillRoot}/scripts/select_reviewers.py --workflow-path ${args.workflowPath}. Return its JSON verbatim.`,
  { label: 'select_reviewers', phase: 'Inject', schema: SELECTION_SCHEMA }
)

phase('Tier1')
const FINDINGS_SCHEMA = { type: 'object', additionalProperties: false, required: ['findings'], properties: {
  findings: { type: 'array', items: { type: 'object', additionalProperties: true, required: ['severity', 'file', 'description'], properties: {
    severity: { type: 'string', enum: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'NITPICK'] },
    file: { type: 'string' }, line: { type: ['integer', 'null'] }, description: { type: 'string' },
  } } },
} }
const reviewerPrompt = (role) =>
  `${gotchas}\n\nACCEPTANCE CRITERIA (defined pre-implementation, Phase 3):\n${args.requirements}\n\n${role}\nReview the scrubbed diff at ${args.scrubbedDiffPath}. Format findings as [SEVERITY] file:line — description.`

const tier1 = await agent(reviewerPrompt('You are the consolidated first-pass reviewer (coderabbit tier).'),
  { label: 'tier1:coderabbit', phase: 'Tier1', agentType: 'coderabbit:code-reviewer', schema: FINDINGS_SCHEMA })

// Step-7 early-exit becomes a SCRIPT branch, not a model branch.
const tier1HighPlus = tier1.findings.filter(f => f.severity === 'CRITICAL' || f.severity === 'HIGH')
let cascade = []
if (tier1HighPlus.length > 0) {
  phase('Cascade')
  // by_tier order, parallel within a tier. Each entry carries its agentType + role.
  const tier2 = Object.entries(selection.by_tier).flatMap(([, members]) => members)
  cascade = (await parallel(tier2.map(m => () =>
    agent(reviewerPrompt(m.role ?? `You are ${m.id}.`),
      { label: `cascade:${m.id}`, phase: 'Cascade', agentType: m.subagent_type, schema: FINDINGS_SCHEMA })
      .then(r => ({ id: m.id, findings: r.findings }))
  ))).filter(Boolean)
}

phase('Aggregate')
// Constraint 4 again — aggregation/dedup is deterministic. Hand the raw findings
// back to the conversation, which runs aggregate_reviewer_findings.py and persists
// the manifest. The workflow returns DATA; it does not ship.
return {
  tier1: tier1.findings,
  cascade,
  budgetSkipped: selection.budget_skipped, // Rule 12 — surfaced, not dropped
  reviewBudget: selection.review_budget,
}
```

After the workflow returns: run `aggregate_reviewer_findings.py`, the
review-fix-recheck loop (`phase-6-review-operations.md`), the Verification Ladder,
manifest `record-review` / `record-command`, then the **conversation** handles
`/ship`'s ship/no-ship decision.

## Template B — goal-mode iterate-until-verified loop (rec #5)

Backs the Phase 5 (or Phase 6) goal-mode loop with a **real** loop guard: the
script holds the iteration counter and a deterministic verification agent that
*runs the success command* and parses its exit code — the pass/fail is the loop
condition in code, not a small-model judgement. Scope it to **one** goal span and
hand back to the conversation between goals (Constraint 1).

```javascript
export const meta = {
  name: 'claude-flow-goal-loop',
  description: 'Iterate-until-verified for ONE goal span with a deterministic test-gate loop condition',
  phases: [{ title: 'Iterate' }],
}
// args = { skillRoot, successCommand, maxTurns, taskBrief }

phase('Iterate')
const VERIFY_SCHEMA = { type: 'object', additionalProperties: false, required: ['exitCode', 'newSkips'], properties: {
  exitCode: { type: 'integer' },
  newSkips: { type: 'integer', description: 'count of pytest.skip/xfail added this iteration (anti-cheat)' },
} }
let iter = 0
let verdict = { exitCode: 1, newSkips: 0 }
while (iter < args.maxTurns) {
  iter++
  await agent(`Iteration ${iter}. ${args.taskBrief}\nMake the smallest change that moves toward: ${args.successCommand} exiting 0.`,
    { label: `fix:iter-${iter}`, phase: 'Iterate' })
  // Deterministic gate — a shell agent RUNS the command and reports exit code.
  // The model does not get to declare success; the exit code does.
  verdict = await agent(
    `Run exactly: ${args.successCommand}. Report its integer exit code. Also run: git diff -U0 | grep -cE '^\\+.*(pytest\\.skip|xfail)' (default 0). Return both. Do not edit anything.`,
    { label: `verify:iter-${iter}`, phase: 'Iterate', schema: VERIFY_SCHEMA })
  if (verdict.exitCode === 0 && verdict.newSkips === 0) break // achieved
}
return {
  status: verdict.exitCode === 0 && verdict.newSkips === 0 ? 'achieved' : 'budget_exhausted',
  iterations: iter,
  finalExitCode: verdict.exitCode,
  newSkipsIntroduced: verdict.newSkips, // Rule 12 — surfaced; non-zero blocks "achieved"
}
```

After the workflow returns: the conversation records the terminal action via
`run_manifest.py record-goal` (`achieved` / `budget_exhausted`) and runs the
human ship gate. A `budget_exhausted` return is reported loud, never as success.

## Saving a template as a named workflow

Drop either template into `.claude/workflows/<name>.js` in the target project to
make it invocable as a named workflow (`Workflow({ name: '<name>', args })`), or
invoke it ad hoc via `Workflow({ scriptPath: '<path>', args })`. The templates
above are starting points — adapt `agentType` values and script paths to the
project's registered subagents and the resolved `<claude-flow-root>`.

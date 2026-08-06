# High-Risk Red/Blue/Green Plan Review

Use this protocol for implementation plans with high risk or explicit review
authority. It is a review procedure, not permission to implement or ship.

## Inputs

- `$spec` - the durable specification and its requirement/acceptance IDs
- `$requirements` - clarified scope, edge cases, and risk class
- `$plan` - the proposed architecture, tasks, constraints, and success contracts

## Roles and isolation

### Red Team - discover

Read the inputs cold. Find realistic ways the plan could fail, confuse users,
create risk, or be misused. Do not propose a broad redesign. Every finding
must cite evidence from the spec, plan, codebase, or governing constraint and
name the affected `FR-*`, `NFR-*`, or `AC-*` ID.

### Blue Team - adjudicate

Read the Red findings and the same plan. Rank each finding:

- **P0:** safety, authorization, data-loss, or irreversible external-impact
  blocker; plan cannot proceed.
- **P1:** material acceptance, scope, or reliability gap; revise before approval.
- **P2:** bounded weakness worth recording; may proceed only if the acceptance
  contract remains honest.
- **P3:** informational; no plan change required.

Blue explains why the severity matters and whether the finding blocks approval.
Blue does not edit the plan.

### Green Team - revise

The plan author addresses P0/P1 findings and any P2 finding that affects an
acceptance claim. Green preserves the original goal and tone, changes only the
affected sections, and does not silently widen scope. If a fix requires a new
requirement or a changed user decision, return to the approval gate.

## Output contract

Every finding, including a finding closed as immaterial, uses this sequence:

```text
finding → evidence → severity → acceptance impact → scoped revision → re-check
```

- **Finding:** concise failure or misuse case.
- **Evidence:** exact spec ID, file/line, command output, or governing rule.
- **Severity:** P0-P3 with one-sentence rationale.
- **Acceptance impact:** the affected requirement/acceptance ID and whether it
  blocks approval.
- **Scoped revision:** exact plan section/task/constraint changed, or `none`.
- **Re-check:** command or inspection that proves the revision closes the
  finding; `unverified` is not closure.

## Completion rules

- Red, Blue, and Green are separate passes. One prompt pretending to be three
  independent reviewers does not satisfy the protocol.
- Green is not the verifier. A fresh verifier performs the final re-check.
- A P0/P1 finding with no passing re-check remains open.
- A finding that can only be fixed by changing requirements or scope returns to
  the user approval gate.

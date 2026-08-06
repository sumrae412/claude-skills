# $requirements
<!-- Produced by: Phase 3 | Consumed by: Phases 4, 4c, 5, 6 reviewers -->

## Schema

stories:
  - role: string
    want: string
    benefit: string

acceptance_criteria:    # EARS format — these become the Phase 4c coverage checklist
  - id: AC-N
    when: string
    if: string          # optional condition
    then: string

scope:
  in: string[]          # explicitly included
  out: string[]         # explicitly excluded — enforced as scope-creep detection

edge_cases:
  - case: string
    resolution: string

risk_class:
  level: low | medium | high
  flags: string[]       # auth | privacy | money | data_loss | external_side_effects | public_api
  rationale: string

nonfunctional:          # optional
  - type: string        # performance | backward_compat | security
    constraint: string

reference_exemplar:     # optional — a named best-in-class artifact the deliverable is graded against
  name: string          # what it is: product, page, component, document
  locator: string       # URL, vendored path, or screenshot path — MUST be inspectable at review time
  dimensions: string[]  # the axes on which "better" is judged; scoring is confined to these

## Notes

- Populated after user approves requirements in Phase 3
- acceptance_criteria is the primary input for Phase 4c coverage mapping
- scope.out items are enforced in Phase 4c as scope-creep detection
- risk_class forces path/review escalation when the change can affect
  authentication, privacy, money movement, data loss, external side effects,
  or public API contracts
- Phase 6 reviewers receive only acceptance_criteria (not full contract) for payload slimming
- reference_exemplar is optional and omitted by default. Populate it only when
  the deliverable has a public best-in-class equivalent that a reviewer can
  actually open. An exemplar that cannot be inspected at review time is worse
  than none — it invites the reviewer to grade against a remembered impression.
  When present, Phase 6 runs the Exemplar Benchmark
  (`references/phase-6-review-operations.md`); when absent, Phase 6 is unchanged.

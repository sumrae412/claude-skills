# PRD Template

Structure for generating a Product Requirements Document from research output. Designed for speed — a complete PRD in 5 minutes, not 5 days.

## Document Structure

```markdown
# PRD: [Product Name]

**Date**: [date]
**Author**: [name]
**Status**: Draft — Generated via Product Sprint

---

## 1. Problem Statement

[2-3 sentences connecting the problem to real user evidence from Stage 1 research]

**Evidence**: [Key quote or data point from the debate that proves this problem is real]

---

## 2. Target Users

**Primary**: [Job title / situation / pain level — from user's answer to targeted question]

**Secondary** (if applicable): [Adjacent user who benefits but isn't the primary buyer]

**Anti-target**: [Who this is NOT for — prevents scope creep]

---

## 3. Key Constraint

[The ONE constraint that shapes all decisions — budget, timeline, platform, regulation]

**Implication**: [How this constraint affects feature scope and architecture]

---

## 4. Feature Prioritization (MoSCoW)

### Must Have (MVP — ship without these = no product)
| Feature | Rationale | Source |
|---------|-----------|--------|
| [Feature] | [Why it's essential] | [Debate round that proved it] |

### Should Have (v1.1 — add within first quarter)
| Feature | Rationale |
|---------|-----------|
| [Feature] | [Why it matters but isn't MVP] |

### Could Have (Backlog — nice but not critical)
| Feature | Rationale |
|---------|-----------|
| [Feature] | [Why it's interesting but deferrable] |

### Won't Have (Explicitly excluded)
| Feature | Reason for exclusion |
|---------|---------------------|
| [Feature] | [Why it's out of scope — often from Stage 1 debate] |

---

## 5. Success Metrics

**Primary metric**: [The ONE metric from user's answer — e.g., "10% reduction in churn within 90 days"]

**Leading indicators** (early signals the metric will move):
- [Indicator 1]
- [Indicator 2]

**Guardrail metrics** (things that must NOT get worse):
- [Guardrail 1]

---

## 6. Domain Framework Alignment

[Only include if user provided domain frameworks in Stage 2 context priming]

**Framework**: [Name — e.g., HIPAA, PCI-DSS, WCAG 2.1 AA]
**Key requirements that shaped this PRD**:
- [Requirement 1 → how it affected feature scope]
- [Requirement 2 → how it affected architecture]

---

## 7. Risks & Open Questions

### Risks (from Stage 1 unresolved concerns)
| Risk | Severity | Mitigation |
|------|----------|------------|
| [Concern skeptic never conceded] | High/Med/Low | [How to address] |

### Open Questions
- [Question that needs more research before building]

---

## 8. Next Steps

- [ ] Stage 3: Build stakeholder persona
- [ ] Stage 4: Generate interactive prototype
- [ ] Stage 5: Create pitch + rehearse with stakeholder
- [ ] Deep dive: `/startup-planner` Stage 8+ for BMC and market sizing
```

## Principles

1. **Evidence over assertions** — every claim should tie back to Stage 1 research
2. **Constraints before features** — the constraint shapes what's possible
3. **Anti-targets are features** — saying who it's NOT for prevents scope creep
4. **One primary metric** — teams that track everything optimize nothing
5. **Won't Have is mandatory** — explicit exclusions prevent feature drift

## Context Priming Pattern

When the user provides domain frameworks in Stage 2:

1. **Absorb the framework first** — read it, understand its requirements
2. **Map framework requirements to features** — which must-haves are driven by the framework vs. user need?
3. **Call out framework-driven constraints** — "HIPAA requires X, which means the architecture must Y"
4. **Don't let the framework bloat the MVP** — only include framework requirements that apply to must-have features

# Spec Kit-inspired Specification Template

Use this minimum artifact before authoring an implementation plan. It adapts
GitHub Spec Kit's `constitution → specify → clarify → plan` sequence; the
Spec Kit CLI is optional.

```markdown
# <Feature> Specification

## Constitution and governing constraints

- Source: `<path>` — <principle or constraint>
- Session-derived principle: <only when no durable source exists; explain why>

## Problem and users

<Who has what problem, and why it matters.>

## User scenarios

- **US-1:** When <context>, <actor> can <action>, so that <outcome>.

## Requirements

- **FR-1:** The system shall ...
- **NFR-1:** The system shall ...

## Scope

### In

- ...

### Out

- ...

## Edge cases and failure modes

- **EC-1:** ...

## Acceptance criteria

- **AC-1:** Given ..., when ..., then ...

## Clarifications and assumptions

- Resolved: ...
- Assumption: ...
- Open question: ...
```

Before the plan is approved, resolve every material ambiguity or record it as
an explicit assumption/open question, and map every plan task to the spec IDs.

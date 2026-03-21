# Discovery Session - Requirements Exploration

Run a structured discovery session to explore and define requirements for a feature, product, or system. This process asks one question at a time to thoroughly understand the problem before proposing solutions.

## How This Works

1. **One question at a time** - Wait for your answer before asking the next
2. **Build understanding progressively** - Each answer informs the next question
3. **No assumptions** - Ask rather than guess
4. **Document as we go** - Summarize periodically to confirm understanding
5. **End with deliverables** - Create specs, plans, or documentation

## Discovery Framework

### Phase 1: Context & Vision
- What problem are we solving?
- Who is this for? (users, customers, stakeholders)
- What's the ideal outcome?
- What does success look like?

### Phase 2: Users & Use Cases
- Who are the primary users?
- What are they trying to accomplish?
- What's their current workflow/process?
- What are their pain points?

### Phase 3: Functional Requirements
- What must the system DO?
- What actions can users take?
- What information do they need?
- What are the inputs and outputs?

### Phase 4: Constraints & Boundaries
- What's out of scope?
- What are technical constraints?
- What are budget/time constraints?
- What existing systems must we integrate with?

### Phase 5: Edge Cases & Concerns
- What could go wrong?
- What are the security considerations?
- What about errors and failures?
- What are the performance requirements?

### Phase 6: Prioritization
- What's the MVP vs nice-to-have?
- What's the implementation order?
- What are the dependencies?

## Starting the Session

When the user invokes `/discover`, begin with:

---

**Discovery Session Started**

I'll ask you one question at a time to fully understand what you're building. Take your time with each answer - the more detail you provide, the better the final result.

**First question:** What are we building? Give me a brief description of the feature, product, or system you want to explore.

---

## Session Rules

1. **Never ask multiple questions at once** - One question, wait for answer
2. **Acknowledge each answer** - Brief confirmation before next question
3. **Go deeper when needed** - If an answer is vague, ask follow-up
4. **Offer options when helpful** - "Would you prefer A, B, or C?"
5. **Summarize every 5-7 questions** - Confirm understanding before continuing
6. **Be thorough but not tedious** - Skip obvious questions, dig into important ones

## Handling Answers

- **"All of the above"** - Accept it, note all options as requirements
- **"I'm not sure"** - Offer options or suggest a reasonable default
- **"Let's defer that"** - Mark as future consideration, move on
- **"What do you recommend?"** - Provide recommendation with reasoning

## Ending the Session

When discovery is complete, ask:

> We've covered the core requirements. Would you like me to:
> 1. Create a requirements document
> 2. Create an implementation plan
> 3. Create both
> 4. Just summarize what we discussed

Then create the requested deliverables based on everything learned.

## Output Formats

### Requirements Document
```markdown
# [Feature Name] Requirements

## Overview
[Brief description]

## Users
[Who uses this]

## Functional Requirements
[What it does]

## Non-Functional Requirements
[Performance, security, etc.]

## Out of Scope
[What it doesn't do]

## Open Questions
[Unresolved items]
```

### Implementation Plan
```markdown
# [Feature Name] Implementation Plan

## Phases
[Ordered list of phases]

## Phase Details
[Tasks per phase]

## Dependencies
[What blocks what]

## Success Criteria
[How we know it's done]
```

## Example Session Flow

```
User: /discover

Claude: Discovery Session Started. What are we building?

User: A notification system for our app

Claude: Got it - a notification system. Who will receive these notifications?

User: Our subscribers

Claude: Subscribers will receive notifications. What types of events should trigger notifications?

User: When tasks are due, when clients respond, when workflows fail

Claude: Three trigger types noted. How should notifications be delivered - email, SMS, push, in-app, or some combination?

[...continues until complete...]
```

## Tips for Best Results

- Answer with as much context as you have
- Say "I don't know yet" if you're unsure
- Mention constraints early (budget, timeline, tech stack)
- Share examples of similar systems you like
- Be honest about priorities

---
name: difficult-workplace-conversations
description: Structure and deliver difficult workplace conversations — performance feedback, peer conflict, raise asks, receiving criticism, terminations, upward feedback. Uses the SBI model (Situation-Behavior-Impact), a three-phase Preparation-Delivery-Followup framework, and ready-to-use scripts for opening lines, handling defensiveness, and closing to agreements. Covers manager-to-report, peer-to-peer, and report-to-manager dynamics. Pairs with /communication-safeguards for state and timing checks before high-stakes messages.
user-invocable: true
allowed-tools: Read, Glob, Grep
---

# Difficult Workplace Conversations

A structured approach to challenging conversations — performance issues, peer conflicts, raise asks, receiving criticism, sensitive topics, and emotionally charged discussions.

## Professional-Help Boundary

> **This skill provides communication frameworks, not professional counsel.**
> For serious situations — harassment, discrimination, legal disputes, terminations with possible wrongful-dismissal claims, or conversations where your mental or physical safety is at risk — consult a licensed professional: an employment attorney, a therapist or licensed counselor, or a trained HR professional. This skill is a preparation and delivery aid, not a substitute for expert judgment on high-stakes legal or clinical matters.

## Compose With /communication-safeguards First

**Before using this skill for any conflict-hot or high-stakes message:**

Run `/communication-safeguards` first. It handles the upstream layer — internal activation, HALT check, state and timing — that this skill cannot see. Once you're in a good state to proceed, return here for structure and delivery.

The sequence is: `/communication-safeguards` (state/timing gate) → this skill (structure/delivery) → `anthropic-skills:toneguard` (scan for passive-aggressive or escalatory language). Each handles a different layer; they compose without overlapping.

See also: [`../communication-safeguards/SKILL.md`](../communication-safeguards/SKILL.md)

---

## When to Use This Skill

- Preparing for a challenging conversation with a colleague, peer, or manager
- Addressing performance issues with a direct report
- Delivering difficult feedback to a peer or upward
- Navigating conflict between team members
- Discussing sensitive topics: salary, promotion, termination
- Handling emotional or defensive reactions in the moment
- Following up after difficult discussions

---

## Core Framework: Preparation-Delivery-Followup

Difficult conversations succeed or fail across three phases. Most failures happen in Phase 1 — preparation skipped or done wrong.

### Phase 1: Preparation (Before)

**Purpose:** Set up a productive conversation before you walk in.

1. **Clarify the issue** — observable facts only, no interpretations
   - What specifically happened?
   - What was the impact on you, the team, or the work?
   - What change do you need?

2. **Check your state** — are you ready?
   - What are you feeling, and why?
   - Are you calm enough to hear their perspective without reacting?
   - What might trigger you? (Name it now, not mid-conversation)

3. **Consider their perspective**
   - How might they see this situation differently?
   - What constraints or pressures might they be carrying?
   - What do they care about that you can acknowledge?

4. **Define your goal**
   - Ideal outcome, minimum acceptable, and what you'll compromise on
   - Relationship goal: how you want to work together after
   - Identity goal: who you want to be in the room

**Full prep worksheet:** [`references/preparation-template.md`](references/preparation-template.md)

---

### Phase 2: Delivery (During)

**Purpose:** Have the conversation effectively.

1. **Open neutrally** — state purpose, share intent, invite partnership
2. **Share your perspective** — behavior, not character; impact, not intention; "I" statements
3. **Listen actively** — paraphrase, clarify, acknowledge, validate
4. **Seek resolution** — specific actions, named owners, check-in date

**Full opening formulas, response handling, and reframing scripts:** [`references/delivery-scripts.md`](references/delivery-scripts.md)

---

### Phase 3: Followup (After)

**Purpose:** Turn conversation into lasting change.

1. **Document agreements** — what was agreed, who does what, by when, how to measure
2. **Check progress** — follow up as promised; acknowledge improvements; address regression early
3. **Maintain the relationship** — separate the issue from the person; rebuild trust through small actions

---

## Key Principles

### The SBI Model

**Situation:** When and where did this happen?
**Behavior:** What specifically did they do or say? (Observable — what a camera would record)
**Impact:** What was the effect on you, the team, or the work?

Use SBI to keep feedback on behavior and impact, not assumptions about intent.

### Separate Impact from Intent

What happened (observable) is not the same as why it happened (assumed). Most people have better intentions than their impact suggests. Name the impact; ask about the intent.

### Managing Emotions in the Room

| If You Feel | Before Acting |
|---|---|
| Angry | Wait 24 hours; write but don't send |
| Hurt | Talk to a neutral party first |
| Anxious | Practice the opening out loud |
| Defensive | Name what you contributed to the situation |

**Full emotional regulation techniques (pre-conversation, in-the-moment, post-conversation):** [`references/emotional-regulation.md`](references/emotional-regulation.md)

---

## Conversation Types

### Performance Feedback
- Lead with specific, observable examples (2-3 minimum)
- Connect to stated expectations
- Focus on future improvement, not the past as a record
- Offer support and name resources

### Conflict Resolution
- Consider hearing both sides separately before a joint conversation
- Identify underlying interests (not just positions)
- Look for shared goals to anchor resolution
- Document agreements in writing within 24 hours

### Sensitive Topics (salary, promotion, termination, personal matters)
- Private, neutral setting — not your office if you hold power
- Allow time for processing; don't rush
- Direct and compassionate; do not soften into vagueness
- Respect confidentiality

### Receiving Feedback
- Thank them first; ask clarifying questions before defending
- Reflect before responding — you don't have to answer immediately
- Separate useful signal from delivery quality

---

## When to Escalate to HR or Legal

Escalate — and consult a professional — when:
- Safety is at risk (physical or psychological)
- Legal issues are involved (harassment, discrimination, wage claims)
- Repeated direct conversations haven't worked
- Power dynamics prevent honest resolution
- Documentation is needed for a formal process

---

## Common Anti-Patterns

**In Preparation**
- Scripting every word — prepare themes, not a script; you'll sound robotic
- Building a legal case — seek understanding, not a verdict
- Waiting too long — issues compound; act within days, not weeks

**In Delivery**
- "You always..." — triggers defensiveness immediately; use SBI instead
- Burying the lead — soften your tone, not your point; get to it
- Leading questions — "Don't you think...?" is not asking

**In Followup**
- No check-in — without follow-up, behavior reverts
- Holding a grudge — resolved means the relationship continues
- Over-documenting — not every conversation needs a paper trail

---

## Quick Scenario Guide

**Missed deadlines (3 in a month):**
> "I wanted to check in about the recent deliverables. I've noticed the last three came in after the deadline. I'd like to understand what's been happening and figure out how we can address it together."

**Peer called out your work publicly:**
> "I'd like to talk about what happened in yesterday's standup. When you said my code 'missed obvious issues,' I felt called out in front of the team. I want to understand your concerns and find a better way to handle code quality feedback."

**Asking for a raise:**
> "I'd like to discuss my compensation. I've been here two years, taken on leadership of the payments project, and want to make sure my salary reflects my contributions and the current market."

---

## Communication Principles

This skill loads [`../shared/communication-principles.md`](../shared/communication-principles.md) before drafting any artifact. Key applies:

- **Lead with the conclusion** (§3): open the conversation with the purpose, not a long wind-up.
- **Audience-centered** (§1): prepare by thinking about what they need to hear, not just what you need to say.
- **Preparation** (§7): the preparation template is non-optional for high-stakes conversations.
- **Sameness-detector** (§9): run before sending any written follow-up or agreement summary.

---

## References (Load When Needed)

- **[`references/conversation-framework.md`](references/conversation-framework.md)** — full three-phase framework with scripts, examples, and agreement templates
- **[`references/preparation-template.md`](references/preparation-template.md)** — worksheet for preparing before difficult conversations (quick 10-min and full 30-min versions)
- **[`references/delivery-scripts.md`](references/delivery-scripts.md)** — opening lines, response handling, reframing techniques, closing scripts
- **[`references/emotional-regulation.md`](references/emotional-regulation.md)** — managing your own emotions before, during, and after

## See Also

- [`../communication-safeguards/SKILL.md`](../communication-safeguards/SKILL.md) — state, timing, and intent gate; run this first for conflict-hot messages
- [`../writing-voice/SKILL.md`](../writing-voice/SKILL.md) — apply Summer's voice to written follow-ups and agreement emails

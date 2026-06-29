---
name: fundraising-email
description: >
  Use when a founder wants to write an email to an investor - cold outreach, warm intro request,
  follow-up after a meeting, monthly investor update, or round-closing note. Triggers on: investor
  email, cold outreach to VC, intro email, follow up with investor, investor update. Outputs a
  ready-to-send subject line and email body. Load communication-principles.md before drafting.
user-invocable: true
---

# Fundraising Email

Before drafting any email, load [`../shared/communication-principles.md`](../shared/communication-principles.md)
and run the **§9 sameness-detector** pass on the draft. Investor emails fail on generic - every
claim must survive the company-swap test ("$42K MRR growing 25% MoM" beats "fast-growing revenue").

## When to Use

- Founder needs to write a cold outreach email to an investor.
- Founder wants to draft a warm intro request (a "forwardable email").
- Founder needs a follow-up after an investor meeting.
- Founder is writing a monthly investor update.
- Founder wants to send a thank-you or round-closing notification.

## Context Required

From the user: company one-liner, stage, key traction metrics, fundraising status, notable social
proof (investors, customers, press), email type, recipient name and firm, prior relationship context,
and desired outcome (meeting, intro, materials review).

## Workflow

1. **Determine email type** - classify as one of the five types below.
2. **Gather context** - ask for any missing metrics or personalization details.
3. **Draft the email** - follow the type-specific template. Keep it short: investors scan, they don't read.
4. **Add personalization** - include at least one specific reference to why this investor is a fit (thesis, portfolio company, blog post). Generic emails get ignored.
5. **Run sameness check** - verify every claim is concrete and survives the swap test.
6. **Deliver** - output subject line and email body, ready to copy-paste.

## Output Format

```
**To:** [Investor Name]
**Subject:** [Subject line]

[Email body]
```

For investor updates, output a longer structured email with sections (see type 4 below).

## Frameworks

### The Five Email Types

#### 1. Cold Outreach
**Goal:** get a 30-minute meeting. **Length:** 5-7 sentences, under 150 words.
- **Line 1:** why this investor specifically (1 sentence).
- **Lines 2-3:** what you do and for whom (no jargon).
- **Lines 4-5:** strongest traction proof point - one number that makes them lean in.
- **Line 6:** specific, low-commitment ask ("Would you have 30 minutes this week or next?").
- No attachments on first email. **Subject line formula:** `[Specific hook] - [Company Name]`
  (e.g., `"$40K MRR in 6 months, AI contract review - Lexara"`).

#### 2. Warm Intro Request (The Forwardable Email)
**Goal:** make it effortless for your connector to intro you. **Two parts:**
- **Note to connector** (2-3 sentences): "Would you be willing to introduce me to [Partner] at
  [Firm]? Short blurb below you can forward directly."
- **Forwardable blurb** (4-6 sentences): written so the connector sends it as-is. Include what the
  company does, strongest metric, why this firm is relevant, and what you're looking for. If the
  connector has to rewrite it, they won't send it.

#### 3. Follow-Up After Meeting
**Goal:** maintain momentum, deliver materials, set next steps. **Length:** 4-8 sentences.
- Thank them and reference one specific thing discussed.
- Attach requested materials. Address any open question.
- Propose a specific next step with a date.
- **Send within 3 hours** - speed signals competence.

#### 4. Monthly Investor Update
**Goal:** keep current and prospective investors informed. **Length:** 300-500 words.
- **Highlights:** top 3 wins (metrics-first).
- **KPIs:** table with this month, last month, MoM change.
- **Challenges:** 1-2 honest struggles (invites help; investors respect candor).
- **Asks:** 1-3 concrete requests (intros to specific customer types, candidates for a role).
- **What's Next:** top 2-3 priorities for next month.
- Send on the same day each month. Monthly updates are the #1 way to convert a "not yet" into a future "yes".

#### 5. Thank-You / Round Closing Note
**Goal:** maintain the relationship. **Length:** 3-5 sentences.
- If invested: genuine thanks, confirm logistics, add to update list.
- If passed: thank them, leave the door open, ask if they want monthly updates. Never burn bridges -
  the investor who passes on seed may lead your Series A.

### Core Principles

1. **Brevity wins** - investors get 50-100 inbound emails weekly. Over 200 words in a cold email gets skimmed.
2. **Specificity beats superlatives** - "$42K MRR growing 25% MoM" beats "fast-growing revenue".
3. **Social proof early** - recognizable customer, investor, or accelerator in the first two lines.
4. **One clear CTA** - every email gets exactly one ask.
5. **Personalization is mandatory** - reference their thesis, portfolio, or writing. Doubles response rates.
6. **Subject lines are headlines** - lead with your best metric or most surprising fact.
7. **Send Tuesday-Thursday, 8-10am investor's timezone** - open rates drop on Mondays and Fridays.

### What Not to Do

- No "disruptive", "revolutionary", "game-changing", or "the Uber of X".
- No NDAs. No reputable investor signs them for startup pitches.
- Don't email multiple partners at the same firm. They compare notes.
- Don't follow up more than twice without new information.
- Don't CC multiple investors on the same email.

## See also

- `investor-research` — research who to email and what personalization to use.
- `yc-pitch-deck` — the email drives the meeting; the deck carries the meeting.
- `fundraising` — broader fundraising strategy and process.
- `elevator-pitch` — spoken 10/30/60/90-second verbal pitches; pair with cold outreach openers.

---
name: inbox-triage
description: >
  Triage Summer's Gmail inbox: score emails by importance, route action items
  to the correct Mem note as checkboxes, create draft replies for urgent emails,
  track unsubscribe candidates, and log everything.
  Use this skill whenever asked to "triage inbox", "check my email",
  "go through my email and add tasks", "run inbox triage", "process my inbox",
  or any request to sort, summarize, or act on email. Also runs automatically
  at 9am EST daily.
---

# Inbox Triage

You are triaging Summer Rae's Gmail inboxes on her behalf.
Your job: turn email noise into structured, actionable items — importance-scored,
routed to the right Mem note, deduped against existing tasks, and logged.

## Email accounts to check
- Personal: sumrae412@gmail.com
- Work: summer@deeplearning.ai

---

## Mem Note IDs

| Note | ID |
|---|---|
| DeepLearning.AI work | `479ee14b-baed-4e54-8c5d-c2edb8c2a5b1` |
| CourierFlow | `7e999d54-9690-4ad1-8494-c665242b4306` |
| BetterBurgh | `c4937ace-82b4-400f-b31e-42bbffc5ed21` |
| Personal (everything else) | `f9d6413e-4d58-4c2c-a446-514f5a7fa148` |

**Always call `get_note` before `update_note`** to retrieve the current `version`.
Send the full note content back in `update_note` — partial patches are not supported.

---

## Step 1 — Fetch email

Search both Gmail accounts with:
```
is:unread in:inbox
```
Fetch up to 50 threads per account. Use `get_thread` for anything substantive.

---

## Step 2 — Categorize each email by project

**DeepLearning.AI** — emails from @deeplearning.ai addresses, work colleagues,
course-related topics, vendors/partners related to her full-time role.

**CourierFlow** — emails related to CourierFlow app development: developers,
contractors, tools, services, or partners connected to building the app.

**BetterBurgh** — emails related to real estate: properties, closings, title
companies, lenders (e.g. LendingClub), landlord/tenant matters, inspections,
contractors.

**Personal** — everything else: personal finances, health, subscriptions,
friends/family, government, general admin.

---

## Step 3 — Score each email (0-100)

| Signal | Weight | Notes |
|---|---|---|
| Sender priority | 30% | VIP=30, known/corporate=20, unknown=10, spam/auto=0 |
| Urgency keywords | 25% | urgent/ASAP/deadline today=25, important/pending=18, question=10, none=0 |
| Relevance | 20% | Personalized/direct=20, CC/related=12, generic=5, off-topic=0 |
| Thread depth | 15% | Active back-and-forth=15, ongoing=10, new reply=5, cold=0 |
| Time sensitivity | 10% | <24h=10, <7 days=7, >7 days=3, none=0 |

Score to action:
- 65-100: Route to Mem + create Gmail draft reply
- 30-64: Route to Mem, no draft needed
- 0-29: Skip

### VIP senders (always score 65+)
- @deeplearning.ai domain
- Any Andrew Ng address
- @lendingclub.com
- @townsgateclosing.com or Townsgate-related
- Any lawyer, notary, or title company
- Any billing/payment failure alert

### Always skip (score 0)
- Marketing, newsletters, promotions
- FYI / receipts / confirmations / automated notifications
- GitHub individual commit/push/branch notifications

### GitHub digest (once per week)
Add one digest task to the CourierFlow note:
`- [ ] **Review this week's CourierFlow GitHub activity** — triaged [date]`
Check the note first — skip if a digest was already added this week.

---

## Step 4 — Handle each email

### A. Marketing / Newsletters / Promotions
**Action:** Skip entirely.

### B. Action Required (Summer must handle personally)
Bills, legal docs, appointments, logins required, physical tasks.
**Action:** Get the current version of the correct Mem note, then add a checkbox
under `## Pending`:
```
- [ ] **Task name** — brief description of what's needed and why.
```

### C. Needs a Reply
Real people or businesses waiting on a response.
**Action:** Create a Gmail draft reply (warm, professional, match formality of
original). Do not send.
Also add to the correct Mem note:
```
- [ ] **Reply to [sender]** — [one line on what it's about]
```

### D. Claude Can Handle It
Tasks completable with available tools (research, phone numbers, lookups, scheduling).
**Action:** Complete it. Add to the correct Mem note under `## Done`:
```
- [x] **[Task]** — handled automatically on [date]
```

### E. FYI / Receipts / Confirmations
**Action:** Skip entirely.

---

## Step 5 — Deduplication

Before adding a task, scan the note content for a similar unchecked `- [ ]` item
(same topic/sender/action). If found, skip. If the match is `- [x]`, add a fresh one.

---

## Step 6 — Create Gmail draft replies

For emails scoring 65+ where a response is expected:
- Brief, professional-but-warm tone
- Match formality of the original
- Subject: `Re: [original subject]`

Skip for FYI emails, automated messages, or anything needing research first.

---

## Step 7 — Log a daily summary

Append to the Personal note (`f9d6413e-4d58-4c2c-a446-514f5a7fa148`) under a
`## Daily Triage Log` section (create if missing):

```
**[Date] — Inbox Triage**
- Emails reviewed: X personal, X work
- DeepLearning.AI: X items
- CourierFlow: X items
- BetterBurgh: X items
- Personal: X items
- Drafts created: X
- Auto-handled: X
- Notable: [anything worth flagging]
```

---

## Step 8 — Report in chat

Brief summary: emails processed/skipped, tasks added by project, drafts created,
anything urgent.

---

## Tools

- `mcp__a5ce767d-48cc-4ac0-b83a-4a0e2432ee4a__get_note` — read a Mem note (required before update)
- `mcp__a5ce767d-48cc-4ac0-b83a-4a0e2432ee4a__update_note` — write full note content back
- `search_threads` — find email (Gmail MCP)
- `get_thread` — read full thread body (Gmail MCP)
- `create_draft` — create reply draft (Gmail MCP)

---

## Principles

- Err toward adding a task — easier to uncheck than to miss something.
- Keep task labels short — action + minimal context, no email body copy.
- Always dedup — read before writing.
- VIPs always get a task — even if the email looks routine.
- Always `get_note` before `update_note` — the version number is required.

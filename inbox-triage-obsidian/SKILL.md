---
name: inbox-triage-obsidian
description: >
  Triage Summer's Gmail inbox: score emails by importance, route action items
  to the correct Obsidian project note as checkboxes, create draft replies for
  urgent emails, track unsubscribe candidates, and log everything.
  Use this skill whenever asked to "triage inbox", "check my email",
  "go through my email and add tasks", "run inbox triage", "process my inbox",
  or any request to sort, summarize, or act on email. Also runs automatically
  at 9am EST daily.
---

# Inbox Triage

You are triaging Summer Rae's Gmail inbox (`sumrae412@gmail.com`) on her behalf.
Your job: turn email noise into structured, actionable items — importance-scored,
routed to the right Obsidian project note, deduped against existing tasks, and logged.

---

## Obsidian Vault File Paths

| Note | Path |
|---|---|
| Claude Tasks (Personal) | `~/Documents/obsidian/Claude Tasks.md` |
| DeepLearning.AI tasks | `~/Documents/obsidian/DeepLearning.AI.md` |
| CourierFlow tasks | `~/Documents/obsidian/CourierFlow.md` |
| BetterBurgh tasks | `~/Documents/obsidian/BetterBurgh.md` |
| Triage Log | `~/Documents/obsidian/Inbox Triage Log.md` |

Use `mcp__Desktop_Commander__read_file` to read and `mcp__Desktop_Commander__write_file`
to write these files. If a file doesn't exist yet, create it with the default header below.

Default header for project files:
```markdown
# [Project Name]

## Pending

## Done
```

Default header for Triage Log:
```markdown
# Inbox Triage Log

Auto-generated log of daily inbox triage runs. Most recent entry at the top.

---
```

---

## Step 1 — Determine lookback window

Read `~/Documents/obsidian/Inbox Triage Log.md`.
Find the most recent `Last email timestamp processed:` line and use that as the
`after:` cutoff for Gmail search.

If the file doesn't exist or has no timestamp, default to `newer_than:1d`.

---

## Step 2 — Fetch email

Search Gmail:
```
after:[TIMESTAMP] -category:promotions -category:social
```
Fetch up to 30 threads. Use `get_thread` for anything substantive.

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
- 65-100: Route to Obsidian + create Gmail draft reply
- 30-64: Route to Obsidian, no draft needed
- 0-29: Skip

### VIP senders (always score 65+)
- @deeplearning.ai domain
- Any Andrew Ng address
- @lendingclub.com
- @townsgateclosing.com or Townsgate-related
- Any lawyer, notary, or title company
- Any billing/payment failure alert

### GitHub notifications
- Skip all individual commit/push/branch notifications.
- Once per week, add one digest task to CourierFlow.md:
  `- [ ] Review this week's CourierFlow GitHub activity (triaged [date])`
  Check the Triage Log first — skip if a digest was already added this week.

---

## Step 4 — Deduplication

Before adding a task:
1. Read the target file with `mcp__Desktop_Commander__read_file`.
2. Scan for a similar unchecked `- [ ]` item (same topic/sender/action).
3. If found, skip. If the match is `- [x]`, add a fresh one.

---

## Step 5 — Route tasks to Obsidian

| Project | File | Route when email involves... |
|---|---|---|
| DeepLearning.AI | `DeepLearning.AI.md` | DL.AI courses, instructors, Andrew Ng, Coursera, curriculum, partnerships |
| CourierFlow | `CourierFlow.md` | CourierFlow app, logistics, driver/courier ops, dispatch, the startup |
| BetterBurgh | `BetterBurgh.md` | BetterBurgh project, Pittsburgh community |
| Personal | `Claude Tasks.md` | Finance, legal, health, real estate, personal errands, anything else |

Task format:
```
- [ ] [Action verb] — [brief context, sender if relevant] (triaged [date])
```

Examples:
```
- [ ] Reply to Aarti re: instructor contract start date (triaged 2026-05-04)
- [ ] ⚠️ Respond to Townsgate — deadline Friday (triaged 2026-05-04)
- [ ] Review LendingClub payment schedule update (triaged 2026-05-04)
```

To append tasks: read the file, add new tasks under `## Pending`, write the full
content back with `mcp__Desktop_Commander__write_file` using mode `append` when
adding to an existing file, or `rewrite` when creating fresh.

---

## Step 6 — Create Gmail draft replies

For emails scoring 65+ where a response is expected, create a draft reply:
- Brief, professional-but-warm tone
- Subject: `Re: [original subject]`

Skip for FYI emails, automated messages, or anything needing research first.

---

## Step 7 — Unsubscribe nudge

If the same sender was skipped in this run AND appears in 3+ prior triage log
entries, add a one-time task to `Claude Tasks.md`:
```
- [ ] Consider unsubscribing from [sender] — skipped 3+ times (triaged [date])
```
Check the file first — skip if the nudge already exists.

---

## Step 8 — Update Triage Log

Read `~/Documents/obsidian/Inbox Triage Log.md`, prepend a new entry below the
header (newest at top), write it back.

Log format:
```
**Inbox Triage — [date] [time EST]**
- Processed: [N] emails
- Skipped: [N] ([breakdown])
- Tasks added: [N] items across [files touched]
- Drafts created: [N]
- Last email timestamp processed: [ISO timestamp of newest email seen]
- Notes: [anything urgent, anomalies, unsubscribe nudges]

---
```

---

## Step 9 — Report in chat

Brief summary: emails processed/skipped, tasks added by project, drafts created,
anything urgent.

---

## Tools

- `mcp__Desktop_Commander__read_file` — read Obsidian markdown files
- `mcp__Desktop_Commander__write_file` — write file content (mode: append or rewrite)
- `search_threads` — find email (Gmail MCP)
- `get_thread` — read full thread body (Gmail MCP)
- `create_draft` — create reply draft (Gmail MCP)

---

## Principles

- Err toward adding a task — easier to uncheck than to miss something.
- Keep task labels short — action + minimal context, no email body copy.
- Always dedup — read before writing.
- VIPs always get a task — even if the email looks routine.
- The triage log is the source of truth for lookback and unsubscribe tracking.

---
name: inbox-triage
description: >
  Triage Summer's Gmail inbox: score emails by importance, route action items
  to the correct Mem note as checkboxes, create draft replies for urgent emails,
  execute Summer-directive tasks from the Claude Tasks note (including
  credential-gated logins via macOS Keychain), create calendar events for
  confirmed appointments, auto-archive curated newsletters to Mem, post the
  daily summary to Summer's Slack DM, and log everything.
  Use this skill whenever asked to "triage inbox", "check my email",
  "go through my email and add tasks", "run inbox triage", "process my inbox",
  or any request to sort, summarize, or act on email. Also runs automatically
  at 10:00am EST daily.
---

# Inbox Triage

You are triaging Summer Rae's Gmail inbox on her behalf.
Your job: turn email noise into structured, actionable items — importance-scored,
routed to the right Mem note, deduped against existing tasks, and logged.

## Role Contract

You are Summer's inbox triage operator. Your role is to classify personal Gmail,
surface real action, draft replies when appropriate, and keep all writes
auditable through Mem, Gmail drafts, calendar entries, and logs.

## Scope

Use this skill only for Summer's personal Gmail inbox and the connected triage
notes listed below. Do not process inaccessible work email, send replies, or
write outside the allowed notes unless the workflow explicitly grants that step.

## Email account to check
- Personal: sumrae412@gmail.com

The work account `summer@deeplearning.ai` is intentionally out of scope — it
isn't accessible via the current Gmail connector and is excluded from triage.
Do not search it, do not log it as "0 work / not accessible," and do not
attempt to surface a connector fix from inside a triage run.

---

## Mem Note IDs

| Note | ID | Role |
|---|---|---|
| Claude Tasks (also called Personal) | `f9d6413e-4d58-4c2c-a446-514f5a7fa148` | **Summer-added directives.** Step 7 executes from `## Pending` here. |
| Claude Inbox Proposals | `2623654a-822b-4f59-8a96-d08747730ddf` | **Triage outbox.** All routed tasks land here as proposals. Never executed. |
| Claude Auto-Execution Log | `eac92dec-244d-4476-8743-8adaa44443ab` | **Audit trail.** Append-only log of successful executions. |
| DeepLearning.AI work | `479ee14b-baed-4e54-8c5d-c2edb8c2a5b1` | Project note (Summer-managed). Triage no longer writes here. |
| CourierFlow | `7e999d54-9690-4ad1-8494-c665242b4306` | Project note (Summer-managed). Triage no longer writes here. |
| BetterBurgh | `c4937ace-82b4-400f-b31e-42bbffc5ed21` | Project note (Summer-managed). Triage no longer writes here. |

**Discrimination is structural, not syntactic.** Where a task LIVES tells you who created it: items in `Claude Tasks` are Summer's directives; items in `Claude Inbox Proposals` are Claude's proposals. No inline markers, no parsing.

**Always call `get_note` before `update_note`** to retrieve the current `version`.
Send the full note content back in `update_note` — partial patches are not supported.

---

## Step 1 — Fetch email

Search the personal Gmail account with:
```
is:unread in:inbox
```
Fetch up to 50 threads. Use `get_thread` for anything substantive.

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
- **TurboTenant** — any email from `@turbotenant.com` or any subject
  containing `Message from tenant`. Tenant communication is always VIP
  regardless of TurboTenant being a platform-generated sender. These do
  NOT match the "automated notifications" skip rule. Route to the
  appropriate property/tenant Mem note (Personal note if no project-
  specific note exists), and draft a reply for any tenant message that
  reads as a question, complaint, or maintenance request.
- **Job offers / recruiter outreach** — any email that looks like a
  recruiter, hiring manager, or platform-mediated job message. Detect via:
  - Subject contains: `job offer`, `offer letter`, `interview`,
    `opportunity at`, `role at`, `position at`, `we'd like to chat`,
    `chat about a role`, `hiring`, `recruiting`
  - Sender domain or display name includes: `recruiter`, `talent`,
    `hiring`, `careers@`, `jobs@`, `@lever.co`, `@greenhouse.io`,
    `@ashbyhq.com`, `@workable.com`, `@bamboohr.com`, LinkedIn InMail
    (`@linkedin.com` with subject mentioning a role/conversation)
  - Body patterns: "I came across your profile," "we have an opportunity,"
    "would you be open to," "your background looks like a great fit,"
    "[name] from [company] recruiting team"
  Route to the Personal Mem note with a `🎯` emoji prefix on the task line
  to make it visually distinct, draft a reply if the message clearly
  expects a response (intro, scheduling ask, follow-up question), and
  never zero-out under "marketing/automated" classification — recruiter
  outreach can pattern-match marketing template language but is genuinely
  worth Summer's attention.

### Floors and overrides (run BEFORE the "Always skip" list)

These rules apply *before* any classification or skip filtering. They exist
because Summer's explicit signals (stars, subject-line prefixes) must not be
silently overridden by the marketing/automated-notification classifier.

- **Starred by Summer → score 65+ floor + bypass "Always skip".** If the
  thread's first message has the Gmail label `STARRED` (or the search query
  matched `is:starred`), treat the email as VIP-tier regardless of sender,
  body content, or subject line. Add a task to the appropriate Mem note,
  draft a reply if a response is expected, and never zero it out under the
  "Always skip" list. The star is Summer's eyeball-passed-it consent — honor
  it before any other rule.
- **Subject-line prefix "Urgent:" / "URGENT" / "[URGENT]" / "Action Required:"
  → score 50 floor.** When the subject *starts with* one of these markers
  (case-insensitive, allow whitespace and brackets), apply a minimum score
  of 50. Place in the 30-64 "Route to Mem, no draft" tier at minimum;
  combine with other signals if they push higher. The word "urgent" buried
  inside a subject or body stays at the normal urgency-keyword weight (25).
  Subject-prefix is the stronger explicit-priority signal.

### Always skip (score 0)

Apply only AFTER the Floors and overrides above. If a Floor rule fires, do
not run this list.

- Marketing, newsletters, promotions
- FYI / receipts / confirmations / automated notifications
- GitHub individual commit/push/branch notifications
- **Redfin** — any email from `@redfin.com` or `@e.redfin.com` (listing
  alerts, saved-search updates, price drops, tour reminders, agent nudges,
  market reports). Never add to Mem, never create a calendar event, never
  draft a reply. Score 0 and move on. No weekly digest either.

**Tie-breaker on uncertain marketing classification.** If an email contains
an explicit urgency keyword (`urgent`, `ASAP`, `deadline`, `action required`,
`important`) AND the classifier is not confident it is marketing/automated,
default to *Route to Mem at the 30-64 tier* rather than skip. False
positives (a real email mis-classified as marketing) are more expensive than
false negatives (one extra task to uncheck). When in doubt, route — Summer
can dismiss with one click.

### GitHub digest (once per week)
Add one digest task to the CourierFlow note:
`- [ ] **Review this week's CourierFlow GitHub activity** — triaged [date]`
Check the note first — skip if a digest was already added this week.

---

## Step 4 — Handle each email

**Routing precedence:** check the email's `From` against the curated-newsletter
list in **4.G first**. If it matches, apply 4.G and skip A–F entirely (no
score, no draft, no proposal). Otherwise, fall through A–F as written.

### A. Marketing / Newsletters / Promotions
**Action:** Skip entirely.

### B. Action Required (Summer must handle personally)
Bills, legal docs, appointments, logins required, physical tasks.
**Action:** Add a checkbox to the **Claude Inbox Proposals** note
(`2623654a-822b-4f59-8a96-d08747730ddf`) under `## Pending`. Prefix the line
with today's date and a `[Project]` tag so Summer can route it during review:
```
- [ ] 2026-05-06 [Personal] **Task name** — brief description of what's needed and why.
```
Project tag is one of: `[DeepLearning.AI]`, `[CourierFlow]`, `[BetterBurgh]`,
`[Personal]`. Pick by the same project-classification rule you applied in Step 2.

### C. Needs a Reply
Real people or businesses waiting on a response.
**Action:** Create a Gmail draft reply (warm, professional, match formality of
original). Do not send. Also add a proposal to **Claude Inbox Proposals**:
```
- [ ] 2026-05-06 [BetterBurgh] **Reply to [sender]** — [one line on what it's about] (draft created)
```

### D. Claude Can Handle It
Tasks completable with available tools (research, phone numbers, lookups, scheduling).
**Action:** Complete it. Add to the correct Mem note under `## Done`:
```
- [x] **[Task]** — handled automatically on [date]
```

### E. FYI / Receipts / Confirmations
**Action:** Skip entirely.

### F. Confirmed meeting / appointment to add to calendar
Emails where Summer has clearly **accepted** or **confirmed** attending a
meeting, appointment, or event. Two cases:

1. **Calendar invites she accepted via email reply** ("yes, see you Tuesday at
   3pm" / "RSVP confirmed").
2. **Plain-text confirmations** with no `.ics` attachment ("Your dentist
   appointment is confirmed for May 10 at 2:00 PM at 123 Main St" / "Order
   pickup ready Tuesday 5/13 between 4-6pm at the warehouse").

**Action:**
1. **Extract the event:** title (concise — "Dentist", "Townsgate closing",
   "Coffee with Sam"), start time, end time (default 30 min if unclear),
   location, and a short description that links back to the source email.
2. **Check for duplicates** via Calendar MCP `list_events` for ±2h around the
   proposed start. If an existing event has the same title or location, do NOT
   create a duplicate — annotate that match in the chat summary instead.
3. **Create the event** via Calendar MCP `create_event` on her primary calendar
   (`primary`). Set `reminders.useDefault: true`.
4. **Append a Mem-side note** to the project's Pending section if the email
   isn't auto-handlable beyond the calendar add (e.g. "review prep before
   meeting"). Otherwise just count it toward `Auto-handled` in Step 8.

**Hard rules:**
- **Past events** — never create. If the proposed time is before now, skip
  and surface in the chat summary as "already past".
- **Ambiguous time** — if the email has multiple candidate times or no clear
  date, skip and add a `- [ ]` task to the Personal note asking Summer to
  schedule it manually. Do not guess.
- **Tentative / proposed** — if the email contains "tentative", "proposed",
  "if you're free", "would you be able to", do NOT create. That's an offer,
  not a confirmation.
- **All-day events for things that aren't all-day** — never. A "ship by Tuesday"
  email is not an all-day event for Tuesday; it's a deadline. Skip those.
- **Recurring** — only set recurrence if the email explicitly states a pattern
  ("every Tuesday at 3pm"). Single occurrence otherwise.

**Idempotency** — running triage twice on the same inbox state must not
double-add. The duplicate check (rule 2) is the safety net. If you're unsure
whether a match constitutes a duplicate, default to NOT creating.

### G. Curated newsletters — auto-archive to Mem (The Code, a16z Speedrun)

Emails from `thecode@mail.joinsuperhuman.ai` or `speedrun@substack.com` bypass Steps 3, 4.A–F, and 6 entirely: extract article links (excluding ads/chrome), fetch each via the `web-scraping-efficient` skill, save one Mem note per article, and add it to the `Claude articles` collection — idempotent, 10-article cap, tracking params stripped.
Load `references/newsletter-archiving.md` when an email's `From` matches a curated-newsletter sender (checked FIRST per Step 4 routing precedence) — it holds the full extraction, exclusion, note-format, and hard rules.

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

## Step 7 — Execute Summer-added tasks (Claude Tasks note)

Scan `## Pending` in the Claude Tasks note (`f9d6413e-4d58-4c2c-a446-514f5a7fa148`) — every item there is a Summer directive (discrimination is structural). For each: apply the safety boundaries first (no money, no irrevocable sends to humans, no external deletes without an explicit "delete" verb, no PII outside Mem, no credential write-back, no work-account actions), classify (direct / login-gated via Step 7.5 / cannot handle), execute, move to `## Done` with an annotation, and append to the Auto-Execution Log. Then run the stale-proposal scan on Claude Inbox Proposals (>14 days old → append `[STALE — never acknowledged]`; never delete or auto-purge).
Load `references/task-execution.md` before executing any Pending item — it holds the full flow, safety boundaries (7.2), Auto-Execution Log format (7.3), and stale-proposal scan (7.4).

---

## Step 7.5 — Login-gated tasks (macOS Keychain retrieval)

Before declaring a login-gated task "cannot handle", check the macOS Keychain under the `claude-automation:<service>` namespace (read-only, via `security find-generic-password`; never other Keychain items). Use the credential once in the browser-fill call, then drop it — never log, echo, or write it anywhere; stop on MFA/captcha/trust prompts and route the task back to Summer; record one audit line per credential read.
Load `references/credential-retrieval.md` whenever a Pending task requires a portal login — it holds the when-to-invoke test, retrieval flow, audit format, and hard rules.

---

## Step 8 — Log a daily summary

Append to the Personal note (`f9d6413e-4d58-4c2c-a446-514f5a7fa148`) under a
`## Daily Triage Log` section (create if missing):

```
**[Date] — Inbox Triage**
- Emails reviewed: X
- DeepLearning.AI: X items
- CourierFlow: X items
- BetterBurgh: X items
- Personal: X items
- Drafts created: X
- Calendar events added: X (Step 4.F)
- Articles archived: X (Step 4.G — The Code, a16z Speedrun → Claude articles)
- Auto-handled: X (includes Mem tasks worked)
- Notable: [anything worth flagging — including Gmail filter tasks left for the
  9:10am gmail-task-executor worker]
```

---

## Step 9 — Report in chat

Brief summary: emails processed/skipped, tasks added by project, drafts created,
Mem tasks worked, anything urgent.

---

## Step 10 — Post summary to Slack

After the chat report, send the same summary as a DM to Summer via Slack.

- **Channel:** `D08AXFD2SDT` (Summer's DM — user ID `U08ATMPMUAJ`)
- **Tool:** `slack_send_message`
- **Format:** Mirror the Step 8 log structure with a brief header line, bullet
  points for each project's item count, drafts, calendar events, and a
  `> ⚠️ Action needed:` callout for anything urgent. Keep it under ~20 lines.

---

## Tools

- `mcp__a5ce767d-48cc-4ac0-b83a-4a0e2432ee4a__get_note` — read a Mem note (required before update)
- `mcp__a5ce767d-48cc-4ac0-b83a-4a0e2432ee4a__update_note` — write full note content back
- `mcp__a5ce767d-48cc-4ac0-b83a-4a0e2432ee4a__create_note` — create a new Mem note (Step 4.G)
- `mcp__a5ce767d-48cc-4ac0-b83a-4a0e2432ee4a__add_note_to_collection` — add new note to `Claude articles` collection (Step 4.G)
- `mcp__a5ce767d-48cc-4ac0-b83a-4a0e2432ee4a__search_notes` — idempotency check by URL before creating (Step 4.G)
- `web-scraping-efficient` skill — fetch article content for archived newsletter links (Step 4.G); do NOT call `WebFetch` directly for these
- `search_threads` — find email (Gmail MCP)
- `get_thread` — read full thread body (Gmail MCP)
- `create_draft` — create reply draft (Gmail MCP)
- `list_events` — check existing calendar events for duplicates (Calendar MCP, Step 4.F)
- `create_event` — add a confirmed meeting/appointment to the primary calendar (Calendar MCP, Step 4.F)
- `security find-generic-password` (Bash) — fetch credentials from macOS Keychain
  under the `claude-automation:*` namespace (Step 7.5)

**Out of scope for this routine** — Gmail filter creation. The attached Gmail
MCP doesn't expose `users.settings.filters.create`. Filter tasks are picked up
by the separate `gmail-task-executor` GitHub Actions workflow at 9:10am ET,
which runs against the same `Claude Tasks` Pending list and uses a dedicated
Gmail OAuth token. Triage should leave filter tasks untouched and let that
worker handle them.

---

## Principles

- Err toward adding a task — easier to uncheck than to miss something.
- Keep task labels short — action + minimal context, no email body copy.
- Always dedup — read before writing.
- VIPs always get a task — even if the email looks routine.
- Always `get_note` before `update_note` — the version number is required.
- **Discrimination is structural.** Where a task lives = who created it.
  `Claude Tasks` note = Summer's directives (Step 7 executes). `Claude Inbox
  Proposals` note = Claude's outbox (Step 7 never executes from here; only
  flags stale items). No inline markers to parse, no syntactic drift.
- **Conservative by default.** When a task is ambiguous, leave it for Summer
  rather than guessing. The Auto-Execution Log only matters if entries are clean.
- **Promotion is Summer's gate.** A proposal becomes a directive when she
  copies the line from Proposals into Claude Tasks (sans date prefix). That
  copy is her explicit consent. Triage never auto-promotes.

---

## References

- [`articles/references/maturity-progression.md`](../articles/references/maturity-progression.md) — Jason Liu's Six Levels framework. `inbox-triage` currently sits around Level 3–4; the doc names what L5 (auto-draft replies on every urgent message) and L6 (per-sender memory) would look like.

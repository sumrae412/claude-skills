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

You are triaging Summer Rae's Gmail inbox on her behalf.
Your job: turn email noise into structured, actionable items — importance-scored,
routed to the right Mem note, deduped against existing tasks, and logged.

## Email account to check
- Personal: sumrae412@gmail.com

The work account `summer@deeplearning.ai` is intentionally out of scope — it
isn't accessible via the current Gmail connector and is excluded from triage.
Do not search it, do not log it as "0 work / not accessible," and do not
attempt to surface a connector fix from inside a triage run.

---

## Mem Note IDs

| Note | ID |
|---|---|
| DeepLearning.AI work | `479ee14b-baed-4e54-8c5d-c2edb8c2a5b1` |
| CourierFlow | `7e999d54-9690-4ad1-8494-c665242b4306` |
| BetterBurgh | `c4937ace-82b4-400f-b31e-42bbffc5ed21` |
| Personal (everything else) | `f9d6413e-4d58-4c2c-a446-514f5a7fa148` |
| Claude Auto-Execution Log | `eac92dec-244d-4476-8743-8adaa44443ab` |

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
under `## Pending`. **Tag Claude-routed tasks** with `(claude-routed YYYY-MM-DD)`
so Step 7 can distinguish them from tasks Summer added directly:
```
- [ ] (claude-routed 2026-05-06) **Task name** — brief description of what's needed and why.
```

### C. Needs a Reply
Real people or businesses waiting on a response.
**Action:** Create a Gmail draft reply (warm, professional, match formality of
original). Do not send.
Also add to the correct Mem note (with the same `(claude-routed)` tag):
```
- [ ] (claude-routed 2026-05-06) **Reply to [sender]** — [one line on what it's about]
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

## Step 7 — Work pending Summer-added tasks (Mem)

After handling email, read the Personal / Claude Tasks note
(`f9d6413e-4d58-4c2c-a446-514f5a7fa148`) and scan `## Pending` for unchecked items.

### 7.0 — Discriminator: who added each task?

For each `- [ ]` in `## Pending`:

- **Tagged `(claude-routed YYYY-MM-DD)`** → Claude added this from email triage. It is a
  PROPOSAL to Summer, NOT a directive. **Do not execute.** Apply the staleness
  rule below; otherwise leave it alone.
- **Untagged** → Summer added it directly. Execute per 7.1 below.

This split is the safety boundary: Summer-added items are directives, Claude-routed
items wait for Summer to read them in the morning brief and either tolerate them
(implicit ack) or delete them. Phase 1 is intentionally cautious. Future phases
may relax this once the Auto-Execution Log has enough data.

#### 7.0a — Staleness check (Claude-routed items only)

If a `(claude-routed YYYY-MM-DD)` task is **>14 days old** (date in the tag is more
than 14 days before today), append `[STALE — never acknowledged]` to the task body
and surface it in the Step 9 chat summary. Do NOT delete or auto-purge — Summer
decides whether to act or remove.

### 7.1 — Execute Summer-added tasks

For each untagged `- [ ]`:

1. **Apply safety boundaries first** (see 7.2). If any rule blocks execution, leave
   the checkbox alone and surface the reason in the Step 9 summary.
2. **Classify the task:**
   - **Claude can handle directly** (Gmail filter creation, calendar event creation,
     research/lookup, scheduling via tool, Drive file fetch): proceed.
   - **Login-gated, credential in macOS Keychain** (Step 7.5): retrieve credential,
     complete task, annotate.
   - **Cannot handle** (physical action, personal decision, ambiguous, requires
     judgment): leave as-is, surface in summary.
3. **Execute** with the appropriate tool.
4. **Move the checkbox to `## Done`** with a one-line completion annotation:
   ```
   - [x] **[Original task text]** — [what was done], [tool], [date]
   ```
5. **Append an entry to the Auto-Execution Log** Mem note
   (`eac92dec-244d-4476-8743-8adaa44443ab`). See 7.3 for format.

Call `update_note` once with the full updated Personal note after working all
actionable tasks. Count completed tasks toward "Auto-handled" in Step 8's log.

### 7.2 — Safety boundaries (apply before every execution)

These are hard rules. If a task touches any of these, do NOT execute — leave
unchecked, surface the reason in Step 9.

- **No money / no purchases.** Never initiate transfers, payments, charges, or
  buys, even if the credential is available. Includes "buy X on Amazon," "pay Y
  invoice," "transfer $Z."
- **No irrevocable sends to real humans.** For "send X to person Y" tasks, draft
  only — never send. Drafts go in Gmail's Drafts folder for Summer to review.
  Exception: Summer-authored Gmail filters that route to spam/label/archive, since
  those don't reach a human.
- **No external deletes without explicit "delete" verb.** "Filter to spam" and
  "archive" and "label" are OK. "Delete" requires the word "delete" or
  "permanently remove" in the task body.
- **No PII outside Mem.** Don't paste account numbers, SSNs, or sensitive
  personal data into chat output, drafts to third parties, or tool arguments
  beyond what the task requires.
- **No credential write-back.** Step 7.5's Keychain access is read-only.
- **No work-account actions.** `summer@deeplearning.ai` is out of scope.

If a task is ambiguous about which boundary applies, default to NOT executing
and ask in the Step 9 summary.

### 7.3 — Auto-Execution Log entry format

After each successful execution, fetch the Auto-Execution Log note
(`eac92dec-244d-4476-8743-8adaa44443ab`), prepend a new entry at the top (right
after the `***` separator), and `update_note` with the new content + version.

```
## YYYY-MM-DD — [Short task name]

- Source: Personal Mem note, Pending (Summer-added)
- Tools used: [Gmail filter | Calendar event | Drive search | Keychain + Browser | ...]
- Action: [one-sentence description of what Claude did]
- Outcome: [filter ID / event ID / URL / "found X" / "drafted reply" / etc.]
- Time: [seconds or "n/a"]

***
```

The log is the corpus that future triage decisions will learn from. Be specific
about the action and outcome — vague entries don't help calibration. Don't log
PII, credentials, or full email bodies.

---

## Step 7.5 — Login-gated tasks (macOS Keychain retrieval)

Before declaring a task "cannot handle" because it requires a login, check whether
the credential is stored in the macOS Keychain under the dedicated
`claude-automation:` service-name namespace. Only entries with that prefix are in
scope — never read other Keychain items (login, internet passwords, certificates,
keys) even if they look relevant.

### When to invoke

A task qualifies for Keychain retrieval when ALL of:
- Task body or linked email mentions a portal/login/sign-in (e.g. "log into
  LetterStream", "check Townsgate closing portal", "download from LendingClub").
- The portal is reachable via web browser (Claude in Chrome MCP or Playwright).
- A `claude-automation:<service>` entry likely exists in the Keychain.

### Retrieval flow

1. **Resolve service name** — derive `<service>` from the task by lowercasing the
   portal name with no spaces (e.g. "LetterStream" → `letterstream`, "Townsgate
   Closing" → `townsgate`). The full service-name lookup key is
   `claude-automation:<service>`.
2. **Fetch username** — run via Bash:
   ```
   security find-generic-password -s "claude-automation:<service>" | awk -F'"' '/"acct"/ {print $4}'
   ```
   If the command exits non-zero, no entry exists — treat the task as "cannot
   handle" and leave the checkbox unchecked.
3. **Fetch password** — run via Bash:
   ```
   security find-generic-password -s "claude-automation:<service>" -w
   ```
   The output is the password on stdout, no trailing newline beyond what
   `security` adds. If macOS prompts "Claude Code wants to use your confidential
   information" with no "Always Allow" button visible, stop and surface the
   prompt to Summer — do NOT click through blindly.
4. **Use credential immediately, then drop it** — pass to the browser tool, then
   discard from working memory. Never write the credential to a Mem note, log,
   draft, file, chat output, or tool argument other than the browser-fill call.
   Do not echo it back even partially.
5. **Audit log** — under the daily triage log entry, record one line per
   credential read:
   ```
   - Keychain read: claude-automation:<service> for task "<task name>"
   ```
   Do NOT log the username, password, URL query string, or any field value.
6. **On failure** — if the login fails (wrong password, MFA prompt, captcha,
   account locked), do NOT retry, do NOT try a second entry, and do NOT prompt
   the user inline. Move the task to `## Pending` with an annotation:
   ```
   - [ ] **[Task]** — login attempt failed (<short reason>) on [date]; needs Summer
   ```

### Hard rules

- **Namespace scope:** only service names matching `claude-automation:*`. If the
  closest match is `login.<something>` or any other service prefix, treat as
  "cannot handle." Do not enumerate the full Keychain.
- **Read-only:** never call `security add-generic-password`,
  `security delete-generic-password`, `security set-generic-password-partition-list`,
  or any write/modify subcommand. This skill is read-only against the Keychain.
- **MFA stop:** if the portal demands MFA / SMS / email-code / captcha, stop
  immediately and route the task back to Summer (failure annotation above).
  Never attempt to read MFA codes from email or SMS.
- **Output discipline:** `security ... -w` prints the password to stdout. Pipe
  it directly into the browser-fill call's stdin or capture it into a shell
  variable that's used once and unset. Never let the value land in a tool
  argument that gets logged, in a `bash` description string, or in chat output.
- **Trust prompt:** if Claude Code is not pre-authorized for an entry, macOS
  shows a popup. Surface that to Summer rather than driving a click — she'll
  re-run the `add-generic-password` command with `-T "$CLAUDE_PATH"` to
  authorize.

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
- Auto-handled: X (includes Mem tasks worked)
- Notable: [anything worth flagging]
```

---

## Step 9 — Report in chat

Brief summary: emails processed/skipped, tasks added by project, drafts created,
Mem tasks worked, anything urgent.

---

## Tools

- `mcp__a5ce767d-48cc-4ac0-b83a-4a0e2432ee4a__get_note` — read a Mem note (required before update)
- `mcp__a5ce767d-48cc-4ac0-b83a-4a0e2432ee4a__update_note` — write full note content back
- `search_threads` — find email (Gmail MCP)
- `get_thread` — read full thread body (Gmail MCP)
- `create_draft` — create reply draft (Gmail MCP)
- `security find-generic-password` (Bash) — fetch credentials from macOS Keychain
  under the `claude-automation:*` namespace (Step 7.5)

---

## Principles

- Err toward adding a task — easier to uncheck than to miss something.
- Keep task labels short — action + minimal context, no email body copy.
- Always dedup — read before writing.
- VIPs always get a task — even if the email looks routine.
- Always `get_note` before `update_note` — the version number is required.
- **Tag every Claude-routed task** with `(claude-routed YYYY-MM-DD)` so Step 7
  doesn't execute it. Untagged = Summer-added = directive. Tagged = proposal.
- **Conservative by default.** When a task is ambiguous, leave it for Summer
  rather than guessing. The Auto-Execution Log only matters if entries are clean.

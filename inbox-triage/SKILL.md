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

Read the Claude Tasks note (`f9d6413e-4d58-4c2c-a446-514f5a7fa148`) and scan
`## Pending` for unchecked items. **Every item here is a directive** — Summer
added it. There is no syntactic marker to check; the discrimination is
structural (Claude-routed proposals live in a different note — see Step 7.4).

For each `- [ ]` in `## Pending`:

1. **Apply safety boundaries first** (see 7.2). If any rule blocks execution, leave
   the checkbox alone and surface the reason in the Step 9 summary.
2. **Classify the task:**
   - **Claude can handle directly** (Gmail filter creation, calendar event,
     research/lookup, scheduling via tool, Drive file fetch): proceed.
   - **Login-gated, credential in macOS Keychain** (Step 7.5): retrieve credential,
     complete task, annotate.
   - **Cannot handle** (physical action, personal decision, ambiguous, requires
     judgment, or required tool not available): leave as-is, surface in summary.
3. **Execute** with the appropriate tool.
4. **Move the checkbox to `## Done`** with a one-line completion annotation:
   ```
   - [x] **[Original task text]** — [what was done], [tool], [date]
   ```
5. **Append an entry to the Auto-Execution Log** Mem note
   (`eac92dec-244d-4476-8743-8adaa44443ab`). See 7.3 for format.

Call `update_note` once with the full updated Claude Tasks note after working all
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

### 7.4 — Stale-proposal scan (Claude Inbox Proposals)

After executing Summer-added tasks, read the **Claude Inbox Proposals** note
(`2623654a-822b-4f59-8a96-d08747730ddf`). For each `- [ ]` line in `## Pending`:

- Parse the leading date (`YYYY-MM-DD` immediately after `- [ ]`).
- If the proposal is **>14 days old** (today − date > 14) AND does NOT already
  end with `[STALE — never acknowledged]`, append that marker to the line.
- Do NOT delete, auto-purge, or move stale items. Summer decides.

Examples:
```
- [ ] 2026-04-20 [BetterBurgh] **Reply to Townsgate** — closing date question (draft created) [STALE — never acknowledged]
```

Surface in the Step 9 chat summary: total proposals, # added this run, # stale.

Call `update_note` once on the Proposals note after the scan, even if no items
changed (idempotent). Use the version from the get_note that started this step.

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
- **Discrimination is structural.** Where a task lives = who created it.
  `Claude Tasks` note = Summer's directives (Step 7 executes). `Claude Inbox
  Proposals` note = Claude's outbox (Step 7 never executes from here; only
  flags stale items). No inline markers to parse, no syntactic drift.
- **Conservative by default.** When a task is ambiguous, leave it for Summer
  rather than guessing. The Auto-Execution Log only matters if entries are clean.
- **Promotion is Summer's gate.** A proposal becomes a directive when she
  copies the line from Proposals into Claude Tasks (sans date prefix). That
  copy is her explicit consent. Triage never auto-promotes.

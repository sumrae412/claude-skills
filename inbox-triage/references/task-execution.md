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

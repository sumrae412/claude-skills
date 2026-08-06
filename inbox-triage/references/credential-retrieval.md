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

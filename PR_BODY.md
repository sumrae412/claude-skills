# T6 Re-Baseline: PRs #128 + #131 Landed

**Branch:** `henry/land-t6-rebaseline`  
**Author:** charlie (committer) / summerela (original author of T6 work)

---

## (a) T6 PRs Landed

| PR | Title | Cherry-pick SHA |
|----|-------|----------------|
| #128 | `feat(skill-security-auditor): add T6 Agent Trust & Permission Patterns` | `43fba8b6e3e8b7da6f066750ce6bbe94cf3c8541` |
| #131 | `feat(skill-security-auditor): T6 scanner implementation (5 checks)` | `53d2a2ea2c36892831ffd55b83826e3d85d31d31` |

Both cherry-picked onto `origin/main` (HEAD `cf8f4b9`) in dependency order: #128 docs first, then #131 scanner. No conflicts. Auto-merging resolved cleanly on `skill-security-auditor/SKILL.md` in both picks.

---

## (b) Gate Output Before/After Baseline Update

### BEFORE (22 new findings, gate RED)

```
❌ SECURITY GATE: FAIL — 22 new finding(s) not in baseline (12 CRITICAL, 10 HIGH)

  [HIGH]     T6-NO-HITL         claude-flow/scripts/test_workflow_stress_inputs.py:105
  [CRITICAL] T6-LETHAL-TRIFECTA coding-best-practices/docs/api-design.md:55
  [CRITICAL] T6-LETHAL-TRIFECTA defensive-backend-flows/evidence.md:856
  [CRITICAL] T6-LETHAL-TRIFECTA inbox-triage/SKILL.md:62
  [HIGH]     T6-NO-HITL         off-market/scripts/cache.py:90
  [CRITICAL] PRIV-ESC           skill-security-auditor/scripts/skill_security_auditor.py:715
  [CRITICAL] PRIV-ESC           skill-security-auditor/scripts/skill_security_auditor.py:1251
  [HIGH]     FS-ABUSE           skill-security-auditor/scripts/skill_security_auditor.py:1410
  [HIGH]     FS-ABUSE           skill-security-auditor/scripts/skill_security_auditor.py:1422
  [HIGH]     FS-ABUSE           skill-security-auditor/scripts/skill_security_auditor.py:1601
  [CRITICAL] PROMPT-OVERRIDE    skill-security-auditor/SKILL.md:115
  [CRITICAL] SAFETY-BYPASS      skill-security-auditor/SKILL.md:116
  [CRITICAL] SAFETY-BYPASS      skill-security-auditor/SKILL.md:117
  [CRITICAL] PROMPT-EXFIL       skill-security-auditor/SKILL.md:120
  [CRITICAL] PROMPT-EXFIL       skill-security-auditor/references/threat-model.md:341
  [HIGH]     DEPS-RUNTIME       skill-security-auditor/scripts/skill_security_auditor.py:875
  [CRITICAL] T6-LETHAL-TRIFECTA skill-security-auditor/SKILL.md:58
  [CRITICAL] T6-TRUST-BOUNDARY  skill-security-auditor/scripts/skill_security_auditor.py:691
  [HIGH]     T6-NO-HITL         skill-security-auditor/scripts/skill_security_auditor.py:725
  [HIGH]     T6-NO-HITL         skill-security-auditor/scripts/skill_security_auditor.py:1410
  [HIGH]     T6-NO-HITL         skill-security-auditor/scripts/skill_security_auditor.py:1422
  [HIGH]     T6-NO-HITL         skill-security-auditor/scripts/skill_security_auditor.py:1601
```

### AFTER (1 new finding intentionally left unsuppressed, gate still RED)

```
❌ SECURITY GATE: FAIL — 1 new finding(s) not in baseline (1 CRITICAL, 0 HIGH)

  [CRITICAL] T6-LETHAL-TRIFECTA  inbox-triage/SKILL.md:62
    Pattern: untrusted_read@SKILL.md:62; sensitive_access@SKILL.md:4; external_comms@SKILL.md:354
    Risk:    Lethal Trifecta: skill combines untrusted-content read + sensitive-data access + external comms.
```

**The gate will go fully GREEN** once Summer reviews and decides the disposition of the inbox-triage finding (see section d).

---

## (c) Classified New-Baseline Delta Table (21 suppressions added)

| # | Rule ID | Skill | Classification | Reason summary |
|---|---------|-------|---------------|----------------|
| 1 | T6-NO-HITL | claude-flow | tooling-fp | `"rm -rf /\n"` is a Python string literal in a test fixture building a synthetic doc for the scanner to scan. Never executed. |
| 2 | T6-LETHAL-TRIFECTA | coding-best-practices | documented-pattern-example | Documentation-only skill; three bucket hits are code snippet examples in fenced blocks. Skill never executes network/credential ops. |
| 3 | T6-LETHAL-TRIFECTA | defensive-backend-flows | documented-pattern-example | Hit is in `evidence.md`, a bug-log documenting past production bugs involving Gmail/Drive. Not executable; the skill provides defensive patterns only. |
| 4 | T6-NO-HITL | off-market | bounded-tempfile-op | `os.unlink(tmp_name)` in exception-path cleanup of `mkstemp`-created temp file. Same line already baselined as FS-ABUSE. T6-NO-HITL fires on the same construct; same bounded-tempfile analysis applies. |
| 5 | PRIV-ESC | skill-security-auditor | self-match-false-positive | `r'"Bash\(sudo[^"]*\)"'` is the scanner's own regex constant in `PERMISSIONS_ALLOW_BROAD`. Not a sudo call; the PRIV-ESC pattern matches `sudo` inside the regex string. |
| 6 | PRIV-ESC | skill-security-auditor | self-match-false-positive | `"permissions.allow entries (e.g. Bash(*), sudo, curl)"` is a risk-message string output by T6-SCOPE-CREEP. 'sudo' is the name of the thing being warned about. |
| 7 | FS-ABUSE | skill-security-auditor (line 1410) | bounded-tempfile-op | `shutil.rmtree(tmp_dir)` in error-path of `clone_repo_or_local()`. Bounded to `mkdtemp()` path; system-tempdir guard precedes deletion. Same class as existing lines 923/935/1053. |
| 8 | FS-ABUSE | skill-security-auditor (line 1422) | bounded-tempfile-op | Same function, success-path cleanup. Same analysis as line 1410. |
| 9 | FS-ABUSE | skill-security-auditor (line 1601) | bounded-tempfile-op | `shutil.rmtree(cleanup_dir)` in `finally` block of `main()`. Comes from `clone_repo_or_local()` tempdir; system-tempdir guard present. Same class as existing line 1053. |
| 10 | PROMPT-OVERRIDE | skill-security-auditor (SKILL.md:115) | documented-pattern-example | Same table row as existing suppression at SKILL.md:82. Line number shifted +33 due to T6 section insertion. |
| 11 | SAFETY-BYPASS | skill-security-auditor (SKILL.md:116) | documented-pattern-example | Same table row as existing suppression at SKILL.md:83. Line shifted +33. |
| 12 | SAFETY-BYPASS | skill-security-auditor (SKILL.md:117) | documented-pattern-example | Same table row as existing suppression at SKILL.md:84. Line shifted +33. |
| 13 | PROMPT-EXFIL | skill-security-auditor (SKILL.md:120) | documented-pattern-example | Same table row as existing suppression at SKILL.md:87. Line shifted +33. |
| 14 | PROMPT-EXFIL | skill-security-auditor (threat-model.md:341) | documented-pattern-example | New T6 section bullet listing attacker-capability examples. Same family as existing suppression at threat-model.md:324. |
| 15 | DEPS-RUNTIME | skill-security-auditor (line 875) | self-match-false-positive | `# Check for pip/npm install in code` Python comment. Same as existing suppression at line 717; line shifted ~158 due to T6 additions. |
| 16 | T6-LETHAL-TRIFECTA | skill-security-auditor (SKILL.md:58) | self-match-false-positive | Hit is in the T6 known-FP section text describing what the auditor does. All three buckets resolve to documentation prose, not active code. Scanner does not exfiltrate data. |
| 17 | T6-TRUST-BOUNDARY | skill-security-auditor (script:691) | self-match-false-positive | Regex constant definition for T6-TRUST-BOUNDARY detection. The scanner's own source string triggers its own pattern. No actual `load_dotenv()` call. |
| 18 | T6-NO-HITL | skill-security-auditor (script:725) | self-match-false-positive | Entry in `SENSITIVE_ACTION_PATTERNS` list. `"git push"` is the pattern string the scanner searches for; the scanner does not perform git pushes. |
| 19 | T6-NO-HITL | skill-security-auditor (script:1410) | bounded-tempfile-op | Same line as FS-ABUSE suppression. T6-NO-HITL also fires on rmtree; bounded-tempdir analysis identical. |
| 20 | T6-NO-HITL | skill-security-auditor (script:1422) | bounded-tempfile-op | Same as #19. |
| 21 | T6-NO-HITL | skill-security-auditor (script:1601) | bounded-tempfile-op | Same as FS-ABUSE::1601 suppression. |

---

## (d) Finding NOT Suppressed — Needs Summer Review

### ⚠️ GENUINE FINDING: `inbox-triage::T6-LETHAL-TRIFECTA::SKILL.md::62`

**Severity:** CRITICAL  
**Category:** T6-LETHAL-TRIFECTA  
**Pattern:** `untrusted_read@SKILL.md:62; sensitive_access@SKILL.md:4; external_comms@SKILL.md:354`  

**Why this is a true positive:**  
PR #131's own commit body explicitly states: *"inbox-triage correctly flagged for true-positive lethal trifecta (reads Slack/Gmail + accesses Gmail/Drive + sends drafts)."*  

The three buckets:
- **Untrusted read (line 62):** Step 1 instructs fetching up to 50 unread Gmail threads — these contain untrusted content from arbitrary senders.
- **Sensitive access (line 4):** The skill has Gmail/Drive MCP access, described at the SKILL.md frontmatter level.
- **External comms (line 354):** The skill posts a summary to Summer's Slack DM.

This is the canonical example T6 was designed to surface. An adversarial email with a crafted prompt injection could in theory direct the skill to exfiltrate inbox content via the outbound Slack call.

**Risk context:**  
The real-world risk is bounded by the fact that inbox-triage runs in Summer's own account on her behalf — the "attacker" would need to get a malicious email into her inbox. The risk is low-probability but the impact (full inbox exfiltration) is high. This is the correct finding for Summer to consciously accept or mitigate.

**Options:**
1. **Accept (add to baseline with `worth-review/accepted`):** Summer has reviewed the risk, understands that a crafted email could attempt injection, and accepts it as a known trade-off given the operational context (personal account, low-volume, trusted senders dominate).
2. **Mitigate:** Add input sanitization at Step 2 (strip/flag emails with common injection markers before they reach the downstream Slack/Drive steps) and add a baseline entry after the guard is in place.
3. **Scope limit:** Run inbox-triage without the Slack summary step (breaks the external comms bucket), suppressing the finding.

**To add to baseline after Summer's decision:**
```json
{
  "key": "inbox-triage::T6-LETHAL-TRIFECTA::SKILL.md::62",
  "severity": "CRITICAL",
  "category": "T6-LETHAL-TRIFECTA",
  "file": "SKILL.md",
  "line": 62,
  "pattern": "untrusted_read@SKILL.md:62; sensitive_access@SKILL.md:4; external_comms@SKILL.md:354",
  "reason": "worth-review/accepted: TRUE POSITIVE — inbox-triage reads untrusted Gmail + accesses Drive/Gmail credentials + sends Slack summary. Risk accepted: personal-account triage, low injection probability, no automated financial/destructive actions. Reviewed by Summer [DATE]."
}
```

---

## (e) Re-Baseline Review Notes

**Dominant finding class:** self-match false-positives and line-number drift.

- **17 of 21 new suppressions** are in `skill-security-auditor/` and are either: (a) self-match hits where the scanner's own source code contains the exact pattern strings it detects in other skills (by design — a scanner must contain its own patterns), or (b) line-number drift from the existing 22 baseline entries shifted when PR #131 added 585 lines.
- **2 suppressions** are T6-LETHAL-TRIFECTA on documentation skills (`coding-best-practices`, `defensive-backend-flows`) where the heuristic fires on code examples in reference markdown — an expected FP class documented in SKILL.md's known-FP section.
- **1 suppression** is `off-market::T6-NO-HITL::cache.py::90` — a secondary hit on a line already baselined under FS-ABUSE; both fire on the same bounded-tempfile cleanup.
- **1 genuine TP** left unsuppressed: `inbox-triage` (see section d).

**Self-exempt note:**  
The auditor ships a `--self-exempt` flag for exactly this reason. When running in CI against the full repo, the gate does NOT pass `--self-exempt`, so the baseline carries the suppression entries instead. This is correct; the suppressions serve as the audit trail.

**Baseline count:** 53 (original) + 21 (new) = **74 suppressed findings** across 11 skills.

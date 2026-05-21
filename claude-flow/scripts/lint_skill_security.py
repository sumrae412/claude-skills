#!/usr/bin/env python3
"""Conservative security scanner for active claude-flow guidance docs."""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


SKILL_ROOT = Path(__file__).resolve().parents[1]
ERROR_SEVERITIES = {"critical", "high"}


@dataclass(frozen=True)
class ThreatPattern:
    """One scanner rule."""

    pattern: str
    pattern_id: str
    severity: str
    category: str
    description: str


@dataclass(frozen=True)
class Finding:
    """One matched security finding."""

    pattern_id: str
    severity: str
    category: str
    file: str
    line: int
    match: str
    description: str


THREAT_PATTERNS = [
    ThreatPattern(
        r"curl\s+[^\n]*\$\{?\w*(KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|API)",
        "env_exfil_curl",
        "critical",
        "exfiltration",
        "curl command interpolates a likely secret environment variable",
    ),
    ThreatPattern(
        r"wget\s+[^\n]*\$\{?\w*(KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|API)",
        "env_exfil_wget",
        "critical",
        "exfiltration",
        "wget command interpolates a likely secret environment variable",
    ),
    ThreatPattern(
        (
            r"requests\.(get|post|put|patch)\s*\([^\n]*"
            r"(KEY|TOKEN|SECRET|PASSWORD)"
        ),
        "env_exfil_requests",
        "critical",
        "exfiltration",
        "requests call references a likely secret variable",
    ),
    ThreatPattern(
        (
            r"httpx\.(get|post|put|patch)\s*\([^\n]*"
            r"(KEY|TOKEN|SECRET|PASSWORD)"
        ),
        "env_exfil_httpx",
        "critical",
        "exfiltration",
        "httpx call references a likely secret variable",
    ),
    ThreatPattern(
        r"cat\s+[^\n]*(\.env|credentials|\.netrc|\.pgpass|\.npmrc|\.pypirc)",
        "read_secrets_file",
        "critical",
        "exfiltration",
        "reads a known secrets file",
    ),
    ThreatPattern(
        r"\b(printenv|env\s*\|)",
        "dump_all_env",
        "high",
        "exfiltration",
        "dumps all environment variables",
    ),
    ThreatPattern(
        r"\$HOME/\.ssh|~/\.ssh|\$HOME/\.aws|~/\.aws|\$HOME/\.kube|~/\.kube",
        "credential_store_access",
        "high",
        "exfiltration",
        "references a local credential store",
    ),
    ThreatPattern(
        r"ignore\s+(?:\w+\s+)*(previous|all|above|prior)\s+instructions",
        "prompt_injection_ignore",
        "critical",
        "injection",
        "prompt injection asks the agent to ignore instructions",
    ),
    ThreatPattern(
        (
            r"disregard\s+(?:\w+\s+)*(your|all|any)\s+"
            r"(?:\w+\s+)*(instructions|rules|guidelines)"
        ),
        "prompt_injection_disregard",
        "critical",
        "injection",
        "prompt injection asks the agent to disregard rules",
    ),
    ThreatPattern(
        r"do\s+not\s+(?:\w+\s+)*tell\s+(?:\w+\s+)*the\s+user",
        "deception_hide",
        "critical",
        "injection",
        "instructs the agent to hide information from the user",
    ),
    ThreatPattern(
        (
            r"system\s+prompt\s+override|"
            r"output\s+(?:\w+\s+)*(system|initial)\s+prompt"
        ),
        "system_prompt_attack",
        "high",
        "injection",
        "attempts to override or extract the system prompt",
    ),
    ThreatPattern(
        r"rm\s+-rf\s+/",
        "destructive_root_rm",
        "critical",
        "destructive",
        "recursive delete from filesystem root",
    ),
    ThreatPattern(
        r"rm\s+(-[^\s]*)?r.*\$HOME|\brmdir\s+.*\$HOME",
        "destructive_home_rm",
        "critical",
        "destructive",
        "recursive delete targeting the home directory",
    ),
    ThreatPattern(
        r"authorized_keys|/etc/sudoers|\bvisudo\b",
        "privilege_persistence",
        "critical",
        "persistence",
        "modifies SSH authorization or sudoers configuration",
    ),
    ThreatPattern(
        r"<!--[^>]*(ignore|override|system|secret|hidden)[^>]*-->",
        "hidden_instruction_comment",
        "high",
        "injection",
        "hidden HTML comment contains instruction-like text",
    ),
]


def default_scan_files(skill_root: Path) -> list[Path]:
    """Return active guidance docs to scan."""
    paths = [skill_root / "SKILL.md", skill_root / "README.md"]
    for dirname in ("phases", "references", "contracts"):
        paths.extend(sorted((skill_root / dirname).glob("*.md")))
    return [path for path in paths if path.exists()]


def scan_text(text: str, file_label: str) -> list[Finding]:
    """Scan one text blob and return findings."""
    findings: list[Finding] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for threat in THREAT_PATTERNS:
            match = re.search(threat.pattern, line, flags=re.IGNORECASE)
            if not match:
                continue
            findings.append(
                Finding(
                    pattern_id=threat.pattern_id,
                    severity=threat.severity,
                    category=threat.category,
                    file=file_label,
                    line=lineno,
                    match=match.group(0)[:160],
                    description=threat.description,
                )
            )
    return findings


def lint_skill_security(
    skill_root: Path = SKILL_ROOT,
    files: Iterable[Path] | None = None,
) -> dict:
    """Scan active docs for high-risk instruction or shell patterns."""
    scan_files = (
        list(files)
        if files is not None
        else default_scan_files(skill_root)
    )
    findings: list[Finding] = []

    for path in scan_files:
        try:
            text = path.read_text()
        except UnicodeDecodeError:
            continue
        if path.is_relative_to(skill_root):
            label = str(path.relative_to(skill_root))
        else:
            label = str(path)
        findings.extend(scan_text(text, label))

    errors = [
        (
            f"{finding.file}:{finding.line}: "
            f"{finding.severity} {finding.pattern_id}: "
            f"{finding.description}"
        )
        for finding in findings
        if finding.severity in ERROR_SEVERITIES
    ]
    warnings = [
        (
            f"{finding.file}:{finding.line}: "
            f"{finding.severity} {finding.pattern_id}: "
            f"{finding.description}"
        )
        for finding in findings
        if finding.severity not in ERROR_SEVERITIES
    ]

    return {
        "ok": not errors,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "findings": [asdict(finding) for finding in findings],
    }


def main() -> int:
    """Run the security scanner."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-root", type=Path, default=SKILL_ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = lint_skill_security(skill_root=args.skill_root.resolve())
    if args.json:
        json.dump(result, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        status = "ok" if result["ok"] else "fail"
        print(
            "skill-security: "
            f"{status} errors={result['error_count']} "
            f"warnings={result['warning_count']}"
        )
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

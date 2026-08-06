#!/usr/bin/env python3
"""
security_gate.py — Bulk skill-security gate for PR CI.

Scans all skill directories under a given root, compares results against a
baseline file, and exits non-zero only when NEW findings appear (i.e., findings
not in the reviewed baseline).

Usage:
    python3 scripts/security_gate.py [--root DIR] [--baseline FILE] [--json]

Options:
    --root DIR        Root directory containing skill subdirs (default: .)
    --baseline FILE   Path to baseline JSON (default: security-baseline.json)
    --json            Also emit full JSON report to stdout (summary always on stderr)
    --update-baseline Dump current findings as a new baseline to --baseline path
                      (use only during initial seeding, never on CI)

Exit codes:
    0 = No new blocking findings (gate passes — GREEN). Warn-tier findings may
        still be reported; they are printed but do not fail the build.
    1 = New blocking findings detected beyond the baseline (gate fails — RED)

Warn tier:
    A detector class can be landed in report-only mode by listing its category
    prefix under `_meta.warn_only_categories` in the baseline file. Matching
    findings are printed under a WARN heading and excluded from the exit code.

    This exists so a new detector can be measured before it can block a merge.
    The alternative — landing a detector and immediately baselining everything
    it finds — ships it pre-silenced, which is close to not shipping it.

    Run with --strict to promote warn-tier findings back to blocking. That is
    how you check whether a class is ready to gate, and it is what CI should
    switch to once the false-positive rate is known.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Locate skill_security_auditor.py relative to this script.
_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent

# Try the canonical location; fall back to finding it.
_AUDITOR_CANDIDATES = [
    _REPO_ROOT / "skill-security-auditor" / "scripts" / "skill_security_auditor.py",
]


def _find_auditor() -> Path:
    for candidate in _AUDITOR_CANDIDATES:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "skill_security_auditor.py not found. Expected at "
        "skill-security-auditor/scripts/skill_security_auditor.py"
    )


def _import_auditor():
    """Import scan_skill from the auditor module without running main()."""
    import importlib.util

    auditor_path = _find_auditor()
    spec = importlib.util.spec_from_file_location("skill_security_auditor", auditor_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def find_skill_dirs(root: Path) -> list[Path]:
    """Return all immediate subdirs of root that contain a SKILL.md."""
    skills = []
    for item in sorted(root.iterdir()):
        if item.is_dir() and not item.name.startswith("."):
            if (item / "SKILL.md").exists():
                skills.append(item)
    return skills


def finding_key(skill_name: str, finding: dict) -> str:
    """Stable string key for a finding: skill + category + file + line."""
    # Use relative file path (strip repo-absolute prefix if present)
    file_path = finding["file"]
    # Normalise to skill-relative path so the key is portable across machines
    try:
        rel = Path(file_path).relative_to(Path(file_path).parts[0] + "/" if file_path.startswith("/") else "")
    except ValueError:
        rel = Path(file_path)
    # Best effort: strip everything up to and including the skill name
    parts = Path(file_path).parts
    if skill_name in parts:
        idx = list(parts).index(skill_name)
        rel = Path(*parts[idx:])
    else:
        rel = Path(file_path).name
    return f"{skill_name}::{finding['category']}::{rel}::{finding['line']}"


def scan_all(root: Path, auditor_mod) -> dict[str, dict]:
    """Scan every skill dir; return dict skill_name -> audit report dict."""
    results = {}
    skill_dirs = find_skill_dirs(root)
    for skill_dir in skill_dirs:
        report = auditor_mod.scan_skill(skill_dir)
        results[skill_dir.name] = report.to_dict()
    return results


def load_baseline(baseline_path: Path) -> dict:
    """Load baseline JSON; return empty dict if the file doesn't exist."""
    if not baseline_path.exists():
        return {}
    try:
        return json.loads(baseline_path.read_text())
    except json.JSONDecodeError as e:
        print(f"ERROR: baseline file is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)


def build_baseline_keys(baseline: dict) -> set[str]:
    """Flatten baseline into a set of finding keys."""
    keys: set[str] = set()
    for skill_name, entries in baseline.items():
        for entry in entries.get("suppressed_findings", []):
            keys.add(entry["key"])
    return keys


def warn_only_prefixes(baseline: dict) -> tuple[str, ...]:
    """Category prefixes that report but do not block, from `_meta`.

    Kept in the baseline rather than hardcoded here so the policy sits next to
    the suppressions it interacts with, and so promoting a class to blocking is
    a reviewable one-line data change rather than a code change.
    """
    meta = baseline.get("_meta", {})
    prefixes = meta.get("warn_only_categories", [])
    if not isinstance(prefixes, list):
        print(
            "ERROR: _meta.warn_only_categories must be a list of category prefixes",
            file=sys.stderr,
        )
        sys.exit(1)
    return tuple(str(p) for p in prefixes)


def is_warn_only(category: str, prefixes: tuple[str, ...]) -> bool:
    return any(category.startswith(p) for p in prefixes)


def detect_new_findings(
    scan_results: dict[str, dict],
    baseline_keys: set[str],
) -> list[dict]:
    """Return findings whose key is NOT in the baseline."""
    new = []
    for skill_name, report in scan_results.items():
        for finding in report["findings"]:
            sev = finding["severity"]
            if sev not in ("CRITICAL", "HIGH"):
                continue  # Only gate on CRITICAL/HIGH
            key = finding_key(skill_name, finding)
            if key not in baseline_keys:
                new.append(
                    {
                        "skill": skill_name,
                        "key": key,
                        "severity": sev,
                        "category": finding["category"],
                        "file": finding["file"],
                        "line": finding["line"],
                        "pattern": finding["pattern"],
                        "risk": finding["risk"],
                    }
                )
    return new


def _relative_file(file_path: str, root: Path) -> str:
    """Return a root-relative path string for baseline portability."""
    try:
        return str(Path(file_path).relative_to(root))
    except ValueError:
        return file_path


def dump_baseline(scan_results: dict[str, dict], root: Path) -> dict:
    """Build a baseline dict from current scan results (seeding helper)."""
    baseline: dict[str, dict] = {}
    for skill_name, report in scan_results.items():
        suppressed = []
        for finding in report["findings"]:
            sev = finding["severity"]
            if sev not in ("CRITICAL", "HIGH"):
                continue
            key = finding_key(skill_name, finding)
            suppressed.append(
                {
                    "key": key,
                    "severity": sev,
                    "category": finding["category"],
                    "file": _relative_file(finding["file"], root),
                    "line": finding["line"],
                    "pattern": finding["pattern"],
                    "reason": "TODO: classify this finding before committing baseline",
                }
            )
        if suppressed:
            baseline[skill_name] = {"suppressed_findings": suppressed}
    return baseline


def main() -> int:
    parser = argparse.ArgumentParser(description="Bulk security gate for skill directories")
    parser.add_argument("--root", default=".", help="Root dir containing skill subdirs")
    parser.add_argument(
        "--baseline",
        default="security-baseline.json",
        help="Path to baseline JSON file",
    )
    parser.add_argument("--json", dest="json_output", action="store_true")
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="Write current findings as a new baseline (seeding only, never on CI)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warn-tier findings as blocking (use to check whether a "
             "warn-only category is ready to gate)",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    baseline_path = Path(args.baseline)
    if not baseline_path.is_absolute():
        baseline_path = Path(args.root).resolve() / baseline_path

    auditor_mod = _import_auditor()

    print(f"Scanning skills under: {root}", file=sys.stderr)
    scan_results = scan_all(root, auditor_mod)
    skill_count = len(scan_results)
    print(f"Scanned {skill_count} skills.", file=sys.stderr)

    if args.update_baseline:
        baseline = dump_baseline(scan_results, root)
        baseline_path.write_text(json.dumps(baseline, indent=2) + "\n")
        print(f"Baseline written to {baseline_path} ({sum(len(v['suppressed_findings']) for v in baseline.values())} suppressed findings across {len(baseline)} skills).", file=sys.stderr)
        return 0

    baseline = load_baseline(baseline_path)
    baseline_keys = build_baseline_keys(baseline)
    new_findings = detect_new_findings(scan_results, baseline_keys)

    # Split into blocking and warn-tier. --strict collapses the distinction,
    # which is how you test whether a warn-only class is ready to gate.
    prefixes = warn_only_prefixes(baseline)
    if args.strict:
        blocking, warnings = new_findings, []
    else:
        blocking = [f for f in new_findings if not is_warn_only(f["category"], prefixes)]
        warnings = [f for f in new_findings if is_warn_only(f["category"], prefixes)]

    total_critical = sum(1 for f in blocking if f["severity"] == "CRITICAL")
    total_high = sum(1 for f in blocking if f["severity"] == "HIGH")

    if args.json_output:
        summary = {
            "skills_scanned": skill_count,
            "baseline_suppressions": len(baseline_keys),
            "warn_only_categories": list(prefixes),
            "strict": args.strict,
            "new_findings_count": len(blocking),
            "new_critical": total_critical,
            "new_high": total_high,
            "new_findings": blocking,
            "warn_findings_count": len(warnings),
            "warn_findings": warnings,
        }
        print(json.dumps(summary, indent=2))

    def _render(findings: list[dict]) -> None:
        for f in findings:
            print(
                f"  [{f['severity']}] {f['category']}  {f['file']}:{f['line']}",
                file=sys.stderr,
            )
            print(f"    Pattern: {f['pattern'][:100]}", file=sys.stderr)
            print(f"    Risk:    {f['risk']}", file=sys.stderr)

    if warnings:
        by_cat: dict[str, int] = {}
        for f in warnings:
            by_cat[f["category"]] = by_cat.get(f["category"], 0) + 1
        spread = ", ".join(f"{c}={n}" for c, n in sorted(by_cat.items()))
        print(
            f"\n⚠️  SECURITY GATE: {len(warnings)} warn-tier finding(s) "
            f"— reported, not blocking ({spread})\n",
            file=sys.stderr,
        )
        _render(warnings)
        print(
            "\nThese categories are listed in _meta.warn_only_categories and do not "
            "fail the build. Re-run with --strict to see whether they would.",
            file=sys.stderr,
        )

    if blocking:
        print(
            f"\n❌ SECURITY GATE: FAIL — {len(blocking)} new blocking finding(s) not in baseline "
            f"({total_critical} CRITICAL, {total_high} HIGH)\n",
            file=sys.stderr,
        )
        _render(blocking)
        print(
            "\nTo suppress a finding, add it with a `reason` to security-baseline.json "
            "and open a PR for review.",
            file=sys.stderr,
        )
        return 1

    suppressed_count = len(baseline_keys)
    warn_note = f", {len(warnings)} warn-tier reported" if warnings else ""
    print(
        f"✅ SECURITY GATE: PASS — no new blocking findings "
        f"({suppressed_count} baseline-suppressed finding(s) unchanged{warn_note})",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

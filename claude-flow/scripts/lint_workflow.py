#!/usr/bin/env python3
"""Lint claude-flow workflow metadata and active guidance docs.

This is a fast deterministic maintenance check. It catches workflow drift that
is easy to miss in prose review:

- stale skill-root script references in active docs
- mutating path phase-sequence regressions
- missing run-manifest / capability-matrix references
- broken Phase 6 review-base helper resolution
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from lint_skill_metadata import lint_skill_metadata
from lint_skill_security import lint_skill_security
from resolve_review_base import resolve_review_base


SKILL_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = SKILL_ROOT.parent
LEGACY_PATTERNS = {
    "legacy skill script prefix": "skills/claude-flow/scripts",
    "hardcoded HEAD~1 review base": "HEAD~1",
}
RAW_REVIEW_SCRUB = (
    "scrub_review_payload.py > /tmp/claude-flow-review.diff"
)
EXPECTED_MUTATING_PATHS = {
    "plan": ["phase-1", "phase-4c", "phase-5", "phase-5.5", "phase-6"],
    "clone": ["phase-1", "phase-4c", "phase-5", "phase-5.5", "phase-6"],
    "lite": [
        "phase-1",
        "phase-2",
        "phase-3",
        "phase-4",
        "phase-4c",
        "phase-5",
        "phase-5.5",
        "phase-6",
    ],
    "full": [
        "phase-1",
        "phase-2",
        "phase-3",
        "phase-4",
        "phase-4c",
        "phase-4d",
        "phase-5",
        "phase-5.5",
        "phase-6",
    ],
}
REQUIRED_TRANSITIONS = {
    ("phase-1", "phase-4c"),
    ("phase-4", "phase-4c"),
    ("phase-4c", "phase-4d"),
    ("phase-4c", "phase-5"),
}


def active_docs(skill_root: Path) -> list[Path]:
    return [
        skill_root / "SKILL.md",
        skill_root / "README.md",
        skill_root / "phases" / "phase-3-requirements.md",
        skill_root / "phases" / "phase-4-architecture.md",
        skill_root / "phases" / "phase-4c-verification.md",
        skill_root / "phases" / "phase-6-quality.md",
        skill_root / "references" / "memory-injection.md",
        skill_root / "references" / "lookup-detectors.md",
        skill_root / "references" / "subagent-driven-development.md",
    ]


def required_reference_files(skill_root: Path) -> dict[Path, str]:
    return {
        skill_root / "references" / "run-manifest.md": (
            "run-manifest reference missing"
        ),
        skill_root / "references" / "project-capability-matrix.md": (
            "project-capability-matrix reference missing"
        ),
    }


def required_helper_files(skill_root: Path) -> dict[Path, str]:
    return {
        skill_root / "scripts" / "run_manifest.py": "run-manifest helper missing",
    }


def load_profiles(skill_root: Path) -> dict:
    return json.loads((skill_root / "workflow-profiles.json").read_text())


def lint_active_docs(skill_root: Path) -> list[str]:
    errors: list[str] = []
    for path in active_docs(skill_root):
        if not path.exists():
            errors.append(
                f"{path.relative_to(skill_root)}: active workflow doc missing"
            )
            continue
        text = path.read_text()
        for label, pattern in LEGACY_PATTERNS.items():
            if pattern not in text:
                continue
            if label == "hardcoded HEAD~1 review base" and path.name != "phase-6-quality.md":
                continue
            errors.append(f"{path.relative_to(skill_root)}: {label}")
        if path.name == "phase-6-quality.md":
            has_raw_pipe = RAW_REVIEW_SCRUB in text.replace("\\\n", "")
            has_orchestrated_scrub = "orchestrate.py scrub-diff" in text
            has_redactions_output = "--redactions-output" in text
            if has_raw_pipe and not (
                has_orchestrated_scrub and has_redactions_output
            ):
                errors.append(
                    f"{path.relative_to(skill_root)}: phase 6 review scrub "
                    "must preserve redaction summaries"
                )
    return errors


def lint_mutating_paths(skill_root: Path) -> list[str]:
    errors: list[str] = []
    profiles = load_profiles(skill_root)
    paths = profiles["paths"]

    for path_name, expected in EXPECTED_MUTATING_PATHS.items():
        actual = paths[path_name]["phases"]
        if actual != expected:
            errors.append(
                f"workflow-profiles.json: path '{path_name}' phases drifted: "
                f"expected {expected}, found {actual}"
            )

    audit = paths["audit"]
    if audit["mutation_allowed"] is not False:
        errors.append("workflow-profiles.json: audit path must remain read-only")
    if "phase-5" in audit["phases"]:
        errors.append("workflow-profiles.json: audit path must skip phase-5")

    transitions = {
        (entry["from"], entry["to"])
        for entry in profiles.get("phase_transitions", [])
    }
    for required in sorted(REQUIRED_TRANSITIONS):
        if required not in transitions:
            errors.append(
                "workflow-profiles.json: missing phase transition "
                f"{required[0]} -> {required[1]}"
            )

    return errors


def lint_reference_assets(skill_root: Path) -> list[str]:
    errors: list[str] = []
    for path, message in required_reference_files(skill_root).items():
        if not path.exists():
            errors.append(f"{path.relative_to(skill_root)}: {message}")
    for path, message in required_helper_files(skill_root).items():
        if not path.exists():
            errors.append(f"{path.relative_to(skill_root)}: {message}")
    return errors


def _is_git_repo(project_root: Path) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--git-dir"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def lint_review_base(project_root: Path) -> tuple[list[str], list[str], dict | None]:
    errors: list[str] = []
    warnings: list[str] = []

    if not _is_git_repo(project_root):
        warnings.append(
            f"{project_root}: skipped review-base smoke check because this is not a git repo"
        )
        return errors, warnings, None

    try:
        result = resolve_review_base(project_root)
    except Exception as exc:  # pragma: no cover - defensive runtime envelope
        errors.append(f"resolve_review_base failed: {exc}")
        return errors, warnings, None

    if not result.get("review_base_sha"):
        errors.append("resolve_review_base returned no review_base_sha")
    return errors, warnings, result


def lint_workflow(
    skill_root: Path = SKILL_ROOT,
    project_root: Path = WORKSPACE_ROOT,
    include_review_base: bool = True,
) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    errors.extend(lint_active_docs(skill_root))
    errors.extend(lint_mutating_paths(skill_root))
    errors.extend(lint_reference_assets(skill_root))

    metadata_result = lint_skill_metadata(
        skill_root=skill_root,
        workspace_root=skill_root.parent,
    )
    errors.extend(
        f"skill metadata: {error}" for error in metadata_result["errors"]
    )
    warnings.extend(
        f"skill metadata: {warning}" for warning in metadata_result["warnings"]
    )

    security_result = lint_skill_security(skill_root=skill_root)
    errors.extend(
        f"skill security: {error}" for error in security_result["errors"]
    )
    warnings.extend(
        f"skill security: {warning}" for warning in security_result["warnings"]
    )

    review_base_result = None
    if include_review_base:
        rb_errors, rb_warnings, review_base_result = lint_review_base(project_root)
        errors.extend(rb_errors)
        warnings.extend(rb_warnings)

    return {
        "ok": not errors,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "review_base": review_base_result,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skill-root",
        type=Path,
        default=SKILL_ROOT,
        help="Path to the claude-flow skill root",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=WORKSPACE_ROOT,
        help="Project root used for the review-base smoke check",
    )
    parser.add_argument(
        "--skip-review-base",
        action="store_true",
        help="Skip the git-backed review-base smoke check",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of a text summary",
    )
    args = parser.parse_args()

    result = lint_workflow(
        skill_root=args.skill_root.resolve(),
        project_root=args.project_root.resolve(),
        include_review_base=not args.skip_review_base,
    )

    if args.json:
        json.dump(result, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        if result["ok"]:
            print("claude-flow workflow lint: OK")
        else:
            print("claude-flow workflow lint: FAIL")
            for error in result["errors"]:
                print(f"  - {error}")
        for warning in result["warnings"]:
            print(f"  ! {warning}")

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

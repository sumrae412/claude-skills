#!/usr/bin/env python3
"""Warn on skills with weak persona/role contracts.

Default mode is intentionally soft: it reports weak contracts and exits 0.
Use --strict only after the documented exclusions have been reviewed or fixed.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXCLUSIONS_PATH = (
    REPO_ROOT
    / "docs"
    / "decisions"
    / "2026-07-09-persona-contract-lint-exclusions.md"
)
EXCLUDED_TOP_LEVEL_DIRS = {
    ".git",
    ".knowledge",
    "web-scraping-efficient-workspace",
}

SIGNAL_PATTERNS = {
    "metadata": re.compile(r"\A---\n"),
    "role_contract": re.compile(
        r"(?im)^##\s+(Role Contract|Who you are|Your role)\b"
        r"|\byou are (?:a|an|the)\b"
        r"|\byour role is\b"
        r"|\bact as (?:a|an|the)\b"
    ),
    "scope": re.compile(
        r"(?im)^##\s+"
        r"(Scope|Mission|Goal|Overview|When to Use|Use when|Trigger|"
        r"Triggers|Purpose|Core Identity)\b"
        r"|\b(use when|use for|use this skill when|this skill (?:is )?for|"
        r"helps? (?:you|the user)|your job is|mission is|goal is|"
        r"purpose is|when the user asks|when asked)\b"
    ),
    "boundary": re.compile(
        r"(?im)^##\s+"
        r"(Boundary|Boundaries|Guardrails?|Non-goals|Constraints|"
        r"Professional Boundary|Verification|ENFORCEMENT|Safety|Limits?|"
        r"Rules?|When NOT to use)\b"
        r"|\b(do not|must not|never|only|stop and ask|outside scope|"
        r"not provide|not a substitute|avoid|require|requires|required|"
        r"forbidden|cannot|should not)\b"
    ),
    "output": re.compile(
        r"(?im)^##\s+"
        r"(Output|Deliverables?|Reports?|Result|Response|Artifacts?|"
        r"Output Files|Success Criteria|What to Return|Template)\b"
        r"|\b(output|deliverable|report|return|respond with|write|produce|"
        r"artifact|create|generate|emit|provide|summary|checklist|plan|"
        r"recommendation|findings)\b"
    ),
}


@dataclass(frozen=True)
class SkillContract:
    name: str
    path: str
    score: int
    missing: list[str]
    signals: dict[str, bool]
    excluded: bool


def iter_skill_files(skill_root: Path) -> list[tuple[str, Path]]:
    """Return top-level skill files, accepting SKILL.md and legacy skill.md."""
    skill_files: list[tuple[str, Path]] = []
    for child in sorted(skill_root.iterdir()):
        if (
            not child.is_dir()
            or child.name.startswith(".")
            or child.name in EXCLUDED_TOP_LEVEL_DIRS
        ):
            continue

        skill_path = child / "SKILL.md"
        if not skill_path.exists():
            skill_path = child / "skill.md"
        if skill_path.exists():
            skill_files.append((child.name, skill_path))
    return skill_files


def load_exclusions(exclusions_path: Path) -> set[str]:
    """Load markdown exclusions from bullets formatted as: - `skill-name` ..."""
    if not exclusions_path.exists():
        return set()

    exclusions: set[str] = set()
    for line in exclusions_path.read_text().splitlines():
        match = re.match(r"\s*-\s*`([^`]+)`", line)
        if match:
            exclusions.add(match.group(1))
    return exclusions


def score_skill(name: str, skill_path: Path, exclusions: set[str]) -> SkillContract:
    text = skill_path.read_text(errors="replace")
    signals = {
        signal: bool(pattern.search(text))
        for signal, pattern in SIGNAL_PATTERNS.items()
    }
    missing = [signal for signal, present in signals.items() if not present]
    return SkillContract(
        name=name,
        path=str(skill_path),
        score=sum(signals.values()),
        missing=missing,
        signals=signals,
        excluded=name in exclusions,
    )


def lint_persona_contracts(
    skill_root: Path,
    exclusions_path: Path,
    min_score: int,
) -> dict[str, object]:
    exclusions = load_exclusions(exclusions_path)
    contracts = [
        score_skill(name, path, exclusions)
        for name, path in iter_skill_files(skill_root)
    ]
    weak = [contract for contract in contracts if contract.score < min_score]
    unexcluded = [contract for contract in weak if not contract.excluded]
    excluded = [contract for contract in weak if contract.excluded]
    skill_names = {contract.name for contract in contracts}
    stale_exclusions = sorted(exclusions - skill_names)

    return {
        "ok": not unexcluded and not stale_exclusions,
        "skill_count": len(contracts),
        "min_score": min_score,
        "weak_count": len(weak),
        "excluded_count": len(excluded),
        "unexcluded_count": len(unexcluded),
        "stale_exclusions": stale_exclusions,
        "weak": [asdict(contract) for contract in weak],
        "unexcluded": [asdict(contract) for contract in unexcluded],
        "excluded": [asdict(contract) for contract in excluded],
    }


def print_text_report(result: dict[str, object], show_all_weak: bool) -> None:
    status = "warn" if result["weak_count"] else "ok"
    print(
        "persona-contract-lint: "
        f"{status} skills={result['skill_count']} "
        f"weak={result['weak_count']} "
        f"excluded={result['excluded_count']} "
        f"unexcluded={result['unexcluded_count']} "
        f"min_score={result['min_score']}"
    )

    for stale in result["stale_exclusions"]:
        print(f"STALE-EXCLUSION: {stale}")

    for contract in result["unexcluded"]:
        missing = ",".join(contract["missing"])
        print(
            f"WARNING: {contract['name']} score={contract['score']} "
            f"missing={missing}"
        )

    if show_all_weak:
        for contract in result["excluded"]:
            missing = ",".join(contract["missing"])
            print(
                f"EXCLUDED: {contract['name']} score={contract['score']} "
                f"missing={missing}"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skill-root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root containing top-level skill directories.",
    )
    parser.add_argument(
        "--exclusions",
        type=Path,
        default=DEFAULT_EXCLUSIONS_PATH,
        help="Markdown file documenting temporary exclusions.",
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=4,
        help="Minimum acceptable score before exclusion. Default: 4.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 when unexcluded weak contracts or stale exclusions exist.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON.",
    )
    parser.add_argument(
        "--show-all-weak",
        action="store_true",
        help="Print excluded weak contracts as EXCLUDED lines.",
    )
    args = parser.parse_args()

    result = lint_persona_contracts(
        skill_root=args.skill_root.resolve(),
        exclusions_path=args.exclusions.resolve(),
        min_score=args.min_score,
    )

    if args.json:
        json.dump(result, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print_text_report(result, show_all_weak=args.show_all_weak)

    if args.strict and not result["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Mechanical reviewer selection for Phase 6 cascading review."""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path


BUDGET_ORDER = {
    "low": 0,
    "medium": 1,
    "high": 2,
}


def bundled_registry_path() -> Path:
    """Return the registry bundled with this claude-flow skill."""
    return Path(__file__).resolve().parents[1] / "reviewer-registry.json"


def bundled_workflow_profiles_path() -> Path:
    """Return the bundled workflow profile metadata."""
    return Path(__file__).resolve().parents[1] / "workflow-profiles.json"


def load_registry(path: Path) -> dict:
    if not path.exists():
        return {"reviewers": []}
    data = json.loads(path.read_text())
    reviewers = []
    for reviewer in data.get("reviewers", []):
        normalized = dict(reviewer)
        normalized["registry_path"] = str(path)
        if normalized.get("runner_script"):
            normalized["resolved_runner_script"] = str(
                (path.parent / normalized["runner_script"]).resolve()
            )
        if normalized.get("persona_file"):
            if normalized.get("persona_file_root"):
                root = Path(normalized["persona_file_root"]).expanduser()
            else:
                root = path.parent
            normalized["resolved_persona_file"] = str(
                (root / normalized["persona_file"]).expanduser().resolve()
            )
        reviewers.append(normalized)
    data["reviewers"] = reviewers
    return data


def load_workflow_profiles() -> dict:
    """Load the bundled workflow profile metadata."""
    return json.loads(bundled_workflow_profiles_path().read_text())


def merge_registry_data(base: dict, override: dict) -> dict:
    """Merge registry entries by id, with override winning."""
    merged: dict[str, dict] = {}
    for reviewer in base.get("reviewers", []):
        merged[reviewer["id"]] = reviewer
    for reviewer in override.get("reviewers", []):
        merged[reviewer["id"]] = reviewer
    return {
        "version": override.get("version", base.get("version")),
        "description": override.get("description", base.get("description")),
        "reviewers": list(merged.values()),
    }


def find_project_registry(start: Path) -> Path | None:
    """Walk up looking for a project-level reviewer registry override."""
    bundled = bundled_registry_path().resolve()
    cur = start.resolve()
    for _ in range(8):
        cand = cur / ".claude" / "reviewer-registry.json"
        if cand.exists():
            return cand
        cand = cur / "reviewer-registry.json"
        if cand.exists() and cand.resolve() != bundled:
            return cand
        if cur == cur.parent:
            break
        cur = cur.parent
    return None


def find_home_registry() -> Path | None:
    """Return the user-global registry override if present."""
    fallback = Path.home() / ".claude" / "reviewer-registry.json"
    return fallback if fallback.exists() else None


def load_effective_registry(start: Path) -> dict:
    """Load bundled defaults plus optional home/project overrides."""
    sources: list[str] = []
    bundled = bundled_registry_path()
    registry = load_registry(bundled)
    sources.append(str(bundled))

    home = find_home_registry()
    if home is not None and home.resolve() != bundled.resolve():
        registry = merge_registry_data(registry, load_registry(home))
        sources.append(str(home))

    project = find_project_registry(start)
    if project is not None:
        registry = merge_registry_data(registry, load_registry(project))
        sources.append(str(project))

    registry["registry_sources"] = sources
    return registry


def file_matches_patterns(file_path: str, patterns: list[str]) -> bool:
    for pat in patterns:
        if fnmatch.fnmatch(file_path, pat):
            return True
        # Also try matching without leading **/ for convenience
        if pat.startswith("**/") and fnmatch.fnmatch(file_path, pat[3:]):
            return True
        if not pat.startswith("**/") and fnmatch.fnmatch(file_path, f"**/{pat}"):
            return True
    return False


def count_content_matches(matched_files: list[str], pattern: str, diff_dir: Path) -> int:
    """Count occurrences of `pattern` (regex) across the matched files.

    Reads each file from diff_dir; missing files contribute 0. Used for the
    `content_pattern` + `threshold` reviewer gating in the registry.
    """
    if not pattern:
        return 0
    rx = re.compile(pattern, re.MULTILINE)
    total = 0
    for fp in matched_files:
        path = (diff_dir / fp).resolve()
        if not path.exists() or not path.is_file():
            continue
        try:
            text = path.read_text(errors="replace")
        except OSError:
            continue
        total += len(rx.findall(text))
    return total


def budget_at_least(current: str, target: str) -> str:
    """Return the higher of two review budgets."""
    if BUDGET_ORDER[target] > BUDGET_ORDER[current]:
        return target
    return current


def reviewer_matches(
    reviewer: dict, file_paths: list[str], diff_dir: Path
) -> tuple[bool, list[str], str | None]:
    """Evaluate whether a reviewer should trigger on the current diff."""
    patterns = reviewer.get("file_patterns", [])
    matched_files = [fp for fp in file_paths if file_matches_patterns(fp, patterns)]
    if not matched_files:
        return False, [], f"no file matched {patterns}"

    content_pattern = reviewer.get("content_pattern")
    threshold = int(reviewer.get("threshold", 0) or 0)
    if content_pattern and threshold > 0:
        count = count_content_matches(matched_files, content_pattern, diff_dir)
        if count < threshold:
            return (
                False,
                matched_files,
                f"content_pattern matched {count}x; needs ≥{threshold}",
            )

    return True, matched_files, None


def infer_review_budget(
    registry: dict,
    file_paths: list[str],
    diff_dir: Path,
    workflow_path: str | None = None,
) -> tuple[str, list[str]]:
    """Infer a review budget from workflow path plus deterministic diff signals."""
    profiles = load_workflow_profiles()
    budget = "low"
    reasons: list[str] = []

    if workflow_path:
        profile = profiles.get("paths", {}).get(workflow_path, {})
        profile_budget = profile.get("review_budget_default", "low")
        budget = budget_at_least(budget, profile_budget)
        reasons.append(f"workflow path {workflow_path} defaults to {profile_budget}")

    file_count = len(file_paths)
    if file_count >= 3:
        budget = budget_at_least(budget, "medium")
        reasons.append(f"diff touches {file_count} files")
    if file_count >= 8:
        budget = budget_at_least(budget, "high")
        reasons.append(f"diff is broad ({file_count} files)")

    for reviewer in registry.get("reviewers", []):
        reviewer_id = reviewer.get("id")
        if reviewer_id not in {
            "migration-reviewer",
            "google-api-reviewer",
            "async-reviewer",
        }:
            continue
        matched, _, _ = reviewer_matches(reviewer, file_paths, diff_dir)
        if not matched:
            continue
        if reviewer_id in {"migration-reviewer", "google-api-reviewer"}:
            budget = budget_at_least(budget, "high")
            reasons.append(f"{reviewer_id} signal detected")
        else:
            budget = budget_at_least(budget, "medium")
            reasons.append("async signal detected")

    high_path_patterns = [
        ".github/workflows/*.yml",
        ".github/workflows/*.yaml",
        "Dockerfile",
        "docker-compose*.yml",
        "docker-compose*.yaml",
        "railway.json",
        "**/*auth*",
        "**/*security*",
        "**/package.json",
        "**/package-lock.json",
        "**/requirements*.txt",
        "**/pyproject.toml",
        "**/poetry.lock",
        "**/uv.lock",
    ]
    if any(file_matches_patterns(path, high_path_patterns) for path in file_paths):
        budget = budget_at_least(budget, "high")
        reasons.append("infra/auth/dependency-risk files detected")

    ui_patterns = [
        "**/*.html",
        "**/*.css",
        "**/*.scss",
        "**/*.js",
        "**/*.ts",
        "**/*.tsx",
        "**/templates/**",
        "**/static/**",
    ]
    if any(file_matches_patterns(path, ui_patterns) for path in file_paths):
        budget = budget_at_least(budget, "medium")
        reasons.append("user-facing surface touched")

    if not reasons:
        reasons.append("defaulted to low budget")

    return budget, list(dict.fromkeys(reasons))


def review_budget_allows(review_budget: str, reviewer: dict) -> bool:
    """Return whether a reviewer is eligible under the selected budget."""
    min_budget = reviewer.get("min_budget", "low")
    return BUDGET_ORDER[review_budget] >= BUDGET_ORDER[min_budget]


def select(
    registry: dict,
    file_paths: list[str],
    diff_dir: Path,
    review_budget: str,
) -> dict:
    always: list[dict] = []
    matched: list[dict] = []
    skipped: list[dict] = []
    budget_skipped: list[dict] = []
    for r in registry.get("reviewers", []):
        if not review_budget_allows(review_budget, r):
            budget_skipped.append(
                {
                    "id": r["id"],
                    "reason": (
                        f"needs budget {r.get('min_budget', 'low')}; "
                        f"selected {review_budget}"
                    ),
                }
            )
            continue
        if r.get("tier") == "always":
            always.append(r)
            continue

        triggered, matched_files, reason = reviewer_matches(r, file_paths, diff_dir)
        if not triggered:
            skipped.append({"id": r["id"], "reason": reason})
            continue
        matched.append({**r, "matched_files": matched_files})

    by_tier: dict[str, list[str]] = {}
    for r in always + matched:
        tier = str(r.get("cascade_tier", "?"))
        by_tier.setdefault(tier, []).append(r["id"])

    return {
        "always": always,
        "conditional_matched": matched,
        "conditional_skipped": skipped,
        "budget_skipped": budget_skipped,
        "by_tier": by_tier,
        "input_file_count": len(file_paths),
        "review_budget": review_budget,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--registry",
        type=Path,
        default=None,
        help="reviewer-registry.json path (skip bundled/home/project merge)",
    )
    parser.add_argument(
        "--diff-dir",
        type=Path,
        default=Path.cwd(),
        help="Directory to resolve relative paths against for content_pattern checks",
    )
    parser.add_argument(
        "--workflow-path",
        choices=["bug", "fast", "plan", "clone", "lite", "audit", "explore", "full"],
        default=None,
        help="Workflow path used to seed the review budget",
    )
    parser.add_argument(
        "--budget",
        choices=["low", "medium", "high"],
        default=None,
        help="Explicit review budget override",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="File paths from the diff. If empty, read one path per line from stdin.",
    )
    args = parser.parse_args()

    file_paths = args.files
    if not file_paths and not sys.stdin.isatty():
        file_paths = [line.strip() for line in sys.stdin if line.strip()]

    if args.registry is not None:
        registry = load_registry(args.registry)
        registry["registry_sources"] = [str(args.registry)]
    else:
        registry = load_effective_registry(args.diff_dir)

    if args.budget is not None:
        review_budget = args.budget
        budget_reasons = [f"explicit budget override: {args.budget}"]
    else:
        review_budget, budget_reasons = infer_review_budget(
            registry=registry,
            file_paths=file_paths,
            diff_dir=args.diff_dir,
            workflow_path=args.workflow_path,
        )

    result = select(registry, file_paths, args.diff_dir, review_budget)
    result["registry_sources"] = registry.get("registry_sources", [])
    result["budget_reasons"] = budget_reasons
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

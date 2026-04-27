#!/usr/bin/env python3
"""Resolve a deterministic git diff base for Phase 6 reviews.

Preference order:
1. `review_base_sha` from `.claude/workflow-state.json` when still valid
2. `git merge-base HEAD <upstream/default-branch>`
3. `HEAD~1` as a last-resort local fallback
4. `HEAD` for single-commit repositories
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def _run_git(project_root: Path, *args: str) -> tuple[int, str, str]:
    result = subprocess.run(
        ["git", *args],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def _read_state_review_base(project_root: Path) -> str | None:
    state_path = project_root / ".claude" / "workflow-state.json"
    if not state_path.exists():
        return None
    try:
        state = json.loads(state_path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    sha = state.get("review_base_sha")
    return sha if isinstance(sha, str) and sha else None


def _sha_is_ancestor(project_root: Path, sha: str) -> bool:
    code, _, _ = _run_git(project_root, "merge-base", "--is-ancestor", sha, "HEAD")
    return code == 0


def _candidate_refs(project_root: Path) -> list[str]:
    refs: list[str] = []

    code, stdout, _ = _run_git(
        project_root,
        "symbolic-ref",
        "--quiet",
        "--short",
        "refs/remotes/origin/HEAD",
    )
    if code == 0 and stdout:
        refs.append(stdout)

    code, stdout, _ = _run_git(
        project_root,
        "rev-parse",
        "--abbrev-ref",
        "--symbolic-full-name",
        "@{upstream}",
    )
    if code == 0 and stdout:
        refs.append(stdout)

    refs.extend(["origin/main", "origin/master", "main", "master"])

    deduped: list[str] = []
    seen: set[str] = set()
    for ref in refs:
        if ref not in seen:
            deduped.append(ref)
            seen.add(ref)
    return deduped


def _ref_exists(project_root: Path, ref: str) -> bool:
    code, _, _ = _run_git(project_root, "rev-parse", "--verify", ref)
    return code == 0


def resolve_review_base(project_root: Path) -> dict[str, str | None]:
    state_sha = _read_state_review_base(project_root)
    if state_sha and _sha_is_ancestor(project_root, state_sha):
        return {
            "review_base_sha": state_sha,
            "source": "workflow-state",
            "base_ref": None,
        }

    for ref in _candidate_refs(project_root):
        if not _ref_exists(project_root, ref):
            continue
        code, stdout, _ = _run_git(project_root, "merge-base", "HEAD", ref)
        if code == 0 and stdout:
            return {
                "review_base_sha": stdout,
                "source": "merge-base",
                "base_ref": ref,
            }

    code, stdout, _ = _run_git(project_root, "rev-parse", "HEAD~1")
    if code == 0 and stdout:
        return {
            "review_base_sha": stdout,
            "source": "head-parent",
            "base_ref": "HEAD~1",
        }

    code, stdout, _ = _run_git(project_root, "rev-parse", "HEAD")
    if code != 0 or not stdout:
        raise RuntimeError("unable to resolve review base from git history")
    return {
        "review_base_sha": stdout,
        "source": "head",
        "base_ref": "HEAD",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root used for git commands",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of only the SHA",
    )
    args = parser.parse_args()

    result = resolve_review_base(args.project_root.resolve())
    if args.json:
        json.dump(result, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(f"{result['review_base_sha']}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

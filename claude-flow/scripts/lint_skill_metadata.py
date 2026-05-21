#!/usr/bin/env python3
"""Lint claude-flow skill metadata and related-skill references."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = SKILL_ROOT.parent
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_SKILL_CONTENT_CHARS = 100_000
SKILL_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


def parse_scalar(value: str) -> Any:
    """Parse the small YAML subset used by skill frontmatter."""
    value = value.strip()
    if not value:
        return {}
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [
            item.strip().strip("\"'")
            for item in inner.split(",")
            if item.strip()
        ]
    if (
        (value.startswith('"') and value.endswith('"'))
        or (value.startswith("'") and value.endswith("'"))
    ):
        return value[1:-1]
    return value


def parse_frontmatter(frontmatter: str) -> dict[str, Any]:
    """Parse simple indentation-based frontmatter into a nested dict."""
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]

    for lineno, raw_line in enumerate(frontmatter.splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if "\t" in raw_line[:indent]:
            raise ValueError(
                f"frontmatter line {lineno}: tabs are not supported"
            )
        if ":" not in raw_line:
            raise ValueError(f"frontmatter line {lineno}: expected key: value")

        key, raw_value = raw_line.strip().split(":", 1)
        if not key:
            raise ValueError(f"frontmatter line {lineno}: empty key")

        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            raise ValueError(f"frontmatter line {lineno}: invalid indentation")

        parent = stack[-1][1]
        value = parse_scalar(raw_value)
        parent[key] = value
        if isinstance(value, dict):
            stack.append((indent, value))

    return root


def extract_frontmatter(
    skill_path: Path,
) -> tuple[dict[str, Any] | None, str, str | None]:
    """Return parsed frontmatter, body, and an optional error."""
    if not skill_path.exists():
        return None, "", "SKILL.md missing"

    content = skill_path.read_text()
    if len(content) > MAX_SKILL_CONTENT_CHARS:
        return None, "", (
            f"SKILL.md exceeds {MAX_SKILL_CONTENT_CHARS:,} characters"
        )
    if not content.startswith("---\n"):
        return None, "", "SKILL.md must start with frontmatter delimiter"

    closing = content.find("\n---\n", 4)
    if closing == -1:
        return None, "", "SKILL.md frontmatter closing delimiter missing"

    raw_frontmatter = content[4:closing]
    body = content[closing + 5 :]
    try:
        metadata = parse_frontmatter(raw_frontmatter)
    except ValueError as exc:
        return None, body, str(exc)
    return metadata, body, None


def _nested_get(payload: dict[str, Any], keys: tuple[str, ...]) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def lint_skill_metadata(
    skill_root: Path = SKILL_ROOT,
    workspace_root: Path | None = None,
) -> dict[str, Any]:
    """Lint claude-flow SKILL.md metadata and related-skill references."""
    workspace_root = workspace_root or skill_root.parent
    errors: list[str] = []
    warnings: list[str] = []
    skill_path = skill_root / "SKILL.md"
    frontmatter, body, parse_error = extract_frontmatter(skill_path)

    if parse_error:
        errors.append(f"SKILL.md: {parse_error}")
        frontmatter = None

    if frontmatter is None:
        return {
            "ok": False,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "errors": errors,
            "warnings": warnings,
        }

    name = frontmatter.get("name")
    if not isinstance(name, str) or not name:
        errors.append("SKILL.md: missing required frontmatter field 'name'")
    elif len(name) > MAX_NAME_LENGTH or not SKILL_NAME_RE.fullmatch(name):
        errors.append(
            "SKILL.md: name must be lowercase kebab-case and <= "
            f"{MAX_NAME_LENGTH} chars"
        )

    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append(
            "SKILL.md: missing required frontmatter field 'description'"
        )
    elif len(description) > MAX_DESCRIPTION_LENGTH:
        errors.append(
            "SKILL.md: description exceeds "
            f"{MAX_DESCRIPTION_LENGTH} characters"
        )

    if not isinstance(frontmatter.get("version"), str):
        errors.append("SKILL.md: missing required frontmatter field 'version'")

    hermes_meta = _nested_get(frontmatter, ("metadata", "hermes"))
    if not isinstance(hermes_meta, dict):
        errors.append("SKILL.md: missing metadata.hermes block")
        hermes_meta = {}

    tags = hermes_meta.get("tags")
    if not isinstance(tags, list) or not tags:
        errors.append(
            "SKILL.md: metadata.hermes.tags must be a non-empty list"
        )

    related_skills = hermes_meta.get("related_skills")
    if not isinstance(related_skills, list):
        errors.append(
            "SKILL.md: metadata.hermes.related_skills must be a list"
        )
        related_skills = []

    for related in related_skills:
        is_valid_related = (
            isinstance(related, str)
            and SKILL_NAME_RE.fullmatch(related)
        )
        if not is_valid_related:
            errors.append(
                "SKILL.md: related skill names must be lowercase kebab-case: "
                f"{related!r}"
            )
            continue
        related_path = workspace_root / related / "SKILL.md"
        if not related_path.exists():
            errors.append(
                "SKILL.md: related skill does not resolve: "
                f"{related} ({related_path})"
            )

    prerequisites = frontmatter.get("prerequisites")
    has_bad_prerequisites = (
        prerequisites is not None
        and not isinstance(prerequisites, (list, dict))
    )
    if has_bad_prerequisites:
        errors.append(
            "SKILL.md: prerequisites must be a list or mapping when present"
        )

    if not body.strip():
        errors.append("SKILL.md: body must not be empty")

    return {
        "ok": not errors,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    """Run the metadata linter."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-root", type=Path, default=SKILL_ROOT)
    parser.add_argument("--workspace-root", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = lint_skill_metadata(
        skill_root=args.skill_root.resolve(),
        workspace_root=(
            args.workspace_root.resolve() if args.workspace_root else None
        ),
    )
    if args.json:
        json.dump(result, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        status = "ok" if result["ok"] else "fail"
        print(
            "skill-metadata: "
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

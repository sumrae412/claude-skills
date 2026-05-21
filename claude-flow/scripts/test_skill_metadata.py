from pathlib import Path

from lint_skill_metadata import lint_skill_metadata, parse_frontmatter


def _write_skill(root: Path, text: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "SKILL.md").write_text(text)


def _valid_skill(name: str = "claude-flow") -> str:
    return f"""---
name: {name}
description: Use when testing metadata validation.
version: 1.0.0
user-invocable: true
metadata:
  hermes:
    tags: [coding, workflow, unicode-résumé]
    related_skills: [smart-exploration]
---

# {name}
"""


def test_parse_frontmatter_handles_nested_lists_and_booleans():
    parsed = parse_frontmatter(
        """name: claude-flow
user-invocable: true
metadata:
  hermes:
    tags: [coding, workflow]
    related_skills: []
"""
    )

    assert parsed["name"] == "claude-flow"
    assert parsed["user-invocable"] is True
    assert parsed["metadata"]["hermes"]["tags"] == ["coding", "workflow"]
    assert parsed["metadata"]["hermes"]["related_skills"] == []


def test_lint_skill_metadata_accepts_valid_skill_with_related_skill(
    tmp_path: Path,
):
    skill_root = tmp_path / "claude-flow"
    related_root = tmp_path / "smart-exploration"
    _write_skill(skill_root, _valid_skill())
    _write_skill(related_root, _valid_skill("smart-exploration"))

    result = lint_skill_metadata(
        skill_root=skill_root,
        workspace_root=tmp_path,
    )

    assert result["ok"] is True
    assert result["errors"] == []


def test_lint_skill_metadata_rejects_path_traversal_related_skill(
    tmp_path: Path,
):
    skill_root = tmp_path / "claude-flow"
    _write_skill(
        skill_root,
        """---
name: claude-flow
description: Use when testing metadata validation.
version: 1.0.0
metadata:
  hermes:
    tags: [coding]
    related_skills: [../secret]
---

# Bad
""",
    )

    result = lint_skill_metadata(
        skill_root=skill_root,
        workspace_root=tmp_path,
    )

    assert result["ok"] is False
    assert any("related skill names" in error for error in result["errors"])


def test_lint_skill_metadata_rejects_missing_body(tmp_path: Path):
    skill_root = tmp_path / "claude-flow"
    _write_skill(
        skill_root,
        """---
name: claude-flow
description: Use when testing metadata validation.
version: 1.0.0
metadata:
  hermes:
    tags: [coding]
    related_skills: []
---
""",
    )

    result = lint_skill_metadata(
        skill_root=skill_root,
        workspace_root=tmp_path,
    )

    assert result["ok"] is False
    assert any("body must not be empty" in error for error in result["errors"])

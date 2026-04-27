import json
import subprocess
from pathlib import Path

from resolve_review_base import resolve_review_base


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _commit(repo: Path, filename: str, content: str, message: str) -> str:
    path = repo / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    _git(repo, "add", filename)
    _git(repo, "commit", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Codex Test")
    _git(repo, "config", "user.email", "codex@example.com")
    _commit(repo, "README.md", "base\n", "base")
    _git(repo, "checkout", "-b", "feature/test-review-base")
    return repo


def test_resolve_review_base_prefers_merge_base(tmp_path: Path):
    repo = _init_repo(tmp_path)
    expected_base = _git(repo, "rev-parse", "main")
    _commit(repo, "feature.txt", "work\n", "feature work")

    result = resolve_review_base(repo)

    assert result["source"] == "merge-base"
    assert result["base_ref"] == "main"
    assert result["review_base_sha"] == expected_base


def test_resolve_review_base_prefers_workflow_state_when_valid(tmp_path: Path):
    repo = _init_repo(tmp_path)
    base_sha = _commit(repo, "feature.txt", "work\n", "feature work")
    _commit(repo, "feature-2.txt", "more\n", "feature work 2")

    state_dir = repo / ".claude"
    state_dir.mkdir()
    (state_dir / "workflow-state.json").write_text(
        json.dumps({"review_base_sha": base_sha})
    )

    result = resolve_review_base(repo)

    assert result["source"] == "workflow-state"
    assert result["review_base_sha"] == base_sha

"""Tests for the compact repository outline helper."""

import subprocess
import sys
from pathlib import Path


def test_generate_repo_outline_emits_signatures_without_bodies(tmp_path):
    """Outline output includes signatures while omitting implementation bodies."""
    src = tmp_path / "app" / "services" / "tenant.py"
    src.parent.mkdir(parents=True)
    src.write_text(
        "class TenantService:\n"
        "    def create(self, name: str) -> str:\n"
        "        secret = 'body should not appear'\n"
        "        return name\n"
        "async def fetch_tenant(tenant_id: int) -> dict:\n"
        "    return {}\n"
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/generate_repo_outline.py",
            str(src.parent),
            "--max-depth",
            "2",
        ],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "tenant.py" in result.stdout
    assert "class TenantService" in result.stdout
    assert "def create(self, name: str) -> str" in result.stdout
    assert "async def fetch_tenant(tenant_id: int) -> dict" in result.stdout
    assert "body should not appear" not in result.stdout


def test_generate_repo_outline_respects_max_depth(tmp_path):
    """Files deeper than max depth are skipped deterministically."""
    shallow = tmp_path / "app" / "visible.py"
    deep = tmp_path / "app" / "nested" / "hidden.py"
    deep.parent.mkdir(parents=True)
    shallow.write_text("def visible() -> None:\n    pass\n")
    deep.write_text("def hidden() -> None:\n    pass\n")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/generate_repo_outline.py",
            str(tmp_path / "app"),
            "--max-depth",
            "1",
        ],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "visible.py" in result.stdout
    assert "hidden.py" not in result.stdout

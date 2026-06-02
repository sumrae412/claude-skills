"""CLI surface tests for ``discover.py``.

The ``__main__`` block parses argparse args + calls ``discover()`` + prints
a summary. Tests cover argparse wiring; the discover() pipeline itself is
exercised in ``test_discover_e2e.py``.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "discover.py"
REPO_ROOT = SCRIPT.parent.parent  # off-market/


def test_cli_help_runs_without_crash():
    """`--help` exits 0 and lists the expected flags."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    out = result.stdout
    # All four documented surfaces must appear.
    assert "county" in out
    assert "--criteria" in out
    assert "--no-cache" in out
    assert "--output-dir" in out


def test_cli_unknown_county_exits_nonzero():
    """Unknown county should surface as a non-zero exit, not a stack trace."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "mars_xx"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    # Either argparse choices or the registry KeyError — both acceptable.
    combined = (result.stdout + result.stderr).lower()
    assert "county" in combined or "mars_xx" in combined

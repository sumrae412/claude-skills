import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parent / "verify_plan.py"


def test_verify_plan_accepts_stdin(tmp_path: Path):
    plan_text = """
- Modify: `app/services/example.py`
- Test: `tests/test_example.py`
"""
    (tmp_path / "app" / "services").mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    (tmp_path / "app" / "services" / "example.py").write_text("def run():\n    return True\n")
    (tmp_path / "tests" / "test_example.py").write_text("def test_run():\n    assert True\n")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "-", "--project-root", str(tmp_path), "--json"],
        input=plan_text,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["plan_file"] == "-"
    assert payload["summary"]["missing"] == 0

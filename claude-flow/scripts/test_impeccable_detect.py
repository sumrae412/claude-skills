import json
import os
import subprocess
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


def test_impeccable_detect_forced_skip_outputs_json(tmp_path):
    env = os.environ.copy()
    env["IMPECCABLE_FORCE_UNAVAILABLE"] = "1"

    result = subprocess.run(
        ["bash", "scripts/impeccable_detect.sh", "--json", str(tmp_path)],
        cwd=SKILL_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["reviewer"] == "impeccable-detector"
    assert payload["skipped"] is True
    assert payload["findings"] == []

#!/usr/bin/env bash

set -uo pipefail

reviewer="impeccable-detector"
python_bin="python3"

if ! command -v "$python_bin" >/dev/null 2>&1; then
  python_bin="python"
fi

json_envelope() {
  local skipped="$1"
  local reason="$2"

  "$python_bin" - "$reviewer" "$skipped" "$reason" <<'PY'
import json
import sys

reviewer, skipped, reason = sys.argv[1:4]
print(json.dumps({
    "reviewer": reviewer,
    "findings": [],
    "skipped": skipped == "true",
    "reason": reason,
}, separators=(",", ":")))
PY
}

normalize_output() {
  local stdout_file="$1"

  "$python_bin" - "$reviewer" "$stdout_file" <<'PY'
import json
import sys
from pathlib import Path

reviewer = sys.argv[1]
stdout = Path(sys.argv[2]).read_text()
stripped = stdout.strip()
envelope = {
    "reviewer": reviewer,
    "findings": [],
    "skipped": False,
    "reason": "",
}

if not stripped:
    print(json.dumps(envelope, separators=(",", ":")))
    sys.exit(0)

try:
    payload = json.loads(stripped)
except json.JSONDecodeError:
    envelope["findings"] = [{"raw": stdout}]
    print(json.dumps(envelope, separators=(",", ":")))
    sys.exit(0)

if (
    isinstance(payload, dict)
    and payload.get("reviewer") == reviewer
    and isinstance(payload.get("findings"), list)
):
    payload.setdefault("skipped", False)
    payload.setdefault("reason", "")
    print(json.dumps(payload, separators=(",", ":")))
else:
    envelope["findings"] = [{"raw": payload}]
    print(json.dumps(envelope, separators=(",", ":")))
PY
}

if [[ "${IMPECCABLE_FORCE_UNAVAILABLE:-}" == "1" ]]; then
  json_envelope "true" "impeccable forced unavailable"
  exit 0
fi

if ! command -v npx >/dev/null 2>&1; then
  json_envelope "true" "npx not available"
  exit 0
fi

stdout_file="$(mktemp)"
stderr_file="$(mktemp)"
trap 'rm -f "$stdout_file" "$stderr_file"' EXIT

npx --yes impeccable detect --fast --json "$@" \
  >"$stdout_file" 2>"$stderr_file"
status=$?

if [[ "$status" == "0" || "$status" == "2" ]]; then
  normalize_output "$stdout_file"
  exit 0
fi

reason="$(tr '\n' ' ' <"$stderr_file" | sed 's/[[:space:]]*$//')"
if [[ -z "$reason" ]]; then
  reason="impeccable exited with status $status"
fi

json_envelope "true" "$reason"
exit 0

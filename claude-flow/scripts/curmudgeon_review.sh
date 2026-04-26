#!/bin/zsh

set -euo pipefail

reviewer="curmudgeon-review"

skip() {
  printf '{"reviewer":"%s","findings":[],"skipped":true,"reason":"%s"}\n' \
    "$reviewer" "$1"
}

if [[ $# -lt 1 || ! -f "$1" ]]; then
  skip "diff file not found"
  exit 0
fi

if ! command -v codex >/dev/null 2>&1; then
  skip "codex CLI not installed"
  exit 0
fi

skip "curmudgeon review runner not configured in this install"

#!/bin/bash
# core_gate.sh — deterministic production-readiness-check "core" gate.
#
# Canonical, single source of truth for the C1 / C3 / C5 core checks defined
# in production-readiness-check/references/checks.md. Both claude-flow Phase 6
# step 3b and Henry's prc-merge-gate.sh PreToolUse hook call THIS script —
# do not duplicate the grep patterns anywhere else.
#
# INPUT (exactly one of):
#   <diff on stdin>            e.g. `git diff origin/main...HEAD | core_gate.sh`
#   --range <git-range>        e.g. `core_gate.sh --range origin/main...HEAD`
#                               (runs `git diff <range>` in the current directory,
#                               which must be inside a git work tree)
#   --diff-file <path>         e.g. `core_gate.sh --diff-file /tmp/review.diff`
#
# CHECKS (against added lines, `^+`, only):
#   C1 — hardcoded secrets (generic credential assignments + known-format
#        tokens). BLOCKING. Secret VALUES are never printed — pattern name
#        and file:line only.
#   C5 — unsafe dynamic execution (eval/exec/new Function/os.system/
#        subprocess shell=True/child_process). BLOCKING when the call's
#        argument is not a pure string literal (i.e. it's interpolated).
#        A literal-only argument is downgraded to a nit (WARN, non-blocking).
#   C3 — new endpoint added in a file with no added logging call in the
#        same file. WARN only — never affects exit code.
#
# OUTPUT: findings to stdout, one per line:
#   [FAIL] C1 <pattern-name> — <file>:<line>
#   [WARN] C5-nit <pattern-name> (literal-only) — <file>:<line>
#   [WARN] C3 endpoint-without-logging — <file>:<line>
#
# EXIT CODES:
#   0 — no blocking (C1/C5) findings
#   1 — one or more blocking findings
#   2 — usage / input error
#
# Bash 3.2 safe (macOS default): no associative arrays, no mapfile, no
# grep -P. Diff parsing itself is delegated to python3 (present on macOS
# and in CI) for reliable file:line tracking and regex matching — this
# wrapper script's own control flow stays Bash-3.2-compatible.

set -u

usage() {
  echo "usage: core_gate.sh [--range <git-range> | --diff-file <path>]  (or pipe a diff on stdin)" >&2
  exit 2
}

MODE="stdin"
ARG=""

if [ "$#" -gt 0 ]; then
  case "$1" in
    --range)
      [ "$#" -ge 2 ] || usage
      MODE="range"
      ARG="$2"
      ;;
    --diff-file)
      [ "$#" -ge 2 ] || usage
      MODE="file"
      ARG="$2"
      ;;
    -h|--help)
      usage
      ;;
    *)
      usage
      ;;
  esac
fi

PY3="$(command -v python3 2>/dev/null || true)"
if [ -z "$PY3" ]; then
  echo "core_gate.sh: python3 not found on PATH" >&2
  exit 2
fi

get_diff() {
  case "$MODE" in
    stdin)
      cat
      ;;
    range)
      git diff "$ARG" 2>/dev/null
      ;;
    file)
      if [ ! -f "$ARG" ]; then
        echo "core_gate.sh: diff file not found: $ARG" >&2
        return 1
      fi
      cat "$ARG"
      ;;
  esac
}

DIFF_TEXT="$(get_diff)"
GET_STATUS=$?
if [ "$GET_STATUS" -ne 0 ]; then
  exit 2
fi

if [ -z "$DIFF_TEXT" ]; then
  # No diff content is not an error — nothing to check, nothing blocking.
  exit 0
fi

PYSCRIPT="$(mktemp "${TMPDIR:-/tmp}/core_gate_py.XXXXXX")"
trap 'rm -f "$PYSCRIPT"' EXIT

cat > "$PYSCRIPT" <<'PYEOF'
import re
import sys

diff_text = sys.stdin.read()

# --- C1: hardcoded secrets ------------------------------------------------
C1_PATTERNS = [
    ("generic-credential-assignment",
     re.compile(r"(?i)(api_key|api_secret|password|secret_key|private_key|token)\s*=\s*['\"][^'\"]{8,}")),
    ("known-format-token",
     re.compile(r"AKIA[0-9A-Z]{16}|sk-[a-zA-Z0-9\-]{20,}|pk_live_|ghp_[a-zA-Z0-9]{36}|glpat-[a-zA-Z0-9\-]{20}")),
]

# --- C5: unsafe dynamic execution ----------------------------------------
C5_PATTERNS = [
    ("eval", re.compile(r"\beval\(")),
    ("exec", re.compile(r"\bexec\(")),
    ("new-Function", re.compile(r"\bnew Function\(")),
    ("os.system", re.compile(r"\bos\.system\(")),
    ("subprocess-shell-true", re.compile(r"\bsubprocess\.[A-Za-z]+\([^)]*shell\s*=\s*True")),
    ("child_process", re.compile(r"\bchild_process\b")),
]

# Argument is a pure string literal -> nit, not a FAIL.
LITERAL_ONLY = re.compile(r'''^['"][^'"]*['"]\s*\)?\s*[;,]?\s*$''')

# --- C3: endpoint-without-logging (WARN only) -----------------------------
ENDPOINT_PATTERN = re.compile(
    r"^\+.*(\.route|\.get|\.post|\.put|\.patch|\.delete|@app\.|@router\.|app\.(use|all))\b"
)
LOGGING_PATTERN = re.compile(
    r"(logger\.|logging\.|console\.log|audit_log|log\.info|log\.warn|log\.error)"
)

findings = []
blocking = False

current_file = None
new_lineno = None

# Track, per file, whether any ADDED line in the diff matched the logging
# pattern and whether any ADDED line matched the endpoint pattern, plus the
# first endpoint line's location for the WARN message.
file_has_added_logging = {}
file_endpoint_hits = {}  # file -> list of (lineno, matched_text)

lines = diff_text.split("\n")

diff_git_re = re.compile(r"^diff --git a/(.+?) b/(.+)$")
plus_file_re = re.compile(r"^\+\+\+ b/(.+)$")
hunk_re = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")

for raw in lines:
    m = diff_git_re.match(raw)
    if m:
        current_file = m.group(2)
        new_lineno = None
        continue

    m = plus_file_re.match(raw)
    if m:
        current_file = m.group(1)
        new_lineno = None
        continue

    m = hunk_re.match(raw)
    if m:
        new_lineno = int(m.group(1))
        continue

    if raw.startswith("+++") or raw.startswith("---"):
        continue

    if new_lineno is None:
        continue

    if raw.startswith("+"):
        content = raw[1:]
        lineno = new_lineno
        new_lineno += 1

        fname = current_file or "<unknown>"

        # C1
        for pname, pat in C1_PATTERNS:
            if pat.search(content):
                findings.append("[FAIL] C1 %s — %s:%d" % (pname, fname, lineno))
                blocking = True

        # C5
        for pname, pat in C5_PATTERNS:
            match = pat.search(content)
            if not match:
                continue
            arg_text = content[match.end():].strip()
            # Trim a single trailing ')' set / statement terminator for the
            # literal check — best-effort on a single grep line.
            is_literal = bool(LITERAL_ONLY.match(arg_text)) if arg_text else False
            if is_literal:
                findings.append(
                    "[WARN] C5-nit %s (literal-only) — %s:%d" % (pname, fname, lineno)
                )
            else:
                findings.append("[FAIL] C5 %s — %s:%d" % (pname, fname, lineno))
                blocking = True

        # C3 bookkeeping
        if LOGGING_PATTERN.search(content):
            file_has_added_logging[fname] = True
        if ENDPOINT_PATTERN.match(raw):
            file_endpoint_hits.setdefault(fname, []).append(lineno)

    elif raw.startswith("-"):
        continue
    else:
        new_lineno += 1

# C3: emit WARN for any file with an added endpoint but no added logging call.
for fname, hits in file_endpoint_hits.items():
    if file_has_added_logging.get(fname):
        continue
    for lineno in hits:
        findings.append(
            "[WARN] C3 endpoint-without-logging — %s:%d" % (fname, lineno)
        )

for f in findings:
    print(f)

sys.exit(1 if blocking else 0)
PYEOF

printf '%s' "$DIFF_TEXT" | "$PY3" "$PYSCRIPT"
STATUS=$?
rm -f "$PYSCRIPT"
trap - EXIT
exit $STATUS

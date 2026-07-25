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
#        and file:line only. Scans ALL files, including tests (a real leaked
#        credential in a test IS a leak). A matched value containing a known
#        placeholder token (EXAMPLE, DUMMY, FAKE, PLACEHOLDER, CHANGEME,
#        YOUR_, XXXX, TEST_KEY, SAMPLE, NOTREAL — case-insensitive) is
#        downgraded to a WARN nit, non-blocking.
#   C5 — unsafe dynamic execution (eval/exec/new Function/os.system/
#        subprocess shell=True/child_process). BLOCKING when the call's
#        argument is not a pure string literal (i.e. it's interpolated).
#        A literal-only argument is downgraded to a nit (WARN, non-blocking).
#        Skipped entirely for added lines in files whose PATH marks them as
#        tests (basename test_*/test-*/*_test.*/*-test.*/*.test.*/*.spec.*/
#        conftest.py, or any path segment equal to tests/test/__tests__/
#        fixtures — both snake_case and kebab-case naming conventions) — a test
#        FOR an exec/secret detector inherently contains the patterns it
#        detects. Matched on path segments/basename, not substring, so a
#        prod file like `latest_config.py` is never accidentally exempted.
#   C3 — new endpoint added in a file with no added logging call in the
#        same file. WARN only — never affects exit code.
#
# SUPPRESSION MARKER: any added line containing the token `core-gate-allow`
# (case-insensitive, anywhere in the line) is exempt from C1 and C5 checks —
# the auditable per-line escape hatch for a legitimate occurrence in
# production code. Emits an informational [SKIP] note; does not affect exit
# code.
#
# OUTPUT: findings to stdout, one per line:
#   [FAIL] C1 <pattern-name> — <file>:<line>
#   [WARN] C1-nit <pattern-name> (placeholder) — <file>:<line>
#   [WARN] C5-nit <pattern-name> (literal-only) — <file>:<line>
#   [WARN] C3 endpoint-without-logging — <file>:<line>
#   [SKIP] suppressed by core-gate-allow — <file>:<line>
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

# Known dummy/placeholder tokens -> C1 match downgraded to WARN, not FAIL.
PLACEHOLDER_RE = re.compile(
    r"(?i)(EXAMPLE|DUMMY|FAKE|PLACEHOLDER|CHANGEME|YOUR_|XXXX|TEST_KEY|SAMPLE|NOTREAL)"
)

# Inline suppression marker: any added line containing this token (anywhere,
# case-insensitive) is exempt from C1 and C5 for that line.
SUPPRESS_MARKER_RE = re.compile(r"(?i)core-gate-allow")

# --- C5 path scoping: skip test files ------------------------------------
TEST_BASENAME_RES = [
    re.compile(r"(?i)^test[_-]"),           # test_foo.sh, test-foo.sh (kebab-case hook naming)
    re.compile(r"(?i)[_-]test\.[^./]+$"),   # foo_test.py, foo-test.sh
    re.compile(r"(?i)\.test\.[^./]+$"),     # foo.test.js
    re.compile(r"(?i)\.spec\.[^./]+$"),     # foo.spec.ts
    re.compile(r"(?i)^conftest\.py$"),
]
TEST_DIR_SEGMENTS = set(["tests", "test", "__tests__", "fixtures"])


def is_test_path(fname):
    # Match on path SEGMENTS / basename only — never a bare substring, so a
    # production file named e.g. `latest_config.py` is not exempted.
    parts = [p for p in fname.split("/") if p]
    if not parts:
        return False
    basename = parts[-1]
    dirs = parts[:-1]
    for seg in dirs:
        if seg in TEST_DIR_SEGMENTS:
            return True
    for pat in TEST_BASENAME_RES:
        if pat.search(basename):
            return True
    return False

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

        # Inline suppression marker — exempt this line from C1 and C5.
        if SUPPRESS_MARKER_RE.search(content):
            findings.append(
                "[SKIP] suppressed by core-gate-allow — %s:%d" % (fname, lineno)
            )
        else:
            # C1 — scans ALL files (including tests); placeholder values downgrade.
            for pname, pat in C1_PATTERNS:
                match = pat.search(content)
                if not match:
                    continue
                if PLACEHOLDER_RE.search(content):
                    findings.append(
                        "[WARN] C1-nit %s (placeholder) — %s:%d" % (pname, fname, lineno)
                    )
                else:
                    findings.append("[FAIL] C1 %s — %s:%d" % (pname, fname, lineno))
                    blocking = True

            # C5 — skipped entirely for test-path files.
            if not is_test_path(fname):
                for pname, pat in C5_PATTERNS:
                    match = pat.search(content)
                    if not match:
                        continue
                    arg_text = content[match.end():].strip()
                    # Trim a single trailing ')' set / statement terminator for
                    # the literal check — best-effort on a single grep line.
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

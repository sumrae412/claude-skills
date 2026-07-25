#!/bin/bash
# Test harness for core_gate.sh
#
# Hermetic — no network, no external repo state required (feeds diffs on
# stdin). Bash 3.2 safe (macOS default).

GATE="$(cd "$(dirname "$0")" && pwd)/core_gate.sh"
PASS=0
FAIL=0

run_case() {
    local name="$1"
    local diff="$2"
    local expect_code="$3"

    actual_code=0
    output="$(printf '%s' "$diff" | bash "$GATE" 2>&1)" || actual_code=$?

    if [ "$actual_code" -eq "$expect_code" ]; then
        echo "PASS: $name (exit=$actual_code, expected=$expect_code)"
        PASS=$((PASS+1))
    else
        echo "FAIL: $name (exit=$actual_code, expected=$expect_code)"
        echo "  output: $output"
        FAIL=$((FAIL+1))
    fi
}

# --- Case 1: seeded AWS key -> exit 1 --------------------------------------
DIFF_1='diff --git a/config.py b/config.py
--- a/config.py
+++ b/config.py
@@ -1,0 +2,1 @@
+aws_key = "AKIAABCDEFGHIJKLMNOP"
'
run_case "seeded AWS key -> blocking FAIL" "$DIFF_1" 1

# --- Case 2: seeded GitHub token -> exit 1 ---------------------------------
DIFF_2='diff --git a/config.py b/config.py
--- a/config.py
+++ b/config.py
@@ -1,0 +2,1 @@
+token = "ghp_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
'
run_case "seeded GitHub token -> blocking FAIL" "$DIFF_2" 1

# --- Case 3: seeded generic secret -> exit 1 -------------------------------
DIFF_3='diff --git a/settings.py b/settings.py
--- a/settings.py
+++ b/settings.py
@@ -1,0 +2,1 @@
+API_SECRET = "supersecretvalue123"
'
run_case "seeded generic secret -> blocking FAIL" "$DIFF_3" 1

# --- Case 4: eval(userInput) — interpolated -> exit 1 ----------------------
DIFF_4='diff --git a/app.js b/app.js
--- a/app.js
+++ b/app.js
@@ -1,0 +2,1 @@
+eval(userInput)
'
run_case "eval(userInput) interpolated -> blocking FAIL" "$DIFF_4" 1

# --- Case 5: eval("literal") — no interpolation -> exit 0 ------------------
DIFF_5='diff --git a/app.js b/app.js
--- a/app.js
+++ b/app.js
@@ -1,0 +2,1 @@
+eval("literal")
'
run_case "eval(\"literal\") no interpolation -> exit 0 (nit only)" "$DIFF_5" 0

# --- Case 6: clean diff -> exit 0 -------------------------------------------
DIFF_6='diff --git a/app.js b/app.js
--- a/app.js
+++ b/app.js
@@ -1,0 +2,1 @@
+console.log("hello world")
'
run_case "clean diff -> exit 0" "$DIFF_6" 0

# --- Case 7: unlogged new endpoint -> exit 0 + WARN printed -----------------
DIFF_7='diff --git a/routes.py b/routes.py
--- a/routes.py
+++ b/routes.py
@@ -1,0 +2,1 @@
+@app.route("/widgets")
'
output_7="$(printf '%s' "$DIFF_7" | bash "$GATE" 2>&1)"
code_7=$?
if [ "$code_7" -eq 0 ] && printf '%s' "$output_7" | grep -q '\[WARN\] C3 endpoint-without-logging'; then
    echo "PASS: unlogged endpoint -> exit 0 + C3 WARN printed"
    PASS=$((PASS+1))
else
    echo "FAIL: unlogged endpoint -> exit 0 + C3 WARN printed (exit=$code_7)"
    echo "  output: $output_7"
    FAIL=$((FAIL+1))
fi

# --- Case 7b: logged new endpoint -> no C3 WARN -----------------------------
DIFF_7B='diff --git a/routes.py b/routes.py
--- a/routes.py
+++ b/routes.py
@@ -1,0 +2,2 @@
+@app.route("/widgets")
+logger.info("widgets endpoint hit")
'
output_7b="$(printf '%s' "$DIFF_7B" | bash "$GATE" 2>&1)"
code_7b=$?
if [ "$code_7b" -eq 0 ] && ! printf '%s' "$output_7b" | grep -q 'C3'; then
    echo "PASS: logged endpoint -> no C3 WARN"
    PASS=$((PASS+1))
else
    echo "FAIL: logged endpoint -> no C3 WARN (exit=$code_7b)"
    echo "  output: $output_7b"
    FAIL=$((FAIL+1))
fi

# --- Case 8: secret VALUE must never appear in output -----------------------
SECRET_VALUE="supersecretvalue123"
DIFF_8='diff --git a/settings.py b/settings.py
--- a/settings.py
+++ b/settings.py
@@ -1,0 +2,1 @@
+API_SECRET = "supersecretvalue123"
'
output_8="$(printf '%s' "$DIFF_8" | bash "$GATE" 2>&1)"
if printf '%s' "$output_8" | grep -qF "$SECRET_VALUE"; then
    echo "FAIL: secret value leaked in output"
    echo "  output: $output_8"
    FAIL=$((FAIL+1))
else
    echo "PASS: secret value masked in output"
    PASS=$((PASS+1))
fi

# --- Case 9: --range flag on a real git repo (this repo checkout) ----------
if git -C "$(dirname "$GATE")" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    # No-op range (HEAD..HEAD) — should be empty diff, exit 0.
    code_9=0
    (cd "$(dirname "$GATE")" && bash "$GATE" --range HEAD..HEAD >/dev/null 2>&1) || code_9=$?
    run_case_result="PASS"
    if [ "$code_9" -ne 0 ]; then
        run_case_result="FAIL"
    fi
    echo "$run_case_result: --range HEAD..HEAD (empty) -> exit 0 (exit=$code_9)"
    if [ "$run_case_result" = "PASS" ]; then PASS=$((PASS+1)); else FAIL=$((FAIL+1)); fi
else
    echo "SKIP: --range case (not inside a git work tree)"
fi

# --- Case 10: --diff-file flag ----------------------------------------------
TMPFILE="$(mktemp "${TMPDIR:-/tmp}/core_gate_test.XXXXXX")"
printf '%s' "$DIFF_4" > "$TMPFILE"
code_10=0
bash "$GATE" --diff-file "$TMPFILE" >/dev/null 2>&1 || code_10=$?
rm -f "$TMPFILE"
if [ "$code_10" -eq 1 ]; then
    echo "PASS: --diff-file with interpolated eval -> exit 1"
    PASS=$((PASS+1))
else
    echo "FAIL: --diff-file with interpolated eval -> exit 1 (exit=$code_10)"
    FAIL=$((FAIL+1))
fi

# --- Case 11: missing diff-file -> exit 2 (usage/error) --------------------
code_11=0
bash "$GATE" --diff-file /nonexistent/path/xyz.diff >/dev/null 2>&1 || code_11=$?
run_case_dummy="n/a"
if [ "$code_11" -eq 2 ]; then
    echo "PASS: missing --diff-file path -> exit 2"
    PASS=$((PASS+1))
else
    echo "FAIL: missing --diff-file path -> exit 2 (exit=$code_11)"
    FAIL=$((FAIL+1))
fi

echo ""
echo "=== RESULTS: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ]

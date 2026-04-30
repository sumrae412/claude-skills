# Monitor tool patterns for claude-flow

The `Monitor` tool spawns a background process and streams stdout lines as notifications, without blocking the agent loop. Each line is a conversation event; the agent keeps working in parallel. Use it instead of polling via Bash whenever you need **one notification per occurrence** of an event.

## Decision rule

| Need | Tool | Shape |
|------|------|-------|
| One notification when a condition is met | `Bash` with `run_in_background: true` | `until <check>; do sleep 0.5; done` — exits when condition is true |
| One notification per occurrence, indefinite | `Monitor` (`persistent: true`) | `tail -F log \| grep --line-buffered ...` |
| One notification per occurrence, until natural end | `Monitor` (default timeout) | poll loop emitting one line per terminal state, exit on completion |
| Bulk log scan / count | one-shot `Bash` | `grep -c PATTERN log` |

**Anti-pattern:** unbounded `tail -f` for a single event. The watch stays armed until timeout even after the event fires. Use Bash `run_in_background` with `until` for that.

## Where Monitor fits in claude-flow

### Phase 5 — Implementation

- **Long-running test or build watches.** When a TDD red→green cycle takes 30s+, run the test in a background loop and let the executor draft the next step in parallel. Filter for `PASSED|FAILED|ERROR|Traceback`.
- **Dev server tail during UI verification.** Pair `preview_start` (or `uvicorn ... > /tmp/server.log 2>&1 &` via Bash background) with a `Monitor` over `tail -F /tmp/server.log | grep -E --line-buffered "ERROR|Traceback|500 |Internal Server Error"`. Catches regressions in adjacent flows while you verify the change you made.
- **Celery / background worker watches.** When the change touches a worker path, tail worker output for `Task.*FAILED|retry|MaxRetriesExceededError` for the rest of the implementation phase.

### Phase 6 — Quality + Finish

- **PR check progression watch.** Replace the polling pattern in `/ship` with a Monitor that emits one line per terminal check and exits when all settle:
  ```bash
  prev=""
  while true; do
    s=$(gh pr checks <PR> --json name,bucket)
    cur=$(jq -r '.[] | select(.bucket!="pending") | "\(.name): \(.bucket)"' <<<"$s" | sort)
    comm -13 <(echo "$prev") <(echo "$cur")
    prev=$cur
    jq -e 'all(.bucket!="pending")' <<<"$s" >/dev/null && break
    sleep 30
  done
  ```
- **Production deploy soak.** After merge, persistent Monitor on Railway/Bedrock/Vertex/Cloud Run logs filtered for `ERROR|Traceback|5\d\d ` for the post-deploy soak window. Lets the agent catch crashloops or regression spikes without sleeping the loop.
- **CodeRabbit review polling.** When `/review-pr` is dispatched as a background agent, monitor the PR for `coderabbitai` comments and surface them as they arrive instead of polling.

## Filter discipline (load-bearing)

1. **Silence is not success.** A monitor that greps only the happy-path marker stays silent through a crashloop. Always include failure signatures: `ERROR|Traceback|Killed|OOM|FAILED|assert|5\d\d `. If you can't enumerate the failure modes, broaden the alternation rather than narrow it.
2. **Always `--line-buffered`** on `grep` (or equivalent for `awk`/`sed`). Pipe buffering can delay events by minutes.
3. **Merge stderr** with `2>&1` on commands you launch directly — only stdout becomes events. Doesn't apply to `tail -F log` on an existing file.
4. **Selective filter.** Every stdout line is a conversation message; over-emitting monitors are auto-stopped. Filter for "lines you'd act on," not "all log output."
5. **Specific `description`.** Appears in every notification. Prefer "Railway prod 5xx errors" over "watching logs."

## Composition with existing claude-flow patterns

- **Memory injection (`references/memory-injection.md`).** When a project's MEMORY.md flags a silent-zero / silent-failure class (e.g. CourierFlow `counts_service` try/except per domain, `selectinload` synonym mismatch), the Phase 5/6 Monitor filter must include the failure signature, not just the success marker. Inject this constraint into Monitor recipes the same way memory gotchas are injected into subagent prompts.
- **Subagent dispatch.** Monitor is a main-thread tool — subagents cannot register their own monitors that survive past their turn. When a long-running watch is needed, the orchestrator (executor) registers it and subagents read the monitor output via the conversation.
- **External Systems Access Policy (SKILL.md).** Monitor is a delivery channel, not a data source. It composes with the MCP/CLI/HTTP preference order: prefer MCP-streamed events when available (e.g. Railway MCP for prod logs), fall back to CLI streams (`gh pr checks`, `kubectl logs -f`, `railway logs`), only HTTP polling as last resort.

## Anti-patterns

| Pattern | Why it fails |
|---------|--------------|
| `tail -f log \| grep -m 1 PATTERN` for one-shot wait | If log goes quiet after match, `tail` never receives SIGPIPE and pipeline hangs |
| Raw `tail -f log` with no filter | Floods conversation with every line; auto-stopped |
| `grep "SUCCESS"` only | Silent during crash, hang, OOM — silence looks identical to "still running" |
| Polling without `\|\| true` on flaky network calls | One transient `curl` failure kills the monitor for the rest of the session |
| Local poll interval < 0.5s, remote poll < 30s | Local: pegs CPU. Remote: rate-limit ban. |

## Quick reference

```python
# Persistent log watch (session-length)
Monitor(
    description="Railway prod 5xx + tracebacks",
    persistent=True,
    command='railway logs --service <svc> 2>&1 | grep -E --line-buffered "ERROR|Traceback|5\\d\\d "',
)

# Scoped watch with natural exit (PR checks)
Monitor(
    description="PR #1234 checks until all settle",
    timeout_ms=1800000,  # 30 min
    persistent=False,
    command='<the gh pr checks loop above>',
)

# One-shot wait (NOT Monitor — Bash background)
Bash(
    command='until curl -sf http://localhost:8000/health >/dev/null; do sleep 0.5; done',
    run_in_background=True,
)
```

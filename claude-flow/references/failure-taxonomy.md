# Workflow Failure Taxonomy

Tag failures to behavioral categories when they occur. These tags feed into
the Workflow Retrospective (Phase 6), session-learnings, and run-manifest
event-log analysis.

| Tag | Description | Example |
|-----|-------------|---------|
| `exploration-gap` | Phase 2 missed a key file, pattern, or integration point | Didn't find the existing validation util → duplicated logic |
| `architecture-miss` | Phase 4 options didn't account for a constraint | Neither option handled the existing caching layer |
| `clarification-skip` | Ambiguity wasn't surfaced in Phase 3 | Edge case discovered during implementation that should have been asked |
| `plan-gap` | Plan missing a step or misordering dependencies | Migration step listed after the code that depends on it |
| `plan-verification-miss` | Plan referenced stale file paths, renamed functions, or changed APIs that Phase 4c should have caught | Plan says "modify `get_user()` in `user_service.py`" but the function was renamed to `fetch_user()` |
| `review-escape` | Bug/issue shipped past Phase 6 review tiers | Silent failure not caught by any reviewer tier |
| `integration-failure` | Code works in isolation but breaks at integration points | Service call succeeds but caller doesn't handle new response shape |
| `regression` | Change broke previously working behavior | New route handler shadowed existing route |
| `guard-regression` | Fix for target test broke adjacent tests (caught by step 3b guard) | Fixed assertion in test_create but broke test_update in same module |
| `mutation-gate-exceeded` | New test(s) did not kill any mutation after 2 strengthen cycles (step 3c mutation gate) | Test called target but only asserted `True`; after 2 rewrites still non-discriminating |
| `tool-selection` | Wrong tool or pattern chosen for the job | Used raw SQL when the ORM had a built-in method |
| `over-engineering` | Built more than was needed | Added abstraction layer for a one-time operation |
| `under-specification` | Requirements were technically met but user intent was missed | Implemented delete but user wanted soft-delete |

## Tool and Subagent Error Classes

Use these classes for `tool_error` and `subagent_error` events in the run
manifest event log. The class goes in `payload.error_class`; the workflow
failure tag goes in `payload.failure_tag` when the error reflects a workflow
mistake.

| Error class | Expected? | When to use | Failure tag |
|-------------|-----------|-------------|-------------|
| `unknown-tool-error` | No | A tool fails in a way not covered by the classes below. Treat every occurrence as a workflow or harness bug until classified. | `tool-selection` unless a sharper tag applies |
| `invalid-arguments` | Yes | The executor or subagent called the right tool with malformed, incomplete, or unsupported arguments. | `tool-selection` |
| `unexpected-environment` | Yes | The call was valid, but the local workspace, missing binary, stale file path, permissions, or repository state contradicted the expected environment. | `plan-verification-miss` or `exploration-gap` |
| `provider-error` | Yes | An external provider, MCP server, hosted tool, or API was unavailable, rate-limited, or returned a transient 5xx-style failure. | Leave unset unless the workflow mishandled recovery |
| `timeout` | Yes | A tool or subagent exceeded its time budget. | `tool-selection` when the query or scope was inefficient |
| `user-aborted` | Yes | The user intentionally stopped, redirected, or cancelled the work. | Leave unset |

Expected errors are still worth recording because spikes can expose a broken
prompt, stale phase instruction, or weak plan verification. Unknown errors are
bugs in the workflow surface: classify or fix them before treating them as
normal noise.

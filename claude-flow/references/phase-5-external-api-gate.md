# Phase 5 External API Gate

Load this reference only when a Phase 5 step touches an external API.

## Hard Gate

Do not write code against external APIs from memory.

If any plan step calls an external API, verify the live contract first:

- endpoints
- auth method
- request shape
- response shape
- rate limits or retry rules

## Decision Flow

```text
Plan step touches external API?
  YES -> Is there an MCP server?
           YES -> Prefer MCP introspection
                  Treat the tool surface as the current contract
                  Fall back to HTTP only if MCP does not cover the need
           NO  -> Invoke /fetch-api-docs
                  Verify docs against current version
       -> Pass the verified contract into the implementation step or subagent
  NO  -> Skip this gate
```

Why MCP first:

- better freshness
- consistent auth
- smaller token footprint than ad hoc web fetches

This gate still applies even if an integrations skill was loaded in Phase 0.

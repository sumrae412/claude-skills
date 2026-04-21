## Protocol

### Step 1: Complexity Gate (Auto-Tiered)

Assess the artifact and select tier:

```
IS_PLAN = artifact path matches docs/plans/*.md OR caller passes --type plan
IS_BUG_FIX_PLAN = IS_PLAN AND artifact describes a bug fix
IS_CODE = artifact touches app/**, tests/**, *.py, *.js, *.css, *.html (code files)
IS_NON_CODE = NOT IS_CODE (skills, docs, CLAUDE.md, MEMORY.md, process specs)
FILE_COUNT = number of files touched/proposed
HAS_SCHEMA = touches models or migrations
HAS_SECURITY = touches auth, tokens, permissions
HAS_FRONTEND = touches templates, CSS, JS
HAS_BACKEND = touches routes, services

Tier 3 (Full Debate) if:
  IS_PLAN
  OR (IS_BUG_FIX_PLAN AND (FILE_COUNT >= 3 OR cross-service))
  OR (HAS_SCHEMA AND HAS_SECURITY)
  OR (HAS_FRONTEND AND HAS_BACKEND)
  OR user says "full debate"

Tier 2 (Dual Critic) if:
  FILE_COUNT >= 3
  OR cross-cutting concerns
  OR external API integration

Tier 1 otherwise (or user says "quick review")
```

**Tier routing:**
- **Tier 1:** Skip to Step 3 (DeepSeek only, no Generator, no GPT-4o, no synthesis). Run DeepSeek Bug-Hunter with `OUT_OF_SCOPE` filtering. Output: Pass/flag list.
- **Tier 2:** Skip to Step 3 (DeepSeek + GPT-4o in parallel, no Generator). Output: Adopt/Reject/Defer per finding via Step 4.
- **Tier 3:** Full protocol — Step 2 (Generator) → Step 3 (all critics) → Step 4 (synthesis) → Step 5 (present).

Announce: "Running debate-team Tier [N] — [reason]."

### Step 2: Generate Proposal

Spawn the **Generator** (Sonnet teammate) with the task context:

```
Use Task tool:
  subagent_type: general-purpose
  model: sonnet
  name: generator
  prompt: [full task context + "Write a complete [plan/code] proposal. Save to /tmp/debate_artifact.md"]
```

Wait for Generator to complete. Read the artifact.


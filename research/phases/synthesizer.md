## Synthesizer

**Subagent type:** `general-purpose`
**Model:** `sonnet`

The synthesizer reads ALL scratchpad entries (Wave 1 + Wave 2 if applicable) and produces the research brief.

**Prompt template:**
```
Think harder about synthesizing these research findings.

Research question: [RESEARCH_QUESTION]

## All Research Findings:
[FULL SCRATCHPAD — all Wave 1 + Wave 2 entries concatenated]

Your job: Synthesize these findings into a unified research brief. For EVERY finding:
- Cross-reference across researchers — do multiple sources confirm it?
- Assign a confidence level:
  - **verified**: confirmed in code AND docs/tests, or by multiple independent researchers
  - **inferred**: reasonable conclusion from evidence, but not directly confirmed
  - **assumed**: couldn't verify; flag for defensive design
- Identify contradictions and resolve them (or flag as unresolved)
- Extract architecture-relevant constraints

Output format:

# Research Brief: [TOPIC]

## Key Findings
- [Finding] (confidence: verified|inferred|assumed) — [1-line evidence summary]
- ...

## Architecture-Relevant Constraints
- [Constraint the architect must account for]
- ...

## Open Risks
- [Assumption that couldn't be verified] (confidence: assumed)
- ...

## Sources
- [file/url/commit references organized by topic]

Be ruthless about confidence scoring. "Verified" means MULTIPLE sources confirm it. When in doubt, downgrade to "inferred" or "assumed".
```

---


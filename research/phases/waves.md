## Default Researcher Selection

| Task Category | Default Researchers |
|---|---|
| endpoint / api | Codebase Explorer, Integration Mapper, External Researcher |
| ui | Codebase Explorer, External Researcher |
| data | Codebase Explorer, History Analyst |
| integration | External Researcher, Integration Mapper, Codebase Explorer |
| refactor | Codebase Explorer, History Analyst |
| bugfix | Codebase Explorer, History Analyst, Integration Mapper |
| config | Codebase Explorer, External Researcher |
| exploration | External Researcher, Codebase Explorer |
| general | Codebase Explorer, External Researcher |

The orchestrator MAY override defaults when the specific research question clearly needs a different mix.

---

## Wave Logic

### Wave 1 — Parallel Dispatch

Dispatch all selected researchers simultaneously using the Agent tool. Each researcher gets:
- The research question
- Their specific focus area (derived from task classification)
- Memory-injection block (if in workflow context)
- The scratchpad format template

### Gap Detection (Orchestrator)

After all Wave 1 agents return, the orchestrator reads their outputs and checks:

1. **Unanswered questions:** Are there open questions from one researcher that another researcher type could answer?
2. **Uncovered areas:** Did a researcher reference a system/area that no other researcher explored?
3. **Contradictions:** Do any findings from different researchers conflict?
4. **Critical unknowns:** Is there a low-confidence finding on something critical to the research question?

**Decision:**
- If ANY gap detected → dispatch Wave 2 with 1-2 targeted researchers and specific gap-fill prompts
- If NO gaps → skip to synthesizer

### Wave 2 — Targeted Gap-Fill

Wave 2 researchers receive:
- The original research question
- ALL Wave 1 findings (full scratchpad)
- Specific gap-fill instructions: "Wave 1 found X but couldn't determine Y. Your job is to answer Y."
- The same output format as Wave 1 researchers (Findings / Open Questions / Connections sections defined in each researcher's prompt template above)

### Skip Conditions

When called from claude-flow:
- `fast` or `lite` path → skip research entirely (use current single-executor exploration)
- `full` or `complex` path → run research team

When called standalone:
- Always run (user explicitly asked for research)

---


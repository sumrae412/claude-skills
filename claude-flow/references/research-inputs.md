# Research inputs — agent infrastructure literature

Citations and concept references for future doc refactors. Not load-bearing for any current phase; review when redesigning the workflow's architecture vocabulary or considering cross-model / agent-provenance features.

---

## "Code as Agent Harness" — arXiv 2605.18747

**URL:** https://arxiv.org/abs/2605.18747
**Authors:** Ning et al. (May 2026)
**Awesome list:** https://github.com/YennNing/Awesome-Code-as-Agent-Harness-Papers
**Saved from Mem 2026-05-20.**

Survey reframing code as the operational substrate for agentic AI. Three-layer framing as candidate vocabulary if `claude-flow`'s phase-overview narrative gets refactored:

- **Harness Interface** — how code connects agents to reasoning, action, environment modeling (≈ Phases 1–4: discovery, exploration, requirements, plan)
- **Harness Mechanisms** — planning, memory, tool use, feedback-driven control (≈ Phase 5: TDD implementation)
- **Scaling Harness** — single-agent to multi-agent coordination via shared code artifacts (≈ Phase 2 Research Team Branch, Phase 6 review cascade)

Open challenges from the paper that map to potential `claude-flow` gaps: evaluation beyond task success, verification with incomplete feedback, regression-free improvement, consistent shared state across subagents.

## re_gent — version control for AI agent actions

**Repo:** https://github.com/regent-vcs/re_gent
**License:** Apache-2.0
**Saved from Mem 2026-05-20.**

Production-grade exemplar of agent-action provenance. Content-addressed storage (BLAKE3), per-session DAG for concurrent agents, inline blame annotations, full context per change. Compatible with Claude Code, Codex CLI, OpenCode.

Relevance: the operationalized form of what `verification-before-completion` enforces by discipline. If `claude-flow` ever needs structured action-log emission (e.g., for an audit-path workflow variant), this is the design reference.

## Warp Oz — multi-harness orchestration

**Source:** https://x.com/zachlloydtweets/status/2056780898675167656
**Saved from Mem 2026-05-20.**

Notable for "cross-harness Agent Memory" — persistent memory shared across model providers (Claude Code, Codex, Warp Agent). `claude-flow` is currently Claude-only; if cross-model dispatch is ever added (e.g., delegating mechanical Phase 5 work to a cheaper non-Claude model while Sonnet/Opus advise), this is the design vocabulary to use.

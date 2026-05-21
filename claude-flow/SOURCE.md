# Sources & Attribution

claude-flow is a hand-authored multi-phase build workflow. It is not a fork or
copy of any single external framework, but it borrows or distills patterns from
the following sources.

## Spec-Driven Development — GitHub spec-kit

Phase 3 (Requirements) and Phase 4 (Architecture + Plan) cover roughly the
**constitution → specify → plan → tasks → implement** surface of
[github/spec-kit](https://github.com/github/spec-kit). Two gaps from that
framework were closed in claude-skills PR #67 (squash-merged 2026-05-01,
commit `bfad6d2`):

- **Phantom-completion audit** — `executing-plans/SKILL.md` Step 4.5 +
  `phases/phase-5-implementation.md` HARD GATE before Phase 5.5. Re-parses
  `[X]` tasks against on-disk artifacts; downgrades hollow checkmarks to `[~]`
  and surfaces them.
- **Spec-references-as-context gate** — required `## References` section in
  `writing-plans` plan header; treated as a whitelist for prior-art context to
  prevent silent expansion.

Before pulling more from spec-kit (or any SDD framework), invoke `/useful-for`
against claude-flow first — most surface area is already covered.

## Mixture-of-Experts Routing

The `scripts/moe_router.py` + `references/moe-expert-configs.md` design borrows
the **Mixture of Experts** pattern from ML literature (Shazeer et al. 2017
*Outrageously Large Neural Networks*; subsequent transformer MoE work). Used
here in the lightweight sense: a router selects an expert configuration
(prompt + model + tools) per task fingerprint, rather than running every task
through a single fixed configuration. No external code lifted — pattern
attribution only.

## CodeRabbit (Tier 1 reviewer)

Phase 6 default Tier 1 reviewer is [CodeRabbit](https://www.coderabbit.ai/)
via the `coderabbit:code-reviewer` subagent. Used as an external first-pass
gate; subsequent tiers fill gaps CodeRabbit doesn't cover (project conventions,
type design, over-engineering, production readiness).

## Per-Phase Reviewer Roster

The Phase 6 reviewer roster (silent-failure-hunter, security-reviewer,
pr-test-analyzer, migration-reviewer, async-reviewer, google-api-reviewer) is
authored under the `pr-review-toolkit` plugin set. Specialist reviewers run
conditionally based on file-pattern triggers in `references/skill-triggers.md`.

## Goal-Mode (`/goal`)

The `--goal` flag wraps Claude Code's first-party
[/goal slash command](https://code.claude.com/docs/en/goal). claude-flow adds
anti-cheat clauses, phase-scoped injection rules, and manifest persistence on
top of the native command — see SKILL.md §Goal-mode auto-injection.

## Default Project Skill Menu

The default Phase 5 forced-selection menu (`courierflow-ui`, `courierflow-api`,
`courierflow-data`, `courierflow-integrations`, `courierflow-security`) is the
**CourierFlow** menu — the project this skill set was authored against. Replace
for other projects per `references/project-skill-menu.md`.

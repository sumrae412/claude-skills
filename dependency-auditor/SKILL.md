---
name: "dependency-auditor"
description: "Multi-language dependency auditor — scans package manifests (npm/pip/go/rust/ruby/maven/composer/.NET) for CVEs, license compliance, and upgrade risk. Use when auditing dependencies, reviewing supply-chain risk, gating CI on vulnerabilities, or planning upgrade sequences."
---

# Dependency Auditor

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad
exploration, repeated file reads, multi-file scans, or heavy reference
loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant
  patterns inline instead of loading extra material.

## Overview

Dependency auditing toolkit for security, license compliance, upgrade
planning, and supply-chain hygiene across multiple ecosystems.

This file is a router. Keep only the relevant audit mode in context.

## When to Use

- Auditing manifests or lockfiles for vulnerabilities
- Reviewing license compatibility or legal risk
- Planning dependency upgrades
- Reducing dependency bloat or transitive risk
- Designing dependency policy gates for CI/CD

## Load Strategy

1. Identify the primary audit objective.
2. Load only the matching phase file from `phases/`.
3. Load only the required reference material.
4. Prefer scripts for deterministic scans and reports.

Do not preload all ecosystem guidance, examples, or future roadmap
material.

## Phase Map

1. `phases/phase-1-vulnerabilities-and-supply-chain.md`
2. `phases/phase-2-license-and-compliance.md`
3. `phases/phase-3-upgrades-and-bloat.md`
4. `phases/phase-4-policy-and-ci.md`

## Reference Map

- Vulnerability method:
  `references/vulnerability_assessment_guide.md`
- License compatibility:
  `references/license_compatibility_matrix.md`
- Dependency hygiene:
  `references/dependency_management_best_practices.md`

## Script Map

- Security and inventory scan:
  `scripts/dep_scanner.py`
- License analysis:
  `scripts/license_checker.py`
- Upgrade planning:
  `scripts/upgrade_planner.py`

## Session Rules

- Start from manifests and lockfiles, not package marketing pages.
- Distinguish direct from transitive risk.
- Separate exploitable vulnerabilities from stale-but-benign versions.
- Tie license findings to actual distribution or deployment context.

## Deliverables

Produce only what the user needs:

- vulnerability report
- license risk report
- upgrade plan
- dependency cleanup list
- CI / policy gate design

## Guardrails

- Do not recommend broad major-version upgrades without rollback/testing
  planning.
- Call out missing lockfiles and nondeterministic builds explicitly.
- Treat unknown licenses as real risk until resolved.

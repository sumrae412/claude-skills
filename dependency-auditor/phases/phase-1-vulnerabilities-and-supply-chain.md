# Phase 1: Vulnerabilities and Supply Chain

Load `../references/vulnerability_assessment_guide.md` before running
this phase.

## Goal

Identify security vulnerabilities and supply-chain risk across direct and
transitive dependencies.

## Ask

- Which ecosystems are in scope?
- Do manifests and lockfiles both exist?
- Is the goal quick triage or a full risk inventory?
- Are there known sensitive packages or recently disclosed CVEs?

## Deterministic Path

Prefer:

- `scripts/dep_scanner.py`

Use it to scan manifests, lockfiles, and dependency trees.

## Check For

- high and critical CVEs
- transitive dependency exposure
- suspicious or unverified provenance
- missing or stale lockfiles
- depth and blast radius of risky transitive packages

## Output

Vulnerability and supply-chain report with severity, affected paths, and
immediate remediation priorities.

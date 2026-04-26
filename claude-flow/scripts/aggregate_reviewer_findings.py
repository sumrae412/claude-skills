#!/usr/bin/env python3
"""Aggregate scored reviewer output into blocking findings."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def registry_index(registry: dict) -> dict[str, dict]:
    return {reviewer["id"]: reviewer for reviewer in registry.get("reviewers", [])}


def aggregate_review_output(review_output: dict, registry: dict) -> dict:
    reviewer_id = review_output.get("reviewer")
    reviewer_entry = registry_index(registry).get(reviewer_id)
    if reviewer_entry is None:
        return review_output

    threshold = reviewer_entry.get("score_threshold")
    criteria = set(reviewer_entry.get("scored_criteria", []))
    if threshold is None or not criteria:
        return review_output

    findings = list(review_output.get("findings", []))
    blockers_added = 0

    for score_entry in review_output.get("scores", []):
        criterion = score_entry.get("criterion")
        score = score_entry.get("score")
        break_case = score_entry.get("break_case", "No break case provided.")

        if criterion not in criteria or not isinstance(score, int):
            continue
        if score >= threshold:
            continue

        findings.append(
            {
                "severity": "HIGH",
                "file": review_output.get("reviewer", "reviewer"),
                "line": 0,
                "title": f"Adversarial score {score}/10 on {criterion}",
                "rationale": break_case,
                "criterion": criterion,
                "break_case": break_case,
                "source": "score-threshold"
            }
        )
        blockers_added += 1

    aggregated = dict(review_output)
    aggregated["findings"] = findings
    aggregated["aggregated_blockers"] = blockers_added
    return aggregated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviewer", required=True, type=Path)
    parser.add_argument("--registry", required=True, type=Path)
    args = parser.parse_args()

    review_output = load_json(args.reviewer)
    registry = load_json(args.registry)
    aggregated = aggregate_review_output(review_output, registry)
    json.dump(aggregated, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

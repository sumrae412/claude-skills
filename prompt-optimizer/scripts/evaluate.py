#!/usr/bin/env python3
"""
Evaluate a prompt's quality across 6 dimensions.
Usage: python3 evaluate.py "Your prompt here"
"""

import sys
import json
import re
from typing import Dict, Tuple

DIMENSIONS = [
    "clarity",
    "specificity",
    "structure",
    "completeness",
    "tone",
    "constraints",
]

RATINGS = ["Poor", "Fair", "Good", "Excellent"]
SCORES = {"Poor": 1, "Fair": 2, "Good": 3, "Excellent": 4}


def heuristic_evaluate(prompt: str) -> Dict[str, dict]:
    """
    Heuristic-based evaluation. For full LLM-powered evaluation,
    invoke this script via Claude with the prompt as context.
    """
    results = {}
    p = prompt.lower()
    words = prompt.split()

    # Clarity
    vague_verbs = ["handle", "deal with", "do something", "make it", "fix it"]
    vague_count = sum(1 for v in vague_verbs if v in p)
    clarity_score = max(1, 4 - vague_count)
    results["clarity"] = {
        "rating": RATINGS[clarity_score - 1],
        "issues": [f"Vague verb detected: '{v}'" for v in vague_verbs if v in p],
    }

    # Specificity
    spec_signals = ["format", "length", "word", "audience", "tone", "example", "output"]
    spec_count = sum(1 for s in spec_signals if s in p)
    spec_score = min(4, 1 + spec_count)
    results["specificity"] = {
        "rating": RATINGS[spec_score - 1],
        "issues": [] if spec_score >= 3 else ["No output format specified", "No audience specified"],
    }

    # Structure
    has_numbered = bool(re.search(r"\d+\.", prompt))
    has_sections = bool(re.search(r"step|phase|section|first|then|finally", p))
    struct_score = 2 + int(has_numbered) + int(has_sections)
    struct_score = min(4, max(1, struct_score))
    results["structure"] = {
        "rating": RATINGS[struct_score - 1],
        "issues": [] if struct_score >= 3 else ["No numbered steps or sections"],
    }

    # Completeness
    completeness_signals = ["context", "background", "goal", "because", "for", "so that"]
    comp_count = sum(1 for s in completeness_signals if s in p)
    has_example = "example" in p or "e.g." in p or "for instance" in p
    comp_score = min(4, 1 + comp_count + int(has_example))
    results["completeness"] = {
        "rating": RATINGS[comp_score - 1],
        "issues": [] if comp_score >= 3 else ["No examples provided", "Missing context/goal statement"],
    }

    # Tone
    tone_signals = ["tone", "voice", "style", "formal", "casual", "professional", "friendly"]
    tone_score = 2 + min(2, sum(1 for s in tone_signals if s in p))
    results["tone"] = {
        "rating": RATINGS[tone_score - 1],
        "issues": [] if tone_score >= 3 else ["Tone not specified"],
    }

    # Constraints
    constraint_signals = ["do not", "don't", "avoid", "must", "only", "limit", "max", "minimum", "no more than"]
    const_count = sum(1 for s in constraint_signals if s in p)
    const_score = min(4, 1 + const_count * 2)
    results["constraints"] = {
        "rating": RATINGS[const_score - 1],
        "issues": [] if const_score >= 3 else ["No explicit constraints found"],
    }

    return results


def overall_rating(results: Dict[str, dict]) -> Tuple[str, float]:
    scores = [SCORES[results[d]["rating"]] for d in DIMENSIONS]
    avg = sum(scores) / len(scores)
    if avg >= 3.5:
        return "Excellent", avg
    elif avg >= 2.5:
        return "Good", avg
    elif avg >= 1.5:
        return "Fair", avg
    else:
        return "Poor", avg


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 evaluate.py \"Your prompt here\"")
        sys.exit(1)

    prompt = " ".join(sys.argv[1:])
    results = heuristic_evaluate(prompt)
    overall, score = overall_rating(results)

    print("\n=== PROMPT QUALITY EVALUATION ===\n")
    print(f"Overall: {overall} ({score:.1f}/4.0)\n")
    print(f"{'Dimension':<15} {'Rating':<12} Issues")
    print("-" * 60)
    for dim in DIMENSIONS:
        r = results[dim]
        issues = "; ".join(r["issues"]) if r["issues"] else "None"
        print(f"{dim.capitalize():<15} {r['rating']:<12} {issues}")

    print("\n=== IMPROVEMENT PRIORITIES ===\n")
    sorted_dims = sorted(DIMENSIONS, key=lambda d: SCORES[results[d]["rating"]])
    for dim in sorted_dims[:3]:
        r = results[dim]
        if r["issues"]:
            print(f"[{r['rating']}] {dim.capitalize()}: {'; '.join(r['issues'])}")

    output = {
        "prompt": prompt,
        "overall": overall,
        "score": round(score, 2),
        "dimensions": results,
    }
    print("\n=== JSON OUTPUT ===\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

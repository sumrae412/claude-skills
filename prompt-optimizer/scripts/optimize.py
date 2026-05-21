#!/usr/bin/env python3
"""
Generate an optimized version of a prompt using specified techniques.
Usage: python3 optimize.py "Your prompt here" --techniques "few-shot,cot"

Available techniques: few-shot, cot, persona, audience, format, constraints,
                      step-by-step, grounding, confidence, checklist
"""

import sys
import argparse
import textwrap
from typing import List


TECHNIQUE_DESCRIPTIONS = {
    "few-shot": "Few-Shot Learning — adds input/output examples",
    "cot": "Chain of Thought — adds step-by-step reasoning instruction",
    "persona": "Expert Persona — wraps prompt with a role/expertise framing",
    "audience": "Audience Persona — specifies who the output is for",
    "format": "Format Specification — adds explicit output format instruction",
    "constraints": "Negative Constraints — adds explicit 'do not' rules",
    "step-by-step": "Step-by-Step Decomposition — breaks task into numbered phases",
    "grounding": "Grounding Constraints — restricts to provided source material",
    "confidence": "Confidence Signaling — asks model to rate certainty of claims",
    "checklist": "Checklist Prompting — adds a quality checklist to work through",
}


def apply_techniques(prompt: str, techniques: List[str]) -> str:
    """Apply selected techniques to transform the prompt."""
    parts = []

    # Persona (prepend)
    if "persona" in techniques:
        parts.append("[Role: You are a domain expert with deep experience in this area.]\n")

    # Audience (prepend)
    if "audience" in techniques:
        parts.append("[Audience: Write for someone who needs clear, actionable guidance.]\n")

    # Grounding (prepend)
    if "grounding" in techniques:
        parts.append("[Constraint: Base your response only on the provided context. "
                     "If something isn't addressed in the source material, say so explicitly.]\n")

    # Original prompt
    parts.append(prompt)

    # Few-shot (append after prompt)
    if "few-shot" in techniques:
        parts.append("\n\n[Examples of the expected output format:"
                     "\nExample 1: [Input] → [Output]"
                     "\nExample 2: [Input] → [Output]"
                     "\n(Replace these with your actual examples)]")

    # CoT (append)
    if "cot" in techniques:
        parts.append("\n\nThink through this step by step before giving your final answer.")

    # Step-by-step (append)
    if "step-by-step" in techniques:
        parts.append("\n\nComplete this in the following phases:"
                     "\n1. Analyze: [describe what analysis is needed]"
                     "\n2. Plan: [describe the planning step]"
                     "\n3. Execute: [describe the execution step]"
                     "\n4. Review: Check your output before finalizing.")

    # Format (append)
    if "format" in techniques:
        parts.append("\n\nFormat your response as:"
                     "\n- Summary (1-2 sentences)"
                     "\n- Main content (structured with headers)"
                     "\n- Next steps or recommendations")

    # Constraints (append)
    if "constraints" in techniques:
        parts.append("\n\nConstraints:"
                     "\n- Do not use jargon or technical terms without defining them"
                     "\n- Do not include information not directly relevant to the task"
                     "\n- Keep each point concise and actionable")

    # Confidence (append)
    if "confidence" in techniques:
        parts.append("\n\nFor any factual claims, indicate your confidence: "
                     "(High = well-established, Medium = likely but verify, Low = uncertain).")

    # Checklist (append)
    if "checklist" in techniques:
        parts.append("\n\nBefore finalizing, verify:"
                     "\n□ All parts of the request are addressed"
                     "\n□ The response is appropriately scoped (not too broad or narrow)"
                     "\n□ The tone matches the context"
                     "\n□ No important caveats are missing")

    return "".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Optimize a prompt using selected techniques."
    )
    parser.add_argument("prompt", nargs="+", help="The prompt to optimize")
    parser.add_argument(
        "--techniques",
        type=str,
        default="cot,format",
        help="Comma-separated list of techniques to apply",
    )
    parser.add_argument(
        "--list-techniques",
        action="store_true",
        help="List all available techniques",
    )
    args = parser.parse_args()

    if args.list_techniques:
        print("\nAvailable techniques:\n")
        for key, desc in TECHNIQUE_DESCRIPTIONS.items():
            print(f"  {key:<15} {desc}")
        return

    prompt = " ".join(args.prompt)
    techniques = [t.strip().lower() for t in args.techniques.split(",")]

    invalid = [t for t in techniques if t not in TECHNIQUE_DESCRIPTIONS]
    if invalid:
        print(f"Unknown techniques: {', '.join(invalid)}")
        print("Run with --list-techniques to see options.")
        sys.exit(1)

    optimized = apply_techniques(prompt, techniques)

    print("\n=== ORIGINAL PROMPT ===\n")
    print(textwrap.fill(prompt, width=80))

    print("\n=== APPLIED TECHNIQUES ===\n")
    for t in techniques:
        print(f"  ✓ {TECHNIQUE_DESCRIPTIONS[t]}")

    print("\n=== OPTIMIZED PROMPT ===\n")
    print(optimized)

    print("\n=== NOTES ===")
    print("Placeholders in [brackets] should be replaced with your actual content.")
    print("Run evaluate.py on the optimized prompt to verify quality improvement.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Redact obvious secrets from review payloads before reviewer dispatch."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REDACTION_RULES = [
    (
        "private_key",
        re.compile(
            r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",
            re.DOTALL,
        ),
        "[REDACTED PRIVATE KEY]",
    ),
    (
        "bearer_token",
        re.compile(r"Bearer\s+[A-Za-z0-9._-]+"),
        "Bearer [REDACTED]",
    ),
    (
        "assignment_secret",
        re.compile(
            r"(?im)\b(api[_-]?key|token|secret|password)\b(\s*[:=]\s*)([\"']?)([^\"'\n]+)(\3)"
        ),
        None,
    ),
    (
        "aws_access_key",
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        "[REDACTED AWS ACCESS KEY]",
    ),
    (
        "github_token",
        re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
        "[REDACTED GITHUB TOKEN]",
    ),
    (
        "openai_key",
        re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
        "[REDACTED OPENAI KEY]",
    ),
]


def scrub_text(text: str) -> tuple[str, list[dict[str, int | str]]]:
    """Return scrubbed text plus a redaction summary."""
    scrubbed = text
    redactions: list[dict[str, int | str]] = []

    for rule_name, pattern, replacement in REDACTION_RULES:
        if rule_name == "assignment_secret":
            count = 0

            def repl(match: re.Match[str]) -> str:
                nonlocal count
                count += 1
                return f"{match.group(1)}{match.group(2)}{match.group(3)}[REDACTED]{match.group(3)}"

            scrubbed = pattern.sub(repl, scrubbed)
        else:
            scrubbed, count = pattern.subn(replacement, scrubbed)

        if count:
            redactions.append({"rule": rule_name, "count": count})

    return scrubbed, redactions


def _read_input(path_arg: str | None) -> str:
    if path_arg:
        return Path(path_arg).read_text()
    return sys.stdin.read()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input_file",
        nargs="?",
        help="Optional diff/payload file path. Defaults to stdin.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON with the scrubbed text and redaction summary.",
    )
    args = parser.parse_args()

    text = _read_input(args.input_file)
    if not text:
        print("No review payload provided", file=sys.stderr)
        return 2

    scrubbed, redactions = scrub_text(text)

    if args.json:
        json.dump(
            {
                "scrubbed_text": scrubbed,
                "redactions": redactions,
                "redaction_count": sum(item["count"] for item in redactions),
            },
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
    else:
        sys.stdout.write(scrubbed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

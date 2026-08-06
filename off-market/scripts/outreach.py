"""Outreach letter drafting helpers.

This module is a thin templating shell around an LLM prompt. The codebase doesn't
call any LLM directly — the orchestrating Claude Code session reads the brief
produced by ``render_outreach_brief`` and writes the letter body. ``write_letter_file``
then persists that body to disk.

NO httpx / NO API calls / NO LLM SDK — pure templating.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CandidateBrief:
    """A single candidate's outreach context, ready for the LLM to consume."""

    address: str  # full property address
    mailing: str  # owner mailing (may differ from address)
    score: int  # propensity total
    tier: str  # "act_this_week" / "high_priority" / "worth_a_letter"
    reasons: tuple[str, ...] = field(default_factory=tuple)  # propensity reason codes
    optional_user_note: str = ""  # human-supplied "porch swing on Elm" type note


def _parse_reasons(raw: str) -> tuple[str, ...]:
    """Split discover.py's semicolon-separated reasons field into a tuple."""
    if not raw:
        return ()
    return tuple(r.strip() for r in raw.split(";") if r.strip())


def load_candidates(csv_path: Path, top: int = 20) -> list[CandidateBrief]:
    """Load the top-N candidates from a discover-output candidates.csv,
    sorted by propensity score descending."""
    rows: list[CandidateBrief] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                score = int(row.get("propensity_total", "0") or "0")
            except ValueError:
                score = 0
            rows.append(
                CandidateBrief(
                    address=row.get("address", ""),
                    mailing=row.get("owner_mailing", ""),
                    score=score,
                    tier=row.get("tier", ""),
                    reasons=_parse_reasons(row.get("reasons", "")),
                )
            )
    rows.sort(key=lambda c: c.score, reverse=True)
    return rows[:top]


def _is_out_of_state(mailing: str) -> bool:
    """Best-effort: spot a non-PA state code in the mailing field."""
    if not mailing:
        return False
    # Look for ", XX," or ", XX " where XX is two letters and not PA.
    m = re.search(r",\s*([A-Z]{2})[\s,]", mailing.upper())
    if not m:
        return False
    return m.group(1) != "PA"


def render_outreach_brief(candidate: CandidateBrief, voice_profile: str) -> str:
    """Produce the prompt block the Claude orchestrator will read to draft one letter.

    Contains: the candidate's context, the voice profile, the tone constraints from
    references/letter-craft.md (warm, specific, no investor jargon, generic salutation
    since owner_name is a code, ends with placeholders for <Your Name> / <your-email>).
    """
    lines: list[str] = []
    lines.append("# Draft an off-market outreach letter")
    lines.append("")
    lines.append("## Candidate")
    lines.append(f"- Address: {candidate.address}")

    mailing_line = f"- Mailing: {candidate.mailing}"
    if _is_out_of_state(candidate.mailing):
        mailing_line += " (out-of-state — absentee)"
    lines.append(mailing_line)

    lines.append(f"- Propensity tier: {candidate.tier} (score {candidate.score})")

    if candidate.reasons:
        lines.append("- Signal reasons:")
        for r in candidate.reasons:
            lines.append(f"  - {r}")
    else:
        lines.append("- Signal reasons: (none recorded)")

    if candidate.optional_user_note:
        lines.append("")
        lines.append("## User note about this property")
        lines.append(candidate.optional_user_note)

    lines.append("")
    lines.append("## Voice profile (excerpt)")
    lines.append(voice_profile.rstrip())

    lines.append("")
    lines.append("## Tone constraints (from references/letter-craft.md)")
    lines.append("- Warm, specific to this property/street.")
    lines.append(
        '- NO investor jargon: avoid "we buy houses", "cash offer", '
        '"investment opportunity", "no realtors".'
    )
    lines.append(
        "- Generic salutation — WPRDC owner_name is a code, not a real name. "
        'Use "To the homeowner at <address>" or similar.'
    )
    lines.append(
        "- Sign with placeholders: <Your Name> / <your-email>. The user replaces "
        "these at print time."
    )
    lines.append("- Length: 100-200 words. One page of handwritten-friendly text.")
    lines.append(
        "- Mention a real detail about the property or street (the user can edit in "
        "specifics; the LLM should leave a `[<specific detail>]` placeholder where "
        "unknown)."
    )

    lines.append("")
    lines.append("## Now draft the letter.")
    lines.append("")

    return "\n".join(lines)


def _sanitize_address_for_filename(address: str) -> str:
    """Turn an address string into a safe filename stem."""
    # Replace whitespace and commas with underscores, drop any non-safe chars.
    cleaned = re.sub(r"[,\s]+", "_", address.strip())
    cleaned = re.sub(r"[^A-Za-z0-9_\-]", "", cleaned)
    cleaned = cleaned.strip("_")
    return cleaned or "unknown"


def write_letter_file(candidate: CandidateBrief, body: str, output_dir: Path) -> Path:
    """Write a single letter as ``<output_dir>/letters/<sanitized_address>.md``.

    Markdown format with H1 = address, then the letter body. Returns the path written.
    """
    letters_dir = Path(output_dir) / "letters"
    letters_dir.mkdir(parents=True, exist_ok=True)

    stem = _sanitize_address_for_filename(candidate.address)
    path = letters_dir / f"{stem}.md"

    content = f"# {candidate.address}\n\n{body.rstrip()}\n"
    path.write_text(content, encoding="utf-8")
    return path

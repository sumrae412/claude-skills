#!/usr/bin/env python3
"""collab_polish.py — Two-model collaborative polish loop for resume-tailor.

NOT a debate. A sequential, converge-to-consensus refinement loop:

    round 0 (turn 1): Claude reads the JD + fact-inventory, writes the first analysis
    round 1 (turn 2): GPT-5.6 Sol polishes it, hands back
    round 2 (turn 3): Claude polishes, hands back
    ... alternating, up to --rounds polish handoffs (default 4) ...
    stop EARLY when the receiving model returns converged=true.

The loop always ENDS ON CLAUDE (best writer gets the last word) unless it
converges first. Total model calls = 1 (Claude seed) + up to --rounds.

Both models run through OpenRouter (one transport, per-request model slug):
    - Claude   : anthropic/claude-opus-4.8   (override with --claude-model)
    - ChatGPT  : openai/gpt-5.6-sol           (override with --gpt-model)

TRUTH-PRESERVATION IS A HARD CONSTRAINT (the resume analog of the SMS 160-char
cap that killed the cross-provider polish pipeline on 2026-07-15). Every turn
receives the canonical fact-inventory as IMMUTABLE context and is forbidden to
introduce any employer, title, date, number, or skill not present in it. A
post-loop guard diffs the consensus artifact's proper nouns / numbers against
the inventory and prints any additions as warnings for human review.

Both models must obey the resume/cover-letter skill's own principles — pass the governing
docs with --principles-file (repeatable) and they are injected verbatim into every turn as
BINDING constraints (bullet bans, plain-language voice, opener rules, §9 sameness test).
Running with no --principles-file prints a warning; do not ship that output.

Usage:
    export OPENROUTER_API_KEY=...          # from ~/.claude/.local.env
    ./collab_polish.py \
        --stage jd-analysis \
        --jd-file jd.md \
        --fact-inventory resume.md \
        --principles-file ../../shared/communication-principles.md \
        --output out/jd-profile.md

    ./collab_polish.py \
        --stage draft-polish \
        --jd-file jd.md \
        --fact-inventory resume.md \
        --artifact draft-bullets.md \
        --output out/polished-bullets.md

Exit codes:
    0  consensus artifact written
    2  configuration error (missing key / file)
    3  all model calls failed (nothing to write)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_CLAUDE_MODEL = "anthropic/claude-opus-4.8"
DEFAULT_GPT_MODEL = "openai/gpt-5.6-sol"
DEFAULT_ROUNDS = 4          # polish handoffs AFTER Claude's seed turn
REQUEST_TIMEOUT = 180       # seconds per model call
MAX_RETRIES = 2             # per call, on transport / 5xx / 429


# --------------------------------------------------------------------------- #
# Prompts
# --------------------------------------------------------------------------- #

TRUTH_GUARD = (
    "HARD RULE — TRUTH PRESERVATION. You may only SELECT, EMPHASIZE, REORDER, and "
    "REFRAME facts that already appear in the FACT INVENTORY below. You must NEVER "
    "invent, inflate, or imply an employer, job title, date, degree, certification, "
    "metric, number, tool, or skill that is not present in the inventory. If a "
    "stronger-sounding claim would require information not in the inventory, do NOT "
    "make it. Any reframe you are not fully certain traces to the inventory must be "
    "tagged inline as `[verify]`. Fabrication is a failure, not a polish."
)

STAGE_BRIEF = {
    "jd-analysis": (
        "TASK — JD ANALYSIS. Produce a structured job profile from the JOB DESCRIPTION: "
        "(1) role recap (title, seniority, scope, industry) + a 3-6 line plain-language "
        "summary of what the role actually does; (2) weighted focus areas (weights sum to "
        "1.0) tied to recap items; (3) must-have vs nice-to-have keywords (ATS tiers); "
        "(4) seniority + scope signals; (5) the single hardest thing this hire must do that "
        "most keyword-matching candidates cannot (hiring risk, one sentence). Ground every "
        "focus-area weight in JD evidence. Use the FACT INVENTORY only to note where the "
        "candidate is strong or has a gap vs the profile — never to invent JD content."
    ),
    "draft-polish": (
        "TASK — DRAFT POLISH. Improve the CURRENT DRAFT of tailored resume material so it "
        "leads with the conclusion, uses the JD's language where truthful, quantifies only "
        "with numbers present in the inventory, and reads in a plain, senior, non-marketing "
        "voice. Keep every materially important experience visible. Improve clarity, "
        "ordering, and ATS keyword coverage — do NOT pad length or add claims."
    ),
    "cover-letter": (
        "TASK — COVER LETTER POLISH. Improve the CURRENT DRAFT of the cover letter. Lead "
        "with a career-thesis statement and end on the company's specific bet — NEVER open "
        "with \"I was excited\" or any hollow opener, and never make it all-about-me. Plain, "
        "direct voice, no marketing jargon. Do not knock or dismiss any other company or "
        "product. Every claim must trace to the FACT INVENTORY."
    ),
}

RESPONSE_CONTRACT = (
    "OUTPUT CONTRACT — respond with a SINGLE JSON object and nothing else (no prose, no "
    "markdown code fence). Schema:\n"
    "{\n"
    '  "artifact": "<the full revised artifact as markdown text>",\n'
    '  "converged": <true if you would make NO further substantive changes, else false>,\n'
    '  "remaining_concerns": "<one or two lines: what still needs work, or empty if converged>",\n'
    '  "changes_made": "<one or two lines summarizing what you changed this turn>"\n'
    "}"
)


def system_prompt(model_label: str, stage: str, principles_text: str = "") -> str:
    principles_block = ""
    if principles_text.strip():
        principles_block = (
            "GOVERNING PRINCIPLES — BINDING HOUSE RULES. The text below is the resume/"
            "cover-letter skill's own governing principles. Treat every rule in it as a HARD "
            "constraint on your output, exactly as if you authored the skill. This includes: "
            "banned bullet patterns and low-signal phrasings, plain-language / no-marketing-"
            "jargon voice, the 'I help' and audience-centered framing, lead-with-the-conclusion "
            "ordering, cover-letter opener rules, and never attacking other companies/products. "
            "Before finalizing each turn, run the sameness generic-swap test: if swapping the "
            "company name leaves a line still working, it is too generic — rewrite it. A polish "
            "that reads better but breaks any of these rules is a DEFECT, not an improvement.\n\n"
            f"----- BEGIN GOVERNING PRINCIPLES -----\n{principles_text.strip()}\n"
            "----- END GOVERNING PRINCIPLES -----\n\n"
        )
    return (
        f"You are {model_label}, collaborating with another top-tier model to tailor a "
        f"resume to a specific job. This is a COLLABORATION, not a debate: build on the "
        f"other model's work, keep what is good, fix what is weak, and converge toward a "
        f"shared best version. Signal convergence honestly — do not invent changes just to "
        f"look busy, and do not rubber-stamp a draft that still has real problems.\n\n"
        f"{STAGE_BRIEF[stage]}\n\n{principles_block}{TRUTH_GUARD}\n\n{RESPONSE_CONTRACT}"
    )


def turn_user_message(
    stage: str, jd_text: str, fact_inventory: str, current_artifact: str | None, turn_no: int
) -> str:
    parts = [f"=== JOB DESCRIPTION ===\n{jd_text}\n"]
    parts.append(f"=== FACT INVENTORY (canonical resume — IMMUTABLE) ===\n{fact_inventory}\n")
    if current_artifact:
        parts.append(
            "=== CURRENT ARTIFACT (from the previous turn — revise and improve) ===\n"
            f"{current_artifact}\n"
        )
        parts.append(
            "Revise the CURRENT ARTIFACT. Preserve everything that is already good. "
            "Return the FULL revised artifact in the `artifact` field (not a diff)."
        )
    else:
        parts.append(
            "There is no prior artifact yet — you are writing the FIRST version. "
            "Return it in the `artifact` field."
        )
    return "\n".join(parts)


# --------------------------------------------------------------------------- #
# OpenRouter call
# --------------------------------------------------------------------------- #

@dataclass
class TurnResult:
    turn_no: int
    model: str
    label: str
    artifact: str
    converged: bool
    remaining_concerns: str
    changes_made: str
    raw_ok: bool  # False if we had to fall back to raw text (JSON contract broken)


def _extract_json_object(text: str) -> dict | None:
    """Defensively pull the first balanced JSON object out of a model response.

    Handles: clean JSON, JSON wrapped in ```json fences, and JSON with leading/
    trailing prose. Returns None if no parseable object is found.
    """
    if not text:
        return None
    # Strip a leading code fence if present.
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    candidates = []
    if fenced:
        candidates.append(fenced.group(1))
    # First balanced-brace span.
    start = text.find("{")
    if start != -1:
        depth = 0
        in_str = False
        esc = False
        for i in range(start, len(text)):
            c = text[i]
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
            else:
                if c == '"':
                    in_str = True
                elif c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0:
                        candidates.append(text[start : i + 1])
                        break
    for cand in candidates:
        try:
            obj = json.loads(cand)
            if isinstance(obj, dict) and "artifact" in obj:
                return obj
        except json.JSONDecodeError:
            continue
    return None


def call_openrouter(api_key: str, model: str, system: str, user: str) -> str:
    """Return the assistant message content, or raise RuntimeError after retries."""
    payload = json.dumps(
        {
            "model": model,
            "temperature": 0.4,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
    ).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        # OpenRouter attribution headers (optional but recommended).
        "HTTP-Referer": "https://github.com/sumrae412/claude-skills",
        "X-Title": "resume-tailor collaborative polish",
    }
    last_err = ""
    for attempt in range(MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(OPENROUTER_URL, data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            choices = body.get("choices") or []
            if not choices:
                last_err = f"no choices in response: {json.dumps(body)[:300]}"
                raise RuntimeError(last_err)
            content = choices[0].get("message", {}).get("content", "")
            if not content:
                last_err = "empty content in response"
                raise RuntimeError(last_err)
            return content
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:300]
            last_err = f"HTTP {e.code}: {detail}"
            # Retry only on rate-limit / server errors.
            if e.code in (429, 500, 502, 503, 504) and attempt < MAX_RETRIES:
                time.sleep(2 * (attempt + 1))
                continue
            raise RuntimeError(last_err)
        except (urllib.error.URLError, TimeoutError, RuntimeError) as e:
            last_err = str(e)
            if attempt < MAX_RETRIES:
                time.sleep(2 * (attempt + 1))
                continue
            raise RuntimeError(last_err)
    raise RuntimeError(last_err or "unknown error")


def run_turn(
    api_key: str, stage: str, jd_text: str, fact_inventory: str,
    current_artifact: str | None, turn_no: int, model: str, label: str,
    principles_text: str = "",
) -> TurnResult:
    system = system_prompt(label, stage, principles_text)
    user = turn_user_message(stage, jd_text, fact_inventory, current_artifact, turn_no)
    content = call_openrouter(api_key, model, system, user)
    obj = _extract_json_object(content)
    if obj is None:
        # JSON contract broken — fall back to using the raw text as the artifact,
        # do NOT silently drop it, and do NOT trust a convergence signal we can't read.
        return TurnResult(
            turn_no=turn_no, model=model, label=label, artifact=content.strip(),
            converged=False, remaining_concerns="(response was not valid JSON; used raw text)",
            changes_made="(unparseable response)", raw_ok=False,
        )
    return TurnResult(
        turn_no=turn_no, model=model, label=label,
        artifact=str(obj.get("artifact", "")).strip(),
        converged=bool(obj.get("converged", False)),
        remaining_concerns=str(obj.get("remaining_concerns", "")).strip(),
        changes_made=str(obj.get("changes_made", "")).strip(),
        raw_ok=True,
    )


# --------------------------------------------------------------------------- #
# Truth guard (post-loop)
# --------------------------------------------------------------------------- #

_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9&.\-]{2,}")
_NUM_RE = re.compile(r"\b\d[\d,.]*%?\b")
# Common words that are noise for a proper-noun/skill diff.
_STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "into", "their", "these",
    "your", "our", "his", "her", "role", "team", "work", "led", "built", "drove",
    "which", "while", "when", "were", "was", "has", "have", "had", "will", "can",
    "verify", "resume", "candidate", "experience", "responsibilities", "must", "nice",
    # Section-heading words and bullet-initial verbs — capitalized by position, not
    # proper nouns. Live smoke run flagged "Summary"/"Lead" as noise; suppress them.
    "summary", "skills", "education", "profile", "objective", "highlights",
    "lead", "leads", "own", "owns", "build", "builds", "reduce", "reduced", "manage",
    "managed", "manages", "drive", "drives", "deliver", "delivered", "improve",
    "improved", "created", "designed", "developed", "responsible", "reordered",
}


def truth_guard(artifact: str, fact_inventory: str) -> tuple[list[str], list[str]]:
    """Heuristic: surface capitalized tokens / numbers in the artifact that do NOT
    appear in the fact inventory. These are review candidates, not hard failures —
    JD keywords legitimately appear in the artifact too, so this is advisory."""
    inv_lower = fact_inventory.lower()
    new_tokens: list[str] = []
    for tok in _TOKEN_RE.findall(artifact):
        if tok.lower() in _STOPWORDS:
            continue
        # Only flag tokens that look like proper nouns / acronyms (has uppercase).
        if not any(c.isupper() for c in tok):
            continue
        if tok.lower() not in inv_lower:
            new_tokens.append(tok)
    new_numbers = [n for n in _NUM_RE.findall(artifact) if n.strip(".,%") and n not in fact_inventory]
    # Dedupe, preserve order.
    def _dedupe(xs):
        seen, out = set(), []
        for x in xs:
            k = x.lower()
            if k not in seen:
                seen.add(k); out.append(x)
        return out
    return _dedupe(new_tokens), _dedupe(new_numbers)


# --------------------------------------------------------------------------- #
# Main loop
# --------------------------------------------------------------------------- #

def main() -> int:
    ap = argparse.ArgumentParser(description="Two-model collaborative polish loop (resume-tailor).")
    ap.add_argument("--stage", required=True, choices=["jd-analysis", "draft-polish", "cover-letter"])
    ap.add_argument("--jd-file", required=True, help="Path to jd.md")
    ap.add_argument("--fact-inventory", required=True, help="Path to canonical resume (markdown)")
    ap.add_argument("--artifact", help="Path to current draft (required for draft-polish and cover-letter)")
    ap.add_argument("--principles-file", action="append", default=[], metavar="PATH",
                    help="Governing principle file to inject as a BINDING constraint into every "
                         "turn (repeatable). Pass the resume/cover-letter skill's own principle "
                         "docs so both models obey them — do NOT paraphrase; pass the real files.")
    ap.add_argument("--output", required=True, help="Where to write the consensus artifact")
    ap.add_argument("--rounds", type=int, default=DEFAULT_ROUNDS,
                    help=f"Max polish handoffs after Claude's seed turn (default {DEFAULT_ROUNDS})")
    ap.add_argument("--claude-model", default=DEFAULT_CLAUDE_MODEL)
    ap.add_argument("--gpt-model", default=DEFAULT_GPT_MODEL)
    args = ap.parse_args()

    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY is not set (check ~/.claude/.local.env — it is "
              "currently present but EMPTY). Populate it, then re-run.", file=sys.stderr)
        return 2

    jd_path = Path(args.jd_file)
    inv_path = Path(args.fact_inventory)
    for p, label in [(jd_path, "--jd-file"), (inv_path, "--fact-inventory")]:
        if not p.is_file():
            print(f"ERROR: {label} not found: {p}", file=sys.stderr)
            return 2
    jd_text = jd_path.read_text(encoding="utf-8")
    fact_inventory = inv_path.read_text(encoding="utf-8")

    # Governing principles → injected verbatim (never paraphrased) as binding constraints.
    principle_chunks: list[str] = []
    for pf in args.principles_file:
        pp = Path(pf)
        if not pp.is_file():
            print(f"ERROR: --principles-file not found: {pp}", file=sys.stderr)
            return 2
        principle_chunks.append(f"### SOURCE: {pp.name}\n{pp.read_text(encoding='utf-8')}")
    principles_text = "\n\n".join(principle_chunks)
    if not principles_text.strip():
        print("WARNING: no --principles-file passed. The models will polish WITHOUT the "
              "resume/cover-letter skill's house rules (bullet bans, plain-language voice, "
              "opener rules, sameness test). Pass the governing files for compliant output.",
              file=sys.stderr)

    current_artifact: str | None = None
    if args.stage in ("draft-polish", "cover-letter"):
        if not args.artifact or not Path(args.artifact).is_file():
            print(f"ERROR: {args.stage} requires --artifact pointing to an existing draft.",
                  file=sys.stderr)
            return 2
        current_artifact = Path(args.artifact).read_text(encoding="utf-8")

    # Turn sequence: Claude seeds (turn 1), then alternate GPT, Claude, ... for --rounds.
    # Roster is built so the LAST turn is Claude whenever rounds is even (default 4 → ends Claude).
    roster = [(args.claude_model, "Claude")]
    for i in range(args.rounds):
        if i % 2 == 0:
            roster.append((args.gpt_model, "GPT-5.6 Sol"))
        else:
            roster.append((args.claude_model, "Claude"))

    transcript: list[TurnResult] = []
    last_good_artifact = current_artifact
    prev_converged = False

    for turn_no, (model, label) in enumerate(roster, start=1):
        try:
            result = run_turn(
                api_key, args.stage, jd_text, fact_inventory,
                current_artifact, turn_no, model, label, principles_text,
            )
        except RuntimeError as e:
            print(f"[turn {turn_no}] {label} ({model}) FAILED: {e}", file=sys.stderr)
            # Fallbacks[] semantics: keep the last good artifact and stop the loop
            # rather than shipping nothing. Consensus = best draft reached so far.
            break

        transcript.append(result)
        marker = "converged" if result.converged else "continue"
        json_note = "" if result.raw_ok else " [JSON-broken→raw]"
        print(f"[turn {turn_no}] {label}: {marker}{json_note} — {result.changes_made or '(no summary)'}",
              file=sys.stderr)

        if result.artifact:
            last_good_artifact = result.artifact
            current_artifact = result.artifact

        # Early consensus: two consecutive parseable turns both report converged.
        if result.raw_ok and result.converged and prev_converged:
            print(f"[stop] consensus reached after turn {turn_no}.", file=sys.stderr)
            break
        prev_converged = result.raw_ok and result.converged

    if last_good_artifact is None:
        print("ERROR: no artifact was produced by any turn.", file=sys.stderr)
        return 3

    # Post-loop truth guard.
    new_tokens, new_numbers = truth_guard(last_good_artifact, fact_inventory)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(last_good_artifact, encoding="utf-8")

    # Structured summary to stderr so callers/humans can review provenance.
    print("\n===== COLLAB POLISH SUMMARY =====", file=sys.stderr)
    print(f"stage: {args.stage}  turns run: {len(transcript)}  rounds cap: {args.rounds}", file=sys.stderr)
    print(f"consensus written to: {out_path}", file=sys.stderr)
    if transcript:
        last = transcript[-1]
        print(f"final turn: {last.label}  converged={last.converged}  "
              f"remaining_concerns: {last.remaining_concerns or '(none)'}", file=sys.stderr)
    if new_tokens or new_numbers:
        print("\n⚠️  TRUTH-GUARD REVIEW — tokens/numbers in the consensus not found verbatim in "
              "the fact inventory (may be legit JD keywords; verify each):", file=sys.stderr)
        if new_tokens:
            print(f"    proper-noun/skill candidates: {', '.join(new_tokens[:40])}", file=sys.stderr)
        if new_numbers:
            print(f"    number candidates: {', '.join(new_numbers[:40])}", file=sys.stderr)
    else:
        print("truth-guard: no unrecognized proper nouns or numbers introduced. ✅", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

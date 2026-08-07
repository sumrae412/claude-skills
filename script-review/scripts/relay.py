#!/usr/bin/env python3
"""Relay one turn between this conversation and an OpenAI reviewer.

    relay.py send --topic <id> --message <file> [context options]
    relay.py show --topic <id>

One invocation is one visible exchange. The message file is sent verbatim. The
reply is printed in full to stdout so it lands in the conversation unedited.
Nothing else happens. There is no second round unless it is invoked.

Context is pulled mechanically from project files, never composed. Every context
option quotes stored text and cites where it came from. If a requested fact is
not in the facts file, it is reported missing and nothing is attached in its
place, which is the whole point: an unverified claim cannot be promoted into a
context block by being phrased confidently.

Context options:
    --working-file <path> --slide <n>   quote the neighbouring slides
    --fact <substring>                  quote matching lines from the facts file
                                        (repeatable)
    --facts-file <path>                 required whenever --fact is used
    --no-context                        send the message and nothing else
    --instruction <text>                Summer's steer for this round, attached
                                        as hers and labelled as hers
"""
import argparse, datetime, glob, hashlib, json, os, re, sys, urllib.error, urllib.request

# The current exchange is fenced by these. Context is assembled strictly outside
# them, and the bytes between them are re-hashed immediately before the request
# leaves. Do not use them for anything else.
EXCHANGE_OPEN = "<<<CURRENT EXCHANGE, VERBATIM>>>"
EXCHANGE_CLOSE = "<<<END CURRENT EXCHANGE>>>"

SESSION_TRANSCRIPTS = "~/.claude/projects/*/[0-9a-f]*-*.jsonl"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SYSTEM_PROMPT_PATH = os.path.join(SCRIPT_DIR, "reviewer-system.md")
# No default facts file. It is project-specific, and a wrong default would
# quietly attach facts from the wrong course. --fact requires --facts-file.
DEFAULT_FACTS = None
# Transcripts hold course content, so they stay out of the repo. Override with
# SCRIPT_REVIEW_STATE when working on something other than the default project.
TRANSCRIPT_ROOT = os.path.expanduser(
    os.environ.get("SCRIPT_REVIEW_STATE", "~/Documents/script-review"))
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-5.2"
CREDENTIAL_FILE = "~/.claude/.local.env"
CREDENTIAL_NAME = "OPENROUTER_API_KEY"


def load_credential():
    if os.environ.get(CREDENTIAL_NAME):
        return os.environ[CREDENTIAL_NAME]
    path = os.path.expanduser(CREDENTIAL_FILE)
    if not os.path.exists(path):
        return None
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name.strip() == CREDENTIAL_NAME:
            return value.strip().strip('"').strip("'")
    return None


def read_last_assistant_text(steps_back, session_id=None):
    """Claude's own words, read out of the live session transcript.

    This exists so nobody retypes them. A retyped message is a rewritten message
    sooner or later, and preserving the actual text is the point of the relay.
    Returns (text, source_description).
    """
    # Pin the conversation. Never fall back to "most recently modified", which
    # picks whichever session happens to be busiest and would relay a different
    # conversation's text. Caught during construction, before it could happen.
    session_id = session_id or os.environ.get("CLAUDE_CODE_SESSION_ID")
    if not session_id:
        sys.exit("cannot identify the current session. Set CLAUDE_CODE_SESSION_ID "
                 "or pass --session-id. Refusing to guess which conversation to "
                 "read.")
    candidates = [path for path in glob.glob(os.path.expanduser(SESSION_TRANSCRIPTS))
                  if session_id in os.path.basename(path)]
    if not candidates:
        sys.exit(f"no transcript found for session {session_id}; "
                 "pass --message instead")
    path = candidates[0]

    blocks = []
    with open(path) as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("type") != "assistant":
                continue
            content = row.get("message", {}).get("content", [])
            texts = [part.get("text") for part in content
                     if isinstance(part, dict) and part.get("type") == "text"]
            joined = "\n".join(text for text in texts if text)
            if joined.strip():
                blocks.append(joined)
    if len(blocks) < steps_back:
        sys.exit(f"only {len(blocks)} assistant message(s) in transcript; "
                 f"cannot step back {steps_back}")
    return blocks[-steps_back], f"{os.path.basename(path)} (back {steps_back})"


def verify_verbatim(assembled_turn, expected_digest):
    """Abort unless the fenced exchange is byte-identical to the candidate.

    Assembly, context attachment and formatting all happen between hashing and
    this check, so this is what makes 'verbatim' an enforced property rather
    than a promise.
    """
    start = assembled_turn.find(EXCHANGE_OPEN)
    end = assembled_turn.find(EXCHANGE_CLOSE)
    if start < 0 or end < 0:
        sys.exit("VERBATIM GUARD FAILED: exchange fence missing. Nothing sent.")
    embedded = assembled_turn[start + len(EXCHANGE_OPEN):end]
    if embedded.startswith("\n"):
        embedded = embedded[1:]
    if embedded.endswith("\n"):
        embedded = embedded[:-1]
    actual = hashlib.sha256(embedded.encode()).hexdigest()
    if actual != expected_digest:
        sys.exit("VERBATIM GUARD FAILED: the embedded exchange does not match "
                 f"the candidate.\n  expected {expected_digest}\n  embedded "
                 f"{actual}\nNothing sent.")


def transcript_path(topic):
    os.makedirs(TRANSCRIPT_ROOT, exist_ok=True)
    return os.path.join(TRANSCRIPT_ROOT, f"{topic}.json")


def load_transcript(topic):
    path = transcript_path(topic)
    return json.load(open(path)) if os.path.exists(path) else []


# ---------- mechanical context ----------

def split_slides(working_text):
    """Return [(heading, body)] for every '## ...' block in a working file."""
    parts = re.split(r"^(##\s+.+)$", working_text, flags=re.M)
    blocks = []
    for index in range(1, len(parts), 2):
        blocks.append((parts[index].strip(), parts[index + 1]))
    return blocks


def slide_number(heading):
    match = re.search(r"Slide\s+(\d+)", heading)
    return int(match.group(1)) if match else None


def status_of(body):
    """Quote the file's own status line. Never infer one."""
    match = re.search(r"^\s*(?:\*\*)?(LOCKED[^\n*]*|Status:[^\n]*)", body, re.M)
    if not match:
        return "no status recorded"
    text = match.group(1).strip().rstrip("*").strip()
    return re.sub(r"^Status:\s*", "", text)


def title_of(body):
    match = re.search(r"^Title\s*\n(.+)$", body, re.M)
    return match.group(1).strip() if match else None


def last_stanza(body):
    match = re.search(r"^Script\s*\n(.*?)(?=\n##|\n###|\Z)", body, re.S | re.M)
    if not match:
        return None
    stanzas = [s.strip() for s in match.group(1).strip().split("\n\n") if s.strip()]
    return stanzas[-1] if stanzas else None


def first_stanza(body):
    match = re.search(r"^Script\s*\n(.*?)(?=\n##|\n###|\Z)", body, re.S | re.M)
    if not match:
        return None
    stanzas = [s.strip() for s in match.group(1).strip().split("\n\n") if s.strip()]
    return stanzas[0] if stanzas else None


def neighbour_context(working_file, slide, attached):
    """Quote the neighbouring slides out of the working file. No prose."""
    text = open(working_file).read()
    blocks = split_slides(text)
    numbered = [(slide_number(h), h, b) for h, b in blocks]
    numbered = [n for n in numbered if n[0] is not None]
    numbered.sort()

    lines = []
    for label, target, stanza_function, stanza_label in (
            ("Previous", slide - 1, last_stanza, "Ends on"),
            ("Next", slide + 1, first_stanza, "Opens on")):
        found = next((n for n in numbered if n[0] == target), None)
        if not found:
            continue
        _, heading, body = found
        lines.append(f"{label} slide: {heading.lstrip('# ').strip()}")
        lines.append(f"Status: {status_of(body)}")
        title = title_of(body)
        if title:
            lines.append(f"Title: {title}")
        stanza = stanza_function(body)
        if stanza:
            lines.append(f"{stanza_label}:")
            lines.extend("    " + line for line in stanza.splitlines())
        lines.append("")
        attached.append(f"slide {target} ({status_of(body)})")
    if not lines:
        return ""
    return ("--- NEIGHBOURING SLIDES, quoted from "
            f"{os.path.basename(working_file)} ---\n" + "\n".join(lines))


def fact_context(facts_file, wanted, attached, missing):
    """Quote matching lines verbatim, with file and line number. No rewriting."""
    if not os.path.exists(facts_file):
        missing.extend(wanted)
        return ""
    numbered = list(enumerate(open(facts_file).read().splitlines(), start=1))
    name = os.path.basename(facts_file)
    lines = []
    for term in wanted:
        hits = [(number, text) for number, text in numbered
                if term.lower() in text.lower() and text.strip()]
        if not hits:
            missing.append(term)
            continue
        for number, text in hits[:4]:
            lines.append(f"{text.strip()}   [{name}:{number}]")
            attached.append(f"fact '{term}' ({name}:{number})")
    if not lines:
        return ""
    return "--- VERIFIED FACTS, quoted from source ---\n" + "\n".join(lines)


# ---------- commands ----------

def command_send(arguments):
    if arguments.from_session:
        message, source = read_last_assistant_text(
            arguments.back, arguments.session_id)
    elif arguments.message:
        if not os.path.exists(arguments.message):
            sys.exit(f"no message file at {arguments.message}")
        message = open(arguments.message).read()
        source = arguments.message
    else:
        sys.exit("pass --from-session or --message")

    # Hash the candidate NOW, before any assembly touches it. Everything after
    # this point is checked against this value.
    candidate_digest = hashlib.sha256(message.encode()).hexdigest()

    # --back is relative and the transcript grows while Claude talks, so the same
    # index can resolve to a different message between a dry run and the send.
    # Observed live during construction. --expect pins it.
    if arguments.expect and not candidate_digest.startswith(arguments.expect):
        sys.exit(f"SELECTION CHANGED: expected {arguments.expect}, "
                 f"selected {candidate_digest[:16]}\n"
                 f"  first line: {message.strip().splitlines()[0][:70]!r}\n"
                 "The transcript moved under you. Re-run the dry run. Nothing sent.")

    attached, missing = [], []
    blocks = []
    if not arguments.no_context:
        if arguments.working_file and arguments.slide:
            neighbours = neighbour_context(arguments.working_file,
                                           int(arguments.slide), attached)
            if neighbours:
                blocks.append(neighbours)
        if arguments.fact:
            facts_file = arguments.facts_file or DEFAULT_FACTS
            if not facts_file:
                sys.exit("--fact needs --facts-file: there is no default facts "
                         "file, because a wrong one would quietly attach facts "
                         "from the wrong project. Nothing sent.")
            facts = fact_context(facts_file, arguments.fact, attached, missing)
            if facts:
                blocks.append(facts)
    if arguments.instruction:
        blocks.append("--- SUMMER'S STEER FOR THIS ROUND ---\n"
                      + arguments.instruction)
        attached.append("Summer's steer")

    transcript = load_transcript(arguments.topic)

    # The exchange goes inside the fence, untouched. Context goes outside it.
    fenced = f"{EXCHANGE_OPEN}\n{message}\n{EXCHANGE_CLOSE}"
    turn = fenced if not blocks else fenced + "\n\n" + "\n\n".join(blocks)

    verify_verbatim(turn, candidate_digest)

    print("Sending to the reviewer:")
    print(f"  exchange: {source} ({len(message)} chars)")
    print(f"  verbatim check: PASS  sha256 {candidate_digest[:16]}")
    print(f"  first line: {message.strip().splitlines()[0][:70]!r}")
    print(f"  attached: {', '.join(attached) if attached else 'nothing'}")
    if missing:
        print(f"  NOT ATTACHED, no match in facts file: {', '.join(missing)}")
    print(f"  history: {len(transcript)} prior message(s)")
    print()

    if arguments.dry_run:
        print("--- dry run, nothing sent. Exact turn below. ---")
        print(turn)
        return

    credential = load_credential()
    if not credential:
        sys.exit(f"no {CREDENTIAL_NAME}. Nothing sent; "
                 f"{arguments.message} is untouched.")

    messages = [{"role": "system", "content": open(SYSTEM_PROMPT_PATH).read()}]
    messages.extend(transcript)
    messages.append({"role": "user", "content": turn})

    # The exact bytes that go over the wire. Hashed here and stored verbatim, so
    # `show --audit` proves what was sent rather than reconstructing a plausible
    # version of it. The credential travels in a header and is never in the body.
    payload_bytes = json.dumps({"model": MODEL, "messages": messages,
                                "usage": {"include": True}}).encode()
    payload_digest = hashlib.sha256(payload_bytes).hexdigest()

    request = urllib.request.Request(
        ENDPOINT, data=payload_bytes,
        headers={"Authorization": f"Bearer {credential}",
                 "Content-Type": "application/json"})
    untouched = "Nothing saved; the selected message is untouched."
    try:
        raw_response = urllib.request.urlopen(request, timeout=900).read().decode()
    except urllib.error.HTTPError as error:
        sys.exit(f"HTTP {error.code}: {error.read().decode()[:400]}\n{untouched}")
    except Exception as error:
        sys.exit(f"failed: {type(error).__name__} {error}\n{untouched}")
    response = json.loads(raw_response)
    if "error" in response:
        sys.exit(f"error: {json.dumps(response['error'])[:400]}\n{untouched}")

    reply = response["choices"][0]["message"]["content"]

    round_number = len(transcript) // 2 + 1
    audit_path = os.path.join(TRANSCRIPT_ROOT,
                              f"{arguments.topic}-audit-{round_number:02d}.json")
    json.dump({
        "topic": arguments.topic,
        "round": round_number,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "provider": "OpenRouter",
        "endpoint": ENDPOINT,
        "model": MODEL,
        "exchange_source": source,
        "relayed_message_sha256": candidate_digest,
        "request_payload_sha256": payload_digest,
        "request_body": payload_bytes.decode(),
        "response_body": raw_response,
        "credentials_in_body": False,
    }, open(audit_path, "w"), indent=1)
    transcript.append({"role": "user", "content": turn})
    transcript.append({"role": "assistant", "content": reply})
    json.dump(transcript, open(transcript_path(arguments.topic), "w"), indent=1)

    reply_path = os.path.join(TRANSCRIPT_ROOT, f"{arguments.topic}-latest-reply.md")
    open(reply_path, "w").write(reply)

    usage = response.get("usage", {}) or {}
    print(f"--- REVIEWER REPLY (openai/gpt-5.2 via OpenRouter, "
          f"${usage.get('cost', 0):.4f}) ---")
    print()
    print(reply)
    print()
    print(f"--- END REPLY. Raw copy: {reply_path}")
    print(f"--- Audit record: {audit_path}")
    print("--- Show this reply to her IN FULL before reacting to it. Bash output "
          "does not reliably reach her.")


def command_show(arguments):
    if arguments.audit:
        pattern = os.path.join(TRANSCRIPT_ROOT, f"{arguments.topic}-audit-*.json")
        records = sorted(glob.glob(pattern))
        if not records:
            sys.exit(f"no audit records for topic '{arguments.topic}'")
        for path in records:
            record = json.load(open(path))
            print(f"===== {os.path.basename(path)} =====")
            for field in ("timestamp", "provider", "model", "endpoint",
                          "exchange_source", "relayed_message_sha256",
                          "request_payload_sha256", "credentials_in_body"):
                print(f"{field}: {record[field]}")
            print("----- EXACT REQUEST BODY SENT -----")
            print(record["request_body"])
            print("----- EXACT RESPONSE BODY RECEIVED -----")
            print(record["response_body"])
            print()
        return
    transcript = load_transcript(arguments.topic)
    if not transcript:
        sys.exit(f"no transcript for topic '{arguments.topic}'")
    for message in transcript:
        who = "SENT" if message["role"] == "user" else "REVIEWER"
        print(f"===== {who} =====")
        print(message["content"])
        print()


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    subcommands = parser.add_subparsers(dest="command", required=True)

    send = subcommands.add_parser("send")
    send.add_argument("--topic", required=True)
    send.add_argument("--message")
    send.add_argument("--from-session", action="store_true",
                      help="take Claude's actual last message from the live "
                           "session transcript instead of a retyped file")
    send.add_argument("--back", type=int, default=1,
                      help="how many assistant messages back to take (1 = most "
                           "recent). Check the preview before sending.")
    send.add_argument("--session-id")
    send.add_argument("--expect",
                      help="sha256 prefix of the intended message, from a dry "
                           "run. Aborts if --back now selects something else.")
    send.add_argument("--working-file")
    send.add_argument("--slide")
    send.add_argument("--fact", action="append")
    send.add_argument("--facts-file")
    send.add_argument("--instruction")
    send.add_argument("--no-context", action="store_true")
    send.add_argument("--dry-run", action="store_true")
    send.set_defaults(function=command_send)

    show = subcommands.add_parser("show")
    show.add_argument("--topic", required=True)
    show.add_argument("--audit", action="store_true",
                      help="print the stored request and response bodies "
                           "verbatim, not a reconstruction")
    show.set_defaults(function=command_show)

    arguments = parser.parse_args()
    arguments.function(arguments)


if __name__ == "__main__":
    main()

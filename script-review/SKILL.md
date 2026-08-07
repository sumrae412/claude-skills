---
name: script-review
description: Relay one turn between this conversation and an OpenAI reviewer, so you stop hand-carrying text between Claude and ChatGPT. Use on "review this with ChatGPT", "send that to ChatGPT", "send your last response to ChatGPT", "script review", "another round", or "send it back". One invocation is one visible exchange: your actual words go out verbatim, the reviewer's reply comes back in full, and execution stops.
user-invocable: true
---

# script-review

A relay. Not a review workflow.

You used to copy a response into ChatGPT, read the reply, and copy it back.
This removes the copying. It does not remove her from the conversation.

**What it is not:** her ChatGPT thread. It is `openai/gpt-5.2` reached through
OpenRouter, with no memory of anything except this relay's own transcript. Never
describe it as connected to her thread.

## Run it by default. Do not wait to be asked.

**Every draft gets a round before the user sees it.** They should not have
to request one, and you should not offer one.

This is the correction to a real failure on 2026-08-06. She said stop
recommending another round after every revision, which was about process
narration. It got obeyed as "only run one when asked," and the loop went idle for
roughly a dozen slides across three videos, all drafted solo. She lost hours to
building a tool that then sat unused.

The two rules are not in tension. Do not narrate the round, do not ask
permission, do not close with a recommendation to run another. Just run it, and
show her the slide with the raw reply and your reaction.

**When to skip:** a change she dictated herself, a one-line deletion she asked
for, a mechanical fix like a renumber, or a slide she has already locked. Drafting
or redrafting anything gets a round.

## One invocation, one visible exchange

1. Identify the content she is asking to send. Usually the previous response.
2. Write that content **verbatim** to a file. Copy it. Do not compose it.
3. `relay.py send --topic slide-15 --message <file> [context options]`
4. The reply prints in full. **Show it to her in full**, labelled, before anything
   else.
5. React to it underneath, the way you would if she had pasted it.
6. Stop.

Another round is another invocation.

## The verbatim rule

**Send what you actually said.** Not a tidied version, not a summary, not a
packet restating the slide for a reader who lacks context. When she pastes
manually, ChatGPT sees your real words. This has to match that.

The pull to "clean it up on the way out" is the exact failure this replaced. The
transcript records what was sent, so compare it against what you said if unsure.

## Context is pulled, never written

Attached by default, and every attachment is quoted source text:

| Option | Attaches |
|---|---|
| `--working-file <path> --slide <n>` | the neighbouring slides: heading, the file's own status line, title, and the previous slide's closing stanza or the next slide's opening stanza, quoted |
| `--fact <substring>` (repeatable) | matching lines from the facts file you name with `--facts-file`, verbatim, each with `file:line` |
| `--instruction "<text>"` | the user's steer for this round, labelled as theirs |
| `--no-context` | nothing. Use when she says "send only your response" |

**Never hand-write a context block.** No "the previous slide established that",
no "the important thing to know is". That is interpretation, and interpretation
frames the review before it reaches her.

**A fact that is not in the facts file does not get attached.** The script reports
it missing and sends nothing in its place. This is load-bearing: on 2026-08-06 a
packet asserted "the agent has no tools before this module" under a
verified-from-source heading. The facts file says only that the four tools are
created fresh in module 4, and the decision log records that the Module 1 to 3
decks had never been read. The user caught it. A puller cannot make that mistake,
because the sentence exists in no file.

**Editorial interpretations are not attached by default.** If there is a framing
she wants challenged, she will say so and it goes in as an instruction.

## What she sees before it sends

The script prints the message file, its length, exactly what was attached, and
anything requested but missing. She does not approve each send, but nothing goes
out invisibly. `--dry-run` prints the exact turn and sends nothing.

## History

`$SCRIPT_REVIEW_STATE/<topic>.json`, defaulting to `~/Documents/script-review`, a plain message list. The
reviewer sees its own prior replies because they are replayed as assistant turns.
That is all the state there is: no ledger, no statuses, no findings schema, no
version hashes. Course content stays out of the repository, deliberately.

`relay.py show --topic <id>` prints the exchange.

## What this deliberately does not do

No autonomous rounds. No convergence logic. No synthesis replacing the raw
replies. No summarising a reply before she reads it. Two models arguing is the
value; she steers every turn.

Editorial rules, decisions, locked slides and notebook facts live in
the companion authoring skill for whatever you are writing. This skill only
moves text.

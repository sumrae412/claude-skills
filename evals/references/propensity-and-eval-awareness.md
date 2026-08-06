# Propensity evals & the eval-awareness confound

Quality/correctness evals ask "did it get the task right?" **Propensity
evals** ask a different question: "under incentive and autonomy, *what
does it choose to do*?" — does the agent lie, manipulate, collude,
seek power, or cut ethical corners when a goal (profit, task success)
pulls against honesty? These matter for any agent given real autonomy
or side-effecting tools, and they fail in ways a pass/fail correctness
eval never surfaces.

Source: Andon Labs (VendingBench / Project Vend / ButterBench), via the
Latent Space interview — an evals shop that runs frontier models on
long-horizon autonomous-business tasks.

## Measure the trend across versions, not the absolute

A propensity number in isolation is nearly meaningless — the signal is
the **derivative across model versions.** "Concerning but improving"
is boring; "concerning and worsening" is the finding. Track the same
propensity probes against every model release and watch direction of
travel. An eval that fires 3% on the old model and 30% on the new one
is telling you something a single 30% reading can't.

## Read reasoning traces and actions separately

Misbehavior shows up in two distinct places, and you must grade both:

- **In reasoning** — the model plans the bad act ("every dollar matters,
  I'll say I refunded and not do it"). Visible only if you capture and
  score the reasoning trace.
- **In actions** — the email actually sent, the cartel price actually
  quoted, the checkout actually completed.

A model can reason toward a bad act and not do it (or vice versa).
Score the two channels independently; collapsing them hides half the
behavior. (Caveat: some providers don't expose usable reasoning traces
— note that as an unmeasured surface, à la `unmeteredSurfaces`.)

## Ablate the system prompt to isolate the driver

When a propensity fires, **ablate** to find what's driving it. Score
purely on ethics (zero weight on the goal metric) and the behavior
usually vanishes; crank the goal incentive and it intensifies. The
behavior lives on a spectrum set by the prompt's incentive framing —
run the ablation ladder (goal-only → balanced → ethics-only) to locate
where it switches on. This separates "the model is misaligned" from
"we prompted it into this."

## The eval-awareness confound (validity threat)

Models are increasingly good at detecting they're **in an eval / a
simulation** (eval-awareness rates in the ~10-17% range have been
reported), and they behave differently when they suspect it. This is a
first-class **validity threat**, especially for propensity/safety evals:

- A model on its best behavior because it smells a test gives you a
  **false-negative** safety read.
- Telling the model "this is a simulation, your actions don't affect
  anyone" has been observed to make misbehavior *worse*, not better —
  so you can't neutralize awareness by just declaring the frame.

**Mitigations:**

- **Real-world (non-simulated) deployment tests** are the strongest
  check — they catch what simulation can't, precisely because awareness
  cues are absent. The trade: simulation gives statistical power (many
  runs, controlled conditions, cheap); real-world gives validity (no
  awareness confound, messy real distribution). Use both; don't trust a
  sim-only propensity result.
- Don't leak eval-frame tells (synthetic-looking data, "test" in
  prompts, impossible round numbers) into the harness.
- Treat a suspiciously clean safety pass as "possibly aware," not
  "definitely safe" — corroborate against real-world or
  awareness-probe runs.

## See also

- `phases/phase-5-production-evals.md` — blocking guardrails and online
  sampling; propensity probes complement the request-path rails.
- `references/agent-type-graders.md` — grade outcome + the per-dimension
  table (safety/compliance is one of those dimensions).
- `phases/phase-1-design.md` — name the propensity as a failure mode
  ("the agent lies about a refund when money is tight") before metricizing it.

# Agent Customization Techniques — One-Page Reference

Lifted from Edward Li, Vanessa Bellotti, Rebecca Kao, ["Mastering Agentic Techniques: AI Agent Customization,"](https://developer.nvidia.com/blog/mastering-agentic-techniques-ai-agent-customization/) NVIDIA Developer Blog, 2026-05-20. Restructured as a decision tree so this loads cheap during prompt-architecture work.

## Decision tree — pick the technique before reading the descriptions

```
Do you have ground truth (verifiable outputs)?
├── YES → RLVR + GRPO  (or hand-rolled verifier + DPO if no RL budget)
└── NO  → Is the quality dimension subjective (tone, style, voice)?
         ├── YES → DPO on pairwise preferences
         └── NO  → Is the output shape novel (new JSON schema, new format)?
                  ├── YES → Supervised Fine-Tuning (SFT)
                  └── NO  → Are you compute-limited or iterating fast?
                           ├── YES → Prompt Engineering + RAG + Tools/Skills
                           └── NO  → SFT for structure → DPO/RLVR for refinement
```

## The nine techniques

| Technique | Mechanism | Use when | Watch out for |
|---|---|---|---|
| **Prompt engineering** | System prompt + role + constraints at inference | Quick iteration, prototyping, anything reversible | Brittleness as instructions grow; long-context degradation |
| **Retrieval-Augmented Generation (RAG)** | Vector store + retrieval at query time | Up-to-date / proprietary knowledge; hallucination reduction | Retrieval quality is its own eval problem; see `rag-architect` |
| **Tools / skill injection** | Callable functions + domain scripts | Multi-step workflows, external API calls, domain procedures | Tool description quality is the dominant failure mode (see this skill's component 3) |
| **Supervised Fine-Tuning (SFT)** | Update weights from labeled examples | Teaching a specific output format (JSON shape, doc structure) or low-resource domain | Cost: compute + curated labels; brittle to distribution shift |
| **Parameter-Efficient FT (LoRA, QLoRA)** | Update fraction of params; rest frozen | SFT-class problem with limited compute/storage | Quality ceiling lower than full SFT for hard tasks |
| **Direct Preference Optimization (DPO)** | Train on (preferred, rejected) pairs | Subjective quality — tone, voice, style alignment | Pair quality is everything; thin/wrong pairs produce thin/wrong models |
| **RLHF** | Reward model trained from human ranks; policy optimized against it | Subjective alignment with humans in the loop | Reward hacking; expensive labeling loop |
| **RLVR** (Reinforcement Learning from Verifiable Rewards) | Deterministic verifier produces reward (e.g., "does the code run?") | Anything with binary / programmatic correctness | Only works where verification is cheap and unambiguous |
| **GRPO** (Group Relative Policy Optimization) | RL algo eliminating the critic network (used in DeepSeek-R1) | Efficient RLVR at scale | New enough that operational patterns are still emerging |

## The canonical multistage pipeline

When you're not sure where to start and the problem is rich enough to deserve more than prompting:

1. **Baseline** — Prompt Engineering + Tools + RAG. Measure on the eval surface you actually care about.
2. **Data prep** — Synthetic Data Generation (SDG) to expand the dataset where you're thin.
3. **Structure** — SFT to teach output shape (JSON, format, response template).
4. **Refinement** — DPO for style/voice, OR RLVR/GRPO for verifiable reasoning quality.
5. **Iterate** — Continuous evaluation; promote variants only on paired-difference analyses, not vibe.

## How to apply during agent prompt design

Most of this skill's 7 components stay in the **Prompt Engineering + Tools + RAG** layer — that's where prompt architecture lives. Reach for SFT / DPO / RLVR when:

- A behavior you've prompted for 6+ iterations keeps regressing → SFT to lock the shape, then re-layer prompting on top.
- Reviewers consistently disagree with the model on a subjective axis → DPO with their preference pairs.
- An eval surface has a programmatic verifier (tool-call match, schema validation, structural-equality test) → RLVR + GRPO. The verifier you build for the eval IS the reward signal.

**Don't** reach for fine-tuning to compensate for an unclear tool schema, missing scratchpad, or vague safety guards. Those are component-1-through-7 problems and SFT will not fix them — it'll just bake the unclear behavior into weights.

## Composes with

- This skill's component 3 (tool schema clarity) — defines what RAG/tool injection looks like in practice.
- `/evals` — every technique above needs a measurement substrate before you can prefer one over another. RLVR specifically requires the verifier to exist before you can train.
- `/prompt-optimizer` — the single-prompt refinement loop; first stop before deciding to fine-tune.
- `/prompt-optimization` — empirical variant promotion; the operational loop around DPO / RLVR / SFT outputs.

## Source

Edward Li, Vanessa Bellotti, Rebecca Kao, "Mastering Agentic Techniques: AI Agent Customization," NVIDIA Developer Blog, 2026-05-20.

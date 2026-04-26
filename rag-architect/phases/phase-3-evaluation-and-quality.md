# Phase 3: Evaluation and Quality

Load `../references/rag_evaluation_framework.md` before running this
phase.

## Goal

Define how the system will be evaluated for relevance, faithfulness, and
end-to-end usefulness.

## Ask

- What failure mode matters most: hallucination, low recall, latency, or
  instability?
- What gold questions or benchmark tasks exist?
- How will source grounding be verified?

## Evaluate

- faithfulness
- context relevance
- answer relevance
- precision / recall / MRR / NDCG
- end-to-end correctness and completeness

Use `retrieval_evaluator.py` when structured retrieval testing is useful.

## Output

Evaluation plan with metrics, test sets, thresholds, and iteration order.

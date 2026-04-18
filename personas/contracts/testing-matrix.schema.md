# Contract: `$testing_matrix`

Output of Phase 3. The cross-product of personas × testing styles × flows, pruned to a cost budget.

## Schema (JSON)

```json
{
  "run_id": "...",
  "app_name": "...",
  "app_kind": "gui | api | cli | chatbot",
  "cells": [
    {
      "cell_id": "c001",
      "persona_id": "p01",
      "flow_name": "send_document_for_signature",
      "testing_style": {
        "mindset": "sequential | divergent",
        "strategy": "click | core_function | input_oriented",
        "habit": "valid_short | invalid"
      },
      "max_steps": 10
    }
  ],
  "matrix_metadata": {
    "full_matrix_size": 450,
    "sampled_size": 50,
    "sampling_method": "stratified_by_axis_bucket",
    "seed": 12345
  }
}
```

## Sampling

- **GUI apps:** PersonaTester 3D (2×3×2 = 12 combinations). Stratified subsample to `testing_styles_per_persona` (default 2). Stratification: each axis value appears for ~equal numbers of personas; within a persona, the selected styles differ on ≥2 of 3 axes.
- **API / CLI / chatbot apps:** no PersonaTester layer. `testing_style = null`. One cell per (persona, flow).

## Budget guard

If `|cells| > 100`, Phase 3 warns the user before proceeding and offers to cap via random sample.

## Persistence

Written to `docs/persona-eval/<app>/<run-id>/testing-matrix.json`.

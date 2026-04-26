# Phase 3: Trace Analysis and Challengers

## Goal

Use trace sampling to explain why a variant loses, then draft a better
challenger.

## Process

- sample traces from the losing variant
- note the earliest observable failure per trace
- group failures into buckets
- target the top 2-3 buckets in the challenger rewrite
- present the challenger for approval before activation

## Rules

- skip deep trace review if the sample size is too small
- do not confuse symptom buckets with root-cause certainty

## Output

Failure-bucket summary plus challenger prompt proposal.

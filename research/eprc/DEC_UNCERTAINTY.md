# Uncertainty-aware Differential Execution Contracts

A single finite-difference Jacobian is not sufficient evidence for a deployment claim.

DEC therefore requires repeated intervention assays before asserting that two local physical contracts are equivalent or different.

## Empirical uncertainty envelope

Given independently repeated physical Jacobian estimates J_1 ... J_R:

1. form the center Jacobian as their mean;
2. compute DEC signature distance from each replicate to the center;
3. retain the empirical q95 distance as a robustness radius.

This q95 radius is explicitly **not** called a formal statistical confidence interval. Its purpose is to make instability visible and to force a three-way decision:

- EQUIVALENT;
- DIFFERENT;
- INCONCLUSIVE.

For two stable estimates A and B with center distance d and radii r_A, r_B:

- equivalence is certified only if d + r_A + r_B <= tau_eq;
- difference is certified only if max(0, d - r_A - r_B) >= tau_diff;
- otherwise the comparison is INCONCLUSIVE.

## Why this matters

This prevents a visually attractive single-seed DEC match from becoming a paper claim. It also gives cross-policy experiments a principled way to retain ambiguous cases instead of threshold-tuning them away.

## Required policy experiment

Each reported policy/controller condition must use at least five independently repeated intervention/probe realizations. The main cross-policy AUC analysis should operate on uncertainty-qualified pairs; unstable pairs remain visible and count against coverage.

## Kill criterion

If most real policy conditions become INCONCLUSIVE at reasonable intervention budgets, DEC is too unstable for the proposed runtime use and the method must be narrowed.
# Certificate-Directed Counterfactual Probing (CDP)

## Motivation

Robust CRG can return INCONCLUSIVE. A runtime method should not respond by reconstructing the entire Jacobian uniformly if only one uncertainty direction blocks the current repair certificate.

## Information geometry

Maintain a positive-definite support-space information matrix V and an uncertainty assumption

  ||(G_true-G_hat) x||_2 <= beta sqrt(x^T V^{-1} x).

For a current candidate repair xi, adding probe z changes V to V + z z^T. Sherman-Morrison gives the exact reduction in xi^T V^{-1} xi:

  Delta(xi,z) = (xi^T V^{-1} z)^2 / (1 + z^T V^{-1} z).

Among an admissible candidate probe set, CDP selects the probe with largest Delta when the repair certificate is blocked by candidate-direction uncertainty.

When the global impossibility certificate is blocked instead, the least-observed eigenvector of V is the natural one-step E-optimal probe because the uniform repair-set uncertainty is beta*r/sqrt(lambda_min(V)).

## What is and is not claimed

Optimal experimental design, Sherman-Morrison updates, and E-optimal probing are established tools. The research claim is not their invention.

The narrower question is whether choosing physical counterfactual interventions to resolve a specific repairability certificate reduces the number of frozen-policy queries needed to reach a correct REPAIR / IMPOSSIBLE decision.

## Frozen comparison

On the same states and disturbance bank compare query count to first non-INCONCLUSIVE decision for:

1. coordinate finite differences;
2. random Gaussian directions;
3. Rademacher/coded interventions;
4. generic D/E-optimal probing;
5. certificate-directed probing.

Report certificate error rate, median/90th-percentile query count, unresolved fraction at a fixed query budget, and closed-loop false accepts. Do not tune the probe strategy on rollout outcomes.

## Kill criterion

If CDP does not reduce certificate query cost over generic design baselines at matched error/coverage, keep robust CRG and drop CDP as a main contribution.
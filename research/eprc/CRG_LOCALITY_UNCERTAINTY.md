# Empirical locality uncertainty for robust CRG

Repeated policy queries can be perfectly deterministic while the local
finite-difference model is still a poor approximation away from the probe
scale. RNG repeatability must therefore not be treated as the whole physical
map uncertainty.

For a fine-probe map estimate G_f and a coarser independently estimated map
G_c, the public capsule now records two empirical terms:

    epsilon_rng   = max_i ||G_f^(i) - mean(G_f)||_2
    epsilon_scale = ||G_c - mean(G_f)||_2

and uses

    epsilon_G = max(epsilon_rng, epsilon_scale)

inside robust CRG.

This is intentionally conservative and explicitly labeled an empirical
locality envelope rather than a confidence interval.

## Why this matters

A deterministic frozen policy may have epsilon_rng = 0 while still showing
large finite-difference curvature. Without the scale term, a robust certificate
could be falsely overconfident simply because the policy has no sampling noise.

## Kill / refinement criterion

If scale drift is too conservative to predict held-out repair outcomes, replace
the max envelope with a calibrated locality model using preregistered held-out
directions. Do not shrink epsilon_G after observing success/failure labels.

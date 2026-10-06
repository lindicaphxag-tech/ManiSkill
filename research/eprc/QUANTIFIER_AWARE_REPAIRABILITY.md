# Quantifier-aware structured repairability

## The runtime mistake

Under an uncertain local physical map set G, these statements are not equivalent:

    for every G, there exists a repair xi_G

and

    there exists one repair xi that works for every G.

The first statement can hold while execution is still unjustified: the robot
must send one action before it knows which local response map is the correct one.

The runtime-valid robust requirement is therefore:

    exists xi, for every G in G:
        ||G xi - d|| <= tau.

This quantifier order becomes important exactly when multi-scale or repeated
counterfactual probes disagree.

## Why the VQ-BeT negative matters

The frozen prospective locality run 37460144187 observed:

    D1 = 3.0126126299
    D2 = 3.4499882450
    D2 / D1 = 1.1451814982 > 0.75

with zero stochastic radius and zero same-scale center shift.

The first-order map therefore failed its pre-registered contraction gate.
This branch does not rescue that state by pretending the observed maps are a
valid uncertainty distribution. Instead, it studies the more general runtime
logic needed *when* multiple admissible local-map hypotheses are justified.

## Structured certificate

For a finite admissible map set {G_i}, the implementation is deliberately
fail-closed:

- CERTIFIED_REPAIR only if one candidate xi independently verifies against
  every G_i;
- CERTIFIED_IMPOSSIBLE if at least one admissible G_i carries a dual separation
  witness proving that even its best local repair exceeds tolerance;
- INCONCLUSIVE otherwise.

A particularly important INCONCLUSIVE case is the **quantifier gap**:

    each G_i is individually repairable
    but
    no common xi is certified.

The regression fixture G1=+1, G2=-1, d=0.5 makes this explicit: each map has an
exact repair, but the repairs have opposite signs.

## Novelty boundary

Robust optimization, min-max control, convex separation, and quantifier order are
not new mathematics.

The research claim under test is narrower:

> runtime repair of a frozen learned robot policy should be authorized against
> the intervention-supported *set of physical response hypotheses*, with
> evidence provenance and quantifier order preserved, rather than collapsing
> disagreement into a point Jacobian or treating per-model feasibility as a
> common executable repair.

## Promotion gate

This component becomes part of the flagship only if, on the frozen multi-state
policy bank, structured uncertainty gives a better calibration/coverage tradeoff
than the current scalar operator-norm envelope without increasing false accepts.

If it merely changes abstention rates without predictive benefit, keep the
simpler robust CRG.

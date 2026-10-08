# CRG v0.2 — Representation-invariant linear action authority

CRG v0.1 used axis-aligned action bounds to shrink the counterfactual support trust region. That is useful but not invariant to a general invertible action-coordinate change because an axis-aligned box becomes a rotated polytope.

v0.2 replaces the box-specific authority gate with a general local linear action authority:

    H a <= h.

For a nominal action a0, CASJ action-support Jacobian J, and support perturbation ||xi||_2 <= r:

    H_i(a0 + J xi) <= H_i a0 + r ||H_i J||_2.

Hence the largest centered support ball guaranteed to satisfy all linear action constraints is

    r_authority = min_i (h_i - H_i a0) / ||H_i J||_2,

intersected with the independent CASJ trust radius.

## Why this matters

For an arbitrary locally invertible action chart a' = R a:

    J' = R J,
    C' = C R^{-1},
    H' = H R^{-1},
    a0' = R a0.

Then

    H' J' = H J,
    H' a0' = H a0,
    C' J' = C J.

Therefore the certified support radius, policy-consistent physical repair set, separation certificate, and repaired physical command are all invariant to the action chart when controller semantics and authority are transformed consistently.

This is stronger than the v0.1 diagonal-scaling test and gives a precise meaning to representation-invariant repairability.

## Constructive action surgery

The solver now returns all of:

- support-space counterfactual delta xi;
- executable action correction J xi;
- repaired action a0 + J xi;
- physical correction C J xi;
- residual and separating-hyperplane margin.

The correction is deliberately restricted to the frozen policy's intervention-identified response image. A controller may have physical authority in a direction that the frozen policy has never exhibited under the current support interventions; CRG does not silently use that extra controller freedom.

## Novelty boundary

Linear constraints, trust regions, pseudoinverses, support functions, and controllability/manipulability geometry are classical and are not claimed.

The research claim remains the policy-conditioned composition: black-box physical support intervention -> action-support differential -> semantic lift -> action-authority intersection -> constructive runtime repair or impossibility certificate.

## Strong falsifier

If unrestricted controller-space correction performs as well as or better than the support-restricted CRG repair on held-out disturbances without increasing false accepts, then the policy-consistency restriction is not empirically justified.
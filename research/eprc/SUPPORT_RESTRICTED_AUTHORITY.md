# Support-restricted authority: exact transport without global full rank

## Problem

The current authority gate is intentionally conservative: if a controller loses any local rank, exact transport is rejected. That is too strong for task-conditioned embodied execution.

A controller can be globally underactuated yet still possess every physical direction required by the current support-induced disturbance.

## Criterion

Let J_phys be the source Differential Execution Contract for the current support perturbations, and let L_t be the target controller's local action-to-physical Jacobian.

An exact local transport exists iff:

  Im(J_phys) subseteq Im(L_t).

Equivalently:

  (I - L_t L_t^+) J_phys = 0.

When this holds, the minimum-norm target action-support response is:

  J_action,target = L_t^+ J_phys.

This criterion remains meaningful when L_t is rectangular, redundant, or globally rank deficient.

## Research consequence

Authority is not a scalar property of a controller. It is conditional on the physical response subspace required by the current policy/support interaction.

This creates three distinct cases:

1. global full rank and support-restricted exact -> ordinary exact transport;
2. global rank loss but support-restricted exact -> exact transport is still admissible for the current disturbance;
3. support response leaves target authority image -> exact transport must be rejected.

## Novelty discipline

The pseudoinverse/projector criterion is standard linear algebra and is not claimed as new mathematics.

The EPRC/DEC contribution is using it as a runtime physical-authority certificate tied to intervention-identified support response, preventing both overly permissive transport and overly conservative rejection.

## Decisive empirical prediction

Support-restricted projection residual should predict held-out transport success better than a global rank-loss flag or action-norm clipping flag.

If not, this authority refinement should be removed from the method.
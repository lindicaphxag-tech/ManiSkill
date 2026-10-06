# Pre-registered support-restricted authority gate

The new authority refinement is useful only if it predicts real transport success better than cheap baselines.

## Frozen predictors

1. support-restricted projection residual: ||(I - L L^+) J_phys|| / ||J_phys||;
2. global controller full-rank flag;
3. clipping/saturation flag.

## Target

Whether the attempted exact transport succeeds on a held-out disturbance according to canonical physical-command error and downstream execution.

## Primary gate

- at least 20 held-out trials;
- both successes and failures must occur;
- projection-residual AUC >= 0.75;
- projection-residual AUC exceeds both frozen baselines by at least 0.05.

If the gate fails, support-restricted authority remains an algebraic observation but is removed as an empirical EPRC claim.

## Why this matters

A global rank-loss flag is intentionally too conservative: it rejects controllers that lack irrelevant physical directions. A clipping flag is too local to tell whether the clipped/lost direction is actually required by the current support response. The projection residual asks the correct task-conditioned question.
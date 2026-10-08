# Chunk Repairability Tube

## Why

Action-chunk policies execute a temporally coupled object, not independent single-step actions. Bounds, step discontinuity, jerk, queue provenance and previous executed action all constrain which repairs are actually executable.

LeRobot's full-chunk safety discussion already motivates sequence-level checks. The contribution investigated here is narrower: intersect those temporal constraints with the intervention-identified frozen-policy repair image instead of clamping arbitrary chunk coordinates.

## Temporal authority

Flatten a horizon-H action chunk a into one vector. Build linear authority A a <= b from:

- per-step action bounds;
- first-step continuity to the previously executed action;
- inter-step delta limits;
- jerk limits using the previous executed delta.

For chunk support Jacobian J_H and canonical physical lift C_H, the policy-consistent repair set is

  R_H = { C_H J_H xi : ||xi|| <= r, A(a0 + J_H xi) <= b }.

Robust CRG shrinks r for Jacobian uncertainty and returns CERTIFIED_REPAIR, CERTIFIED_IMPOSSIBLE, or INCONCLUSIVE.

## Distinction from ordinary chunk safety

A generic chunk safety layer asks whether a proposed chunk violates bounds/jerk and may clamp it.

Chunk CRG asks a different question: among corrections that the frozen policy's measured local response can actually support, is there a temporally admissible repair for this physical target? If not, it returns an impossibility or abstention certificate rather than silently manufacturing a controller-space action.

## External path

This object is designed to fit a policy-independent full-chunk ProcessorStep once LeRobot's processing architecture provides the insertion boundary discussed around #4241/#4592. Compatibility is not adoption.

## Kill criterion

If per-step CRG plus ordinary chunk clamping matches full chunk-CRG on stale/delayed/discontinuous action-chunk disturbances, temporal repairability should not be a main contribution.
# Target-memory feasibility response — exploratory follow-up

This is a deliberately **development-set** pilot designed AFTER seeing
the four-seed frozen PPO target-memory failure in
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37717254769.
It is NOT an independent holdout, and no success-rate significance or
L8/L9 claim is licensed.

## Causal motivation

The same frozen third-party PPO weights, 42-dimensional trained policy
observations and runtime 7-dimensional target pose state are present.
The exact compiler refused:
- seed 42 at step 5, required amplitude 1.423;
- seed 429 at step 5, required amplitude 1.621.

Even known previous-target memory cannot make an action within a fixed
native action-space bound when the physical goal lies beyond that bound.

## Four concurrent options (same frozen checkpoint, same four development seeds)

1. Native source `pd_ee_delta_pose`.
2. Target `pd_ee_target_delta_pose` with live-target exact rewrite, **fail
   closed** if beyond bounds.
3. Same target controller with *explicit non-exact projection*:
   physical goal is expressed relative to previous target, but the
   native translational vector is clamped into [-1,+1] per dimension
   and rotational native vector is projected to the unit Euclidean ball.
   Every approximate step and demanded original amplitude is logged.
4. Naive target direct-copy policy action.

Scripts, CPU CI and machine-readable episode-level logs:
https://github.com/lindicaphxag-tech/ManiSkill/tree/validation/frozen-ppo-memory-feasibility-fallback-20261008

**Crucial distinction:** option (3) is NOT an exact action compiler
and no contract certificate may call it equivalent. It is a *bounded
approximate execution fallback*. If it produces a success, we must
report original target residual/error, number of clipped steps and
whether the source policy itself succeeded. A single new success does
not establish a safe or optimal fallback.

## Hard boundaries

- Four development seeds 42,270,429,2026, reused knowingly — not a
  holdout; baseline prior outcome known to model developer.
- PhysX CPU PickCube/Panda, 50 steps each, same published ActionShift
  checkpoint, no fine-tuning; policy computes own observations after
  explicit target-controller memory removal to preserve source ABI.
- All refusal errors and fallback steps remain visible in JSON.
- If projective approximation fails or regresses on seeds, record it
  rather than selecting post hoc thresholds to game the result.
- Independent future held-out scenes, task diversity and dynamic
  intervention bounds are required for any publication-grade claims.

This file was committed before inspecting the new pilot CI result.

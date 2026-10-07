# Bounded SO(3) action compiler

This artifact studies a specific controller-semantic gap: a valid target
orientation on SO(3) may not fit in one normalized Euler-action step because
the production EE-pose controller radially clips its normalized three-axis
rotation vector. Componentwise clipping changes the represented rotation.

## Method

Given a target quaternion `q`, take its principal rotation vector `v`, then
search `N = 1, 2, ...` for the first geodesic increment `q_step = Exp(v/N)`
whose production uppercase-XYZ Euler representation `e` satisfies
`||e / action_scale||_2 <= 1`. Emit that same normalized command `e/action_scale`
for `N` controller steps. The scale argument is explicit because the current
controller multiplies by `rot_lower` (negative in shipped Panda configurations)
while the proposed fix in ManiSkill PR #1472 uses `rot_upper` (positive).

Repeating one group element reconstructs the target exactly at the controller
target level: `(q_step)^N = q`. Ascending search returns the smallest number of
steps among equal subdivisions of the principal geodesic. It does not establish
global time optimality, IK feasibility, collision safety, dynamic tracking, or
task success.

## Reproduce the numerical characterization

```bash
python benchmark.py
```

The fixed-seed experiment samples Haar-uniform rotations and compares a single
controller step with the exact uniform-subdivision compiler under the current
negative `rot_lower`, the positive `rot_upper` proposed in #1472, and one
asymmetric scale. Results include the one-step feasibility/error distribution,
number of compiled steps, and maximum quaternion endpoint error. This is a
kinematic controller-target study; the separate Kaggle PegInsertionSide assay
is needed for policy-level evidence.

## Current numerical result

With seed `20261008` and 20,000 Haar-uniform target rotations, production
uppercase-XYZ matrix parity was checked on a separate 1,000-angle sweep; the
maximum absolute matrix-entry difference was `5.6e-16`. At symmetric `0.1 rad`
per-axis scales, the direct single-step action was feasible for none of these
full-range targets; the exact compiler used a median of 24 equal steps (95th
percentile 31, maximum 32), with worst endpoint error `1.74e-15 rad`. With
asymmetric scales `[0.10, 0.08, 0.12] rad`, the median was 24 steps, 95th
percentile 34, maximum 40, and worst endpoint error `1.85e-15 rad`.

These are deliberately broad SO(3) targets, not empirical policy action
statistics. They characterize geometric reconstruction and action-budget cost;
they do not establish practical task benefit. A next validity gate is replaying
real policy/demo delta rotations through the production controller and measuring
IK, contact, and task success.

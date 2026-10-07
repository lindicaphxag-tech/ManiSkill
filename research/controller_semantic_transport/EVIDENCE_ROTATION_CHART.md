# Frozen rotation-chart evidence

This evidence is intentionally independent of policy training and simulator
dynamics.  It isolates one representation question raised by ManiSkill #1138
and PR #1495:

> What happens if a rotation is converted to an axis-angle / rotation-vector
> coordinate, but the receiving controller interprets the same three numbers
> as XYZ Euler coordinates?

## Frozen protocol

- seed: 20261006
- samples: 20,000
- desired XYZ Euler components: i.i.d. Uniform[-0.8, 0.8] radians
- desired rotation: Rx(x) Ry(y) Rz(z), matching ManiSkill's XYZ convention
- historical encoding: convert desired rotation matrix to a rotation vector
- historical decode: interpret that rotation vector as XYZ Euler
- metric: SO(3) geodesic angle between intended and decoded rotations

Run:

    python research/controller_semantic_transport/tools/rotation_chart_sweep.py

## Frozen result

The fixed protocol yields approximately:

| statistic | geodesic error |
| --- | ---: |
| mean | 0.146 rad |
| median | 0.135 rad |
| p90 | 0.265 rad |
| p95 | 0.306 rad |
| p99 | 0.407 rad |
| maximum | 0.540 rad |
| fraction > 0.05 rad | 85.0% |
| fraction > 0.10 rad | 64.5% |
| fraction > 0.20 rad | 26.2% |

0.135 rad is about 7.7 degrees and 0.540 rad is about 30.9 degrees.

These numbers are not a task-success claim. They establish only that the two
three-parameter charts are not interchangeable for generic compound rotations.

## Two-layer validation matrix

PR #1495 (converter chart) and upstream PR #1472 (controller rotation sign)
address independent semantic layers.  Task-level validation should therefore
use a 2x2 factorial design:

| converter | controller sign | purpose |
| --- | --- | --- |
| historical axis-angle-as-Euler | historical negative sign | original baseline |
| fixed XYZ Euler | historical negative sign | isolate representation fix |
| historical axis-angle-as-Euler | sign fixed | isolate sign fix |
| fixed XYZ Euler | sign fixed | composed corrected contract |

The same demos, seed set, training budget and evaluation episodes must be used
for all four cells.  A representation claim should not borrow gains caused by
the sign patch, and vice versa.

## Promotion rule

The deterministic SO(3) evidence supports a representation-contract bug.
It does not promote PR #1495 to a policy-performance result.

That requires the maintainer-requested PegInsertionSide Diffusion Policy
experiment or an equivalent frozen task-level evaluation.

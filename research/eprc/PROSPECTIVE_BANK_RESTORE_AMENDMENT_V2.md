# Prospective-bank environment protocol amendment — 2026-10-08

## Frozen scientific design unchanged

The original 20-case bank was frozen before running:
- reset states: `17,29,43,59,71,89,101,131,151,181`;
- held-out disturbances A and B, source and checkpoint revisions;
- support scale, perturbation epsilon and randomness seeds;
- DEC correlation threshold and margin over preregistered baselines.

Those constants are **not modified**. Unstable states remain in the output.

## Why v1 execution failed

The first 10-state run completed 7 reset states and failed on three others
(29/43/131) during `restore_snapshot` readback. All three failures precede
prospective scoring, so **there is no valid 20-case science result** from v1.

Failing runs raised on `block_position` because Python/NumPy float64
`np.array_equal` found a 1–2 ULP coordinate difference after round-tripping
through the Pymunk physics engine. The diagnostic retry recorded:

| Seed | Block position requested | Observed | Max absolute drift |
| --- | --- | --- | --- |
| 29 | (288.4250657450654, 249.32821179243305) | (288.4250657450654, 249.32821179243302) | ~2.84e-14 |
| 43 | (214.3517050599082, 202.6441123136045) | (214.3517050599082, 202.64411231360452) | ~2.84e-14 |
| 131 | (200.07948724792587, 280.9254845595014) | (200.0794872479259, 280.92548455950146) | ~5.68e-14 |

These values show float readback drift, not evidence of a meaningful robot
displacement. They do **not** by themselves establish that every internal
physics-body field, collision cache or rendered pixel is identical.

## Declared protocol change (v1 -> v2)

The old `reset-fresh-space-exact-readback-v1` requires bitwise equality for all
snapshot coordinates. The amended
`reset-fresh-space-block-position-4ulp-v2` permits at most four
position-dependent IEEE 754 float64 ULPs of readback difference for
**block_position only**. The restored agent position, velocities, block
angle, block velocity and angular velocity remain strictly equal.

The check is per coordinate, rejects NaN/inf and shape mismatches, and uses
neither a generic relative tolerance nor a pixel-sized allowance. Any larger
difference still rejects the sample and leaves the bank incomplete.

A regression includes all three original failing readbacks and rejects
larger shifts and >4 ULP changes.

## Scientific-status discipline

This is a **post-run environment protocol amendment**. Although the original
state bank and scoring thresholds remain frozen, v2 results must not be
reported as an entirely untouched preregistered v1 experiment.

The first v1 run, all failures, and this amendment remain public. On v2, count
all ten states and twenty pairs; do not drop or resample a failed state.
If v2 is unable to recover all states, record an incomplete primary gate
rather than reporting correlation on a convenient subset.

A complete v2 run may provide useful *amended-protocol prospective evidence*.
A genuinely fresh independent preregistered confirmatory run is still needed
for any strong generalized claim.

# Paired frozen-policy result — Diffusion vs VQ-BeT PushT — 2026-10-06

This record freezes the first successful **same-runner, same-runtime, same-physical-protocol**
comparison between two official frozen LeRobot policy families.

Workflow:

- run: `37471301545`
- paired artifact: `eprc-paired-cross-policy-pusht`
- artifact id: `11418336019`
- artifact ZIP SHA-256:
  `247bae02c6f6d71c923eb4ba0a294b9ec974c2404ca970ff1240b574914bf048`

Both policies were probed under:

- the same LeRobot runtime commit:
  `3c0a209f9fac4d2a57617e686a7f2a2309144ba2`;
- the same PushT reset seed: `17`;
- the same exact-state restoration protocol;
- the same support coordinates: block x / y / theta;
- the same fine/coarse physical perturbations;
- the same held-out disturbance:
  `[10 px, -6 px, 0.35 rad]`;
- the same CPU runner.

## Policy A — Diffusion PushT

Checkpoint:

`lerobot/diffusion_pusht@d3d143b0342488252497853815b27ce3c0384c6b`

Observed:

- paired replay max error: **0.0**;
- five-seed DEC q95 radius: **3.8257607408**;
- DEC stability gate: **failed**;
- stochastic local-map radius: **21.4347152645**;
- finite-difference scale-drift radius: **10.2151530418**;
- dominant evidence bottleneck: **STOCHASTIC_LIMITED**;
- nominal held-out residual: **4.5876593192**;
- robust CRG decision: **INCONCLUSIVE**.

The same state/protocol therefore does not justify a stable single DEC estimate
for this stochastic policy under the frozen five-seed budget.

## Policy B — VQ-BeT PushT

Checkpoint:

`lerobot/vqbet_pusht@390e5e4c079c880b22e873dad53ecfac706bc78a`

Observed:

- paired replay max error: **0.0**;
- five-seed DEC q95 radius: **0.0**;
- DEC stability gate: **passed**;
- stochastic local-map radius: **0.0**;
- finite-difference scale-drift radius: **3.0126126299**;
- dominant evidence bottleneck: **LOCALITY_LIMITED**;
- nominal held-out residual: **4.4226541813**;
- robust CRG decision: **INCONCLUSIVE**.

The policy is repeatable, but the first-order local physical model is not
supported by the scale-validity gate.

## Paired adjudication

The fail-closed cross-policy adjudicator produced:

- same frozen protocol: **yes**;
- reports comparable: **yes**;
- DEC signature distance: **0.2587364806**;
- held-out response relative distance: **1.5301942270**;
- robust CRG decisions agree: **yes** (both `INCONCLUSIVE`);
- both DEC stability gates pass: **no**.

Therefore this experiment does **not** support a claim that two policy families
share the same numerical DEC or held-out response.

The stronger surviving observation is different:

> under the same physical repair request and the same intervention protocol,
> two frozen policies can reach the same fail-closed runtime decision for
> different evidence reasons.

Diffusion is evidence-limited primarily by stochastic variation. VQ-BeT is
evidence-limited primarily by locality / scale mismatch.

## Claim update

The flagship should **not** require cross-policy numerical contract equality.

The cross-policy claim is narrowed to:

> the same physical-repairability framework can express and diagnose distinct
> evidence bottlenecks across policy families without forcing a repair when the
> local evidence is unsupported.

A future multi-state benchmark must test whether bottleneck-conditioned
evidence allocation improves time-to-terminal-certificate relative to a fixed
probing strategy. A single paired state is only a mechanism witness.

## External evidence boundary

This is owner-run evidence and counts as **zero external replication/adoption**.

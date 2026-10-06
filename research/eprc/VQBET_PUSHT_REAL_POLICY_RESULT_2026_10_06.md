# Frozen VQ-BeT PushT evidence — 2026-10-06

This record freezes the first fully green real-policy EPRC/DEC/CRG run.

## Provenance

- policy: `lerobot/vqbet_pusht`
- model revision: `390e5e4c079c880b22e873dad53ecfac706bc78a`
- LeRobot training runtime: `3c0a209f9fac4d2a57617e686a7f2a2309144ba2`
- branch head at the green run: `49f7bae973f50f8f166076430017f7857d3f778e`
- current-policy workflow: run **37456801175**
- historical-native workflow: run **37456801100**
- LeRobot plugin compatibility: run **37456801328**
- contract capsule: run **37456801120**

All four workflows completed successfully.

## Frozen physical intervention protocol

Same PushT reset state, exact state restore, and block support coordinates:

[
s=(x_{block},y_{block},	heta_{block}).
]

The metric-whitened support scale is:

- 16 px in block x;
- 16 px in block y;
- 0.08 rad in block rotation.

Fine central probes use `[4 px, 4 px, 0.02 rad]`; coarse locality probes use
`[8 px, 8 px, 0.04 rad]`.

The held-out disturbance was frozen as:

`[+10 px, -6 px, +0.35 rad]`.

## Real frozen-policy observations

Five RNG-seed repeats produced identical first-step DEC signatures:

- all 10 pairwise DEC distances: **0.0**
- q95 seed DEC radius: **0.0**
- preprocessing repeat error: **0.0**
- paired policy repeat error: **0.0**

First action-step support Jacobian, in action per physical support unit:

```text
[[ 0.1599884,  0.0066643,   2.6519775],
 [ 0.4089317, -0.0629921, -14.7735596]]
```

This is evidence of deterministic local response under paired randomness. It is
not evidence that the local map is linear over a larger neighborhood.

## The important negative result

For the held-out disturbance, the frozen robust CRG decision is:

`INCONCLUSIVE`.

- nominal residual: **4.42265**
- allowed residual tolerance: **4.0**
- best-case residual lower bound: **2.91635**
- worst-case residual upper bound: **5.92896**
- robust support radius: **0.5**
- observed operator uncertainty: **3.01261**

The uncertainty decomposition is the key mechanism result:

- RNG stochastic radius: **0.0**
- finite-difference scale-drift radius: **3.01261**

So perfect paired-repeat stability does **not** imply that the local derivative
is valid at the held-out scale. The blocker is locality/curvature, not policy RNG.

This result is deliberately retained rather than tuning the tolerance until a
repair certificate appears.

## AMRC consequence

The request-conditioned active planner proposed six additional symmetric support
probes, i.e. **12 additional frozen-policy evaluations**, but its information-only
projection remained `INCONCLUSIVE` at that frozen budget.

Those probes were **planned, not executed**, and therefore are not counted as
new evidence.

The evidence-action router then applies a stricter provenance rule. Because
finite-difference scale drift (**3.01261**) dominates RNG stochasticity (**0.0**)
and the information-only AMRC plan remains inconclusive, the run is classified
as:

`LOCALITY_LIMITED`

with **additional same-scale queries not authorized** as evidence for shrinking
the locality envelope. The next admissible experiment is a smaller symmetric
physical perturbation / smaller trust region (or an explicitly validated
higher-order local model), not simply more directional samples.

## What this establishes

This run supports three narrower claims:

1. physical support response can be measured repeatably from an official frozen
   LeRobot policy;
2. robust CRG distinguishes stochastic repeatability from finite-scale locality;
3. the runtime can abstain rather than converting a stable Jacobian into an
   unjustified repair.

It does **not** yet establish cross-policy transfer, closed-loop recovery gain,
third-party replication, or external adoption.

The next prospective gate uses the official `lerobot/diffusion_pusht`
checkpoint under the same intervention protocol.

# Frozen VQ-BeT PushT witness — 2026-10-06

This is a **negative but result-bearing** real frozen-policy witness.

It is intentionally retained because it falsifies a weaker version of the
research claim: deterministic black-box support derivatives are **not**
automatically valid repair models.

## Frozen provenance

- policy: `lerobot/vqbet_pusht`
- checkpoint revision: `390e5e4c079c880b22e873dad53ecfac706bc78a`
- LeRobot training-runtime commit:
  `3c0a209f9fac4d2a57617e686a7f2a2309144ba2`
- task/runtime: PushT, exact-state restore
- reset seed: `17`
- fine probe: `[4 px, 4 px, 0.02 rad]`
- coarse probe: `[8 px, 8 px, 0.04 rad]`
- held-out disturbance: `[10 px, -6 px, 0.35 rad]`

Public runs:

- base real-policy probe:
  https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37460144227
- prospective locality-refinement probe:
  https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37460144187

## What succeeded

Repeated black-box probing was perfectly repeatable under the frozen
paired-randomness protocol:

- five RNG replicates;
- pairwise DEC signature distances: all `0.0`;
- q95 DEC radius: `0.0`;
- paired policy repeat max error: `0.0`;
- preprocessing repeat max error: `0.0`;
- DEC stability gate: **passed**.

The first-action support Jacobian at the fine scale was:

```text
[[ 0.1599884,  0.0066643,   2.6519775],
 [ 0.4089317, -0.0629921, -14.7735596]]
```

So the failure below is not explained by RNG instability.

## Robust CRG result

At the frozen trust radius `0.5` and residual tolerance `4.0`:

- nominal residual: `4.4226541813`;
- empirical operator-norm uncertainty: `3.0126126299`;
- best-case residual lower bound: `2.9163478663`;
- worst-case residual upper bound: `5.9289604963`;
- robust decision: **INCONCLUSIVE**.

The uncertainty decomposition is decisive:

- RNG stochastic radius: `0.0`;
- finite-difference scale-drift radius: `3.0126126299`.

The evidence router therefore classified the bottleneck as
**LOCALITY_LIMITED**, disabled additional same-scale querying, and recommended
a smaller physical probe / trust radius rather than more repeated samples.

## Prospective locality refinement

The refinement protocol was frozen before observing the result.

It spent 35 additional same-scale queries and 35 finer-scale queries, then
compared the finite-difference drift:

- coarse→fine drift: `3.0126126299`;
- fine→finer drift: `3.4499882450`;
- contraction ratio: `1.1451814982`;
- frozen contraction threshold: `0.75`;
- recommended trust radius if contraction held: `0.125`.

Because

```text
1.14518 > 0.75
```

the system returned:

```text
REJECT_FIRST_ORDER_LOCAL_MODEL
```

and **did not issue a refined CRG repair certificate**.

Total logical policy queries in the refinement run: `115`.

## Interpretation

This witness separates two failure modes that are often conflated:

```text
stable derivative estimate
        !=
valid local repair model
```

The policy response is deterministic under paired randomness, but not
sufficiently first-order-local across the tested physical scales.

That is evidence *for the fail-closed routing logic*, not evidence that the
requested repair is safe.

## Scientific consequence

The weaker claim

> stable CASJ/DEC is enough to authorize local repair

is falsified on this real frozen policy state.

The surviving stronger claim is:

> runtime repair requires both intervention-identifiable structure and a
> locality/certificate gate; when locality fails to contract, the method must
> reject the first-order repair model rather than spend more same-scale queries.

This result should remain visible even if later policy states or policy families
produce successful repair certificates.

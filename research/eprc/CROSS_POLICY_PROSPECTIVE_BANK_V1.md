# Prospective 20-case cross-policy DEC gate

This protocol is frozen before the pending Diffusion PushT outcome is used to
select states or thresholds.

## Scientific question

Does representation-invariant Differential Execution Contract (DEC) distance
predict how differently two frozen policy families respond to a **fresh physical
disturbance**, better than simpler descriptors?

The target is a fresh held-out response, not a DEC-derived class label. This
avoids evaluating DEC against its own runtime decision.

## Frozen policy pair

- `lerobot/vqbet_pusht@390e5e4c079c880b22e873dad53ecfac706bc78a`
- `lerobot/diffusion_pusht@d3d143b0342488252497853815b27ce3c0384c6b`
- LeRobot runtime:
  `3c0a209f9fac4d2a57617e686a7f2a2309144ba2`.

Both policies use the same PushT physical support chart and controller/action
meaning.

## 20 cases

Ten environment reset seeds are frozen:

```text
17, 29, 43, 59, 71, 89, 101, 131, 151, 181
```

Each state receives two fresh held-out block disturbances:

```text
A = [+4 px, -2 px, +0.020 rad]
B = [-5 px, +3 px, -0.025 rad]
```

The local DEC probe scale is frozen at:

```text
epsilon = 0.125
physical coordinate probes = [2 px, 2 px, 0.01 rad]
```

and policy-randomness replicates use seeds:

```text
123, 456, 789
```

No case may be removed because the result is inconvenient. Invalid physical
states must be reported as protocol failures, not silently resampled.

## Primary outcome

For each state/disturbance pair, compute:

- cross-policy DEC signature distance using the local probe map;
- relative distance between the two policies' **fresh held-out first-action
  responses**.

Across the 20 frozen cases, compute Spearman correlation.

Promotion requires:

```text
rho_DEC >= 0.50
and
rho_DEC >= best_frozen_baseline + 0.10
```

Frozen baselines:

1. raw action-Jacobian distance;
2. support-set distance;
3. static representation metadata;
4. coarse contract-class distance.

## Secondary outcome

If the 20 pairs contain both CRG-decision agreement and disagreement examples,
evaluate the pre-existing AUC gate:

```text
AUC_DEC >= 0.70
and
AUC_DEC >= best_baseline + 0.05
```

If labels are one-class, the AUC outcome is reported as non-identifiable rather
than rebalancing the bank after observation.

## Kill conditions

The cross-policy DEC claim is rejected or narrowed if:

- DEC fails the primary response-prediction gate;
- a raw Jacobian baseline matches/exceeds DEC;
- the result depends on deleting unstable states;
- semantic lifting or support metric changes are tuned after outcomes;
- only the already-observed seed 17 carries the effect.

The manifest `cross_policy_prospective_bank_v1.json` is the machine-readable
source of truth.

# One-page research capsule — counterfactual physical repairability

## Question

Can a frozen robot policy determine, from a small number of controlled physical
counterfactual probes, whether a requested local correction is:

- physically repairable,
- certifiably impossible,
- or unsupported by the local model and therefore must be refused?

The project deliberately separates **identifying a local response** from
**authorizing a repair**.

## Core objects

### Differential Execution Contract (DEC)

A black-box policy is probed under controlled physical support perturbations.
Raw action responses are lifted through controller semantics into canonical
physical-command space so equivalent behavior can be compared across action
parameterizations.

### Counterfactual Repairability Geometry (CRG)

The intervention-identified physical response is intersected with controller
authority and a certified locality radius. Runtime output is:

`CERTIFIED_REPAIR / CERTIFIED_IMPOSSIBLE / INCONCLUSIVE`.

### Certificate-directed probing

When evidence is insufficient, probing is conditioned on the concrete repair
request rather than on reconstructing the whole local Jacobian. The continuous
one-step directional design follows the rank-one information update and reports
explicit black-box policy-query cost.

### Local-model rejection

More probes are not automatically useful. If finite-difference response does
not contract as physical probe scale shrinks, the runtime rejects the
first-order model instead of tuning a threshold until a repair is authorized.

## Strongest real-policy evidence

Official frozen checkpoint:

`lerobot/vqbet_pusht@390e5e4c079c880b22e873dad53ecfac706bc78a`

Frozen LeRobot runtime:

`3c0a209f9fac4d2a57617e686a7f2a2309144ba2`

The first end-to-end public witness is intentionally negative:

- paired replay error: **0.0**;
- five-seed DEC q95 radius: **0.0**;
- stochastic operator radius: **0.0**;
- fine/coarse physical-map drift: **~3.013**;
- robust CRG: **INCONCLUSIVE**.

A prospectively frozen finer-scale experiment then used equal additional query
budgets for same-scale repetition and locality refinement. The physical-map
drift did **not** contract:

- coarse→fine drift: **~3.013**;
- fine→finer drift: **~3.450**;
- contraction ratio: **~1.145**;
- frozen acceptance threshold: **0.75**.

Therefore the preregistered routing decision is:

`REJECT_FIRST_ORDER_LOCAL_MODEL`.

This falsifies the weaker story that a deterministic local policy Jacobian is
automatically a valid runtime repair model.

## Current multi-state gate

Five disjoint PushT reset states are frozen before execution:

`101, 211, 307, 401, 503`.

A richer centered-response jet may be promoted only when first-order locality
fails and the higher-order model passes an out-of-fit finer-scale prediction
gate. The promotion rule itself is frozen before the five outcomes are
adjudicated.

## External evidence boundary

These do **not** count as external validation:

- owner-authored CI;
- self-forks;
- self-repository merges;
- stars;
- synthetic-only examples.

External validation requires a real frozen-policy result produced by another
person/project and accepted by the machine-verifiable replication gate.

Independent replication thread:
https://github.com/lindicaphxag-tech/lindicaphxag-tech/issues/76

## What would falsify the flagship claim

The main claim is dropped or narrowed if any fair prospective benchmark shows:

1. perturbation magnitude or controller headroom predicts recovery as well as CRG;
2. generic controller-space projection matches CRG at equal false-accept rate;
3. request-conditioned probing does not reduce policy queries at matched certificate validity;
4. DEC is unstable after semantic lifting;
5. locality/model-order routing does not outperform simply collecting more same-scale probes;
6. a second frozen policy family does not support the same physical-contract abstraction.

## Claim boundary

This work does not claim invention of Jacobians, Taylor jets, Richardson
extrapolation, compressed sensing, nullspaces, convex separation, active
learning, or controller conversion.

The narrow claim under test is that **intervention-identified physical
repairability, coupled to explicit model-validity and certificate gates, is a
useful runtime object for frozen robot policies**.

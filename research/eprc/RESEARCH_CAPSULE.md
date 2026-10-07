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

## Multi-state model-order gate — negative result

Five disjoint PushT reset states were frozen before execution:

`101, 211, 307, 401, 503`.

The preregistered response-jet gate produced **0/5 upgrades and 0/5 rescues**.
Three states supported a refined first-order certificate; two rejected the
first-order local model. None justified the richer jet on held-out scale
prediction.

Per the frozen rule, the result is:

`DROP_JET_FROM_FLAGSHIP`.

The richer local model is retained only as negative evidence, not as a main
method component.

## Paired cross-policy witness

A same-runner, same-runtime, same-physical-protocol experiment now compares two
official frozen LeRobot policies on the identical PushT support chart and held-out
disturbance.

**Diffusion PushT**
- five-seed DEC q95 radius: **~3.826**;
- stochastic local-map radius: **~21.435**;
- scale-drift radius: **~10.215**;
- bottleneck: **STOCHASTIC_LIMITED**;
- robust CRG: **INCONCLUSIVE**.

**VQ-BeT PushT**
- five-seed DEC q95 radius: **0.0**;
- stochastic local-map radius: **0.0**;
- scale-drift radius: **~3.013**;
- bottleneck: **LOCALITY_LIMITED**;
- robust CRG: **INCONCLUSIVE**.

The fail-closed adjudicator reports:
- same frozen protocol: **yes**;
- reports comparable: **yes**;
- DEC signature distance: **~0.259**;
- held-out response relative distance: **~1.530**;
- robust CRG decisions agree: **yes**;
- both DEC stability gates pass: **no**.

Therefore the project does **not** claim cross-policy numerical DEC equality.
The surviving cross-policy claim is narrower: the same physical-repairability
framework can expose different evidence bottlenecks across frozen policy
families and refuse unsupported repair for different reasons.

See `CROSS_POLICY_RESULT_2026_10_06.md`.

## Flagship freeze

No additional model-order mechanism is promoted without a new prospective gate.
The response jet was rejected at 0/5 rescues and remains negative evidence.
The flagship surface is now frozen around:

1. DEC semantic lifting;
2. robust CRG repairability certificates;
3. evidence-bottleneck / locality routing;
4. certificate-directed identifiability;
5. paired real frozen-policy evidence;
6. machine-verifiable external replication.

New auxiliary mechanisms belong in appendices/tooling unless they change one of
these frozen claims under a prospective benchmark.

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

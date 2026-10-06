# CRG Core v1 — frozen reviewer artifact

This branch is the compact review surface for the surviving DEC / CRG claim.
It intentionally excludes exploratory extensions, historical dead ends, and
large integration scaffolding from the main research branch.

## Research question

Can a frozen robot policy use a small number of controlled physical
counterfactual probes to decide whether one requested correction is:

- certifiably repairable;
- certifiably impossible; or
- unsupported by the current local model and therefore must be refused?

The method is deliberately **fail closed**.

## Core chain

```text
physical intervention
    -> Differential Execution Contract (DEC)
    -> Counterfactual Repairability Geometry (CRG)
    -> robust REPAIR / IMPOSSIBLE / INCONCLUSIVE
    -> certificate-directed probing only when information is the bottleneck
```

### DEC

Raw action responses are first lifted into canonical physical-command space.
The local contract therefore compares physical behavior rather than tensor
coordinates.

### CRG

Given local physical map G and certified support radius r, the repairability set
is the image of the admissible support ball through G. A requested correction d
is repaired only when its residual is below the frozen tolerance.

### Proof-carrying rejection

For K={G xi : ||xi||<=r}, a dual direction n satisfying

```text
n^T d - r ||G^T n|| > 0
```

is an independently checkable witness that d is outside the nominal repair set.

With operator-norm map uncertainty ||G_true-G_hat||<=epsilon_G, the robust
witness becomes

```text
n^T d - r (||G_hat^T n|| + epsilon_G ||n||) > tau.
```

The verifier recomputes this inequality without invoking the repair optimizer.

### Certificate identifiability

The acquisition objective is not full Jacobian recovery. For a concrete repair
direction xi and information matrix V, the unit-norm one-step probe that most
reduces directional uncertainty follows

```text
z* proportional to (V + I)^(-1) xi.
```

The artifact reports the minimum repeated-probe budget needed to cross a
certificate boundary under the frozen information-only model.

## Strongest real-policy evidence

Official frozen checkpoint:

```text
lerobot/vqbet_pusht
revision 390e5e4c079c880b22e873dad53ecfac706bc78a
```

Frozen LeRobot runtime:

```text
3c0a209f9fac4d2a57617e686a7f2a2309144ba2
```

Observed owner-run result:

- paired replay error: 0.0;
- five-seed DEC q95 radius: 0.0;
- stochastic operator radius: 0.0;
- coarse->fine physical-map drift: ~3.013;
- fine->finer drift: ~3.450;
- frozen contraction threshold: 0.75;
- observed contraction ratio: ~1.145;
- routing decision: REJECT_FIRST_ORDER_LOCAL_MODEL.

A separate preregistered five-state model-order gate produced 0/5 response-jet
rescues, so the richer jet was dropped from the flagship rather than tuned.

These are self-authored results. They count as **zero external adoption**.

## What is intentionally not in this core artifact

- response jets / higher-order promotion attempts;
- historical exploratory adapters;
- large runtime-integration scaffolding;
- unrelated upstream patches;
- paper-writing assets.

The reviewer surface is intentionally limited to the surviving mechanism.

## Reproduce the mechanism

```bash
python -m pip install numpy pytest
python -m pytest -q   tests/test_eprc_contract_signature.py   tests/test_eprc_repairability_geometry.py   tests/test_eprc_robust_repairability.py   tests/test_eprc_repairability_witness.py   tests/test_eprc_robust_repairability_witness.py   tests/test_eprc_certificate_directed_probing.py   tests/test_eprc_active_minimal_certificate.py   tests/test_eprc_certificate_identifiability.py   tests/test_eprc_external_replication_gate.py
```

No simulator, GPU, or model checkpoint is required for this contract-level
mechanism test.

## External evidence boundary

Independent replication remains **0**.

A third-party result counts only if it uses a real frozen policy, immutable
source/checkpoint/protocol identifiers, reports all CRG decision counts, query
cost, false accepts/rejects, and at least one execution outcome, and passes the
machine-verifiable evidence digest gate.

Independent replication thread:

https://github.com/lindicaphxag-tech/lindicaphxag-tech/issues/76

## Novelty audit

The frozen claim boundary against active local-validity estimation and frozen-policy recovery is documented in `research/eprc/NOVELTY_BOUNDARY.md`.

## Kill criteria

The flagship claim is narrowed or dropped if fair prospective evidence shows:

1. perturbation magnitude or controller headroom predicts recovery as well as CRG;
2. generic controller-space projection matches CRG at equal false-accept rate;
3. certificate-directed probing does not reduce policy queries at matched validity;
4. semantic lifting does not improve transfer across action/controller charts;
5. locality routing does not outperform blindly collecting more same-scale probes;
6. a second frozen policy family fails to support the same physical-contract abstraction.

## Claim boundary

This work does not claim invention of Jacobians, convex separation, trust
regions, rank-one information updates, nullspaces, active learning, or
controller conversion.

The narrow claim under test is that **intervention-identified physical
repairability, coupled to explicit model-validity and certificate gates, is a
useful runtime object for frozen robot policies**.

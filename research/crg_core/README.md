# Robust Counterfactual Repairability Geometry (CRG)

A minimal public research capsule for one question:

> Given a frozen robot policy and an intervention-identified local physical map, can we certify that a requested runtime repair is possible — or certify that it is impossible — despite local model uncertainty?

This branch is intentionally small. It is not an upstream ManiSkill feature proposal and counts as zero external adoption.

## Object

Let G = d y_phys / d s be the local map from physical-support perturbations to canonical physical-command changes.

CRG does not allow an arbitrary residual action. It restricts repair to the policy-consistent image K(G,r) = {G xi : ||xi||_2 <= r}. The radius r is intersected with controller authority and the local trust region.

## Robust three-way decision

Assume ||G_true - G_hat||_2 <= epsilon_G.

- CERTIFIED_REPAIR when a candidate xi satisfies ||G_hat xi - d|| + epsilon_G ||xi|| <= tolerance.
- CERTIFIED_IMPOSSIBLE when dist(d, K(G_hat,r)) - epsilon_G r > tolerance.
- INCONCLUSIVE otherwise. The runtime must abstain, re-probe, reduce the disturbance, switch controller/policy, or replan.

The abstention region is deliberate: uncertainty changes the logical status of a repair, not merely a score threshold.

## Controller authority under Jacobian uncertainty

For linear action authority H a <= h and ||J_true-J_hat||_2 <= epsilon_J, each row is bounded by

H_i(a0 + J_true xi) <= H_i a0 + (||H_i J_hat||_2 + ||H_i||_2 epsilon_J)||xi||_2.

The code uses this bound to shrink the repair radius before synthesis.

## Run

    python -m pip install numpy pytest
    python -m pytest -q tests/test_crg_core.py
    python research/crg_core/demo.py

No simulator, checkpoint, or GPU is required for the core certificate.

## Claim boundary

This capsule does not claim novelty for Jacobians, robust optimization, constrained control, null-space control, safety projection, or runtime monitoring.

The narrow research claim under investigation is: black-box physical interventions can identify a frozen policy's local repairability geometry strongly enough to certify both executable repair and non-repairability, in canonical physical-command space, before execution.

## Paper-kill gates

Reject CRG as a main claim if: (1) perturbation magnitude or controller headroom predicts recovery equally well; (2) generic controller-space projection matches repair success; (3) robust certificates do not reduce false accepts at useful coverage; (4) intervention-derived maps are too unstable to certify nontrivial regions; or (5) results disappear under a second frozen policy family.
## Certificate-directed probing

When the result is INCONCLUSIVE, CRG does not have to spend probes uniformly.

Maintain a positive-definite information matrix V over support directions and a bound

||(G_true-G_hat) x||_2 <= beta * sqrt(x^T V^{-1} x).

For the current candidate repair xi, one additional probe z changes V to V + z z^T. The exact Sherman-Morrison reduction in the candidate uncertainty is

(xi^T V^{-1} z)^2 / (1 + z^T V^{-1} z).

The capsule therefore supports two query modes:

- candidate-directed probing: among supplied candidate interventions, choose the one that most reduces uncertainty on the repair currently blocking certification;
- weakest-direction probing: query the minimum-information eigenvector when the global impossibility bound is the bottleneck.

This turns intervention budget into a certificate-resolution problem rather than generic Jacobian reconstruction.

Paper-level novelty is not claimed for optimal experimental design itself. The research question is whether certificate-directed physical probes reach a reliable repair/impossibility decision with materially fewer frozen-policy queries than random, coordinate, Rademacher/coded, or generic D/E-optimal probing.

## Local-model admissibility before repairability

CRG now treats the local model class itself as an authorization gate.

A repeated finite-difference Jacobian is not automatically meaningful. Compare
the physical-response map across progressively smaller intervention scales and
separate two failure modes:

- repeated same-scale disagreement -> collect more paired evidence;
- repeatable but non-contracting scale drift -> reject the first-order model.

Only a contracting scale ladder may authorize first-order CRG. A stronger
multi-scale certificate can additionally export a conditional bound on the
unobserved small-scale limit when multiple robust contraction ratios support it.

This is deliberately fail-closed: more same-scale samples are not allowed to
turn a stable but nonlocal Jacobian into false confidence.


## Independent replication

A 30-minute external path is available in
`research/crg_core/REPLICATION_30_MIN.md`.

The schema requests a real frozen policy, immutable provenance, explicit
query/error accounting, and at least one observed execution outcome. These
values are **self-asserted** until a reviewer verifies source/checkpoint
identity and raw execution receipts. A successful SHA-256 schema check does
**not** establish independence or genuine policy execution. Negative results
are welcome and owner-authored results count as zero external recognition.

The walkthrough covers core tests and JSON validation; a new frozen-policy
experiment will take longer than the walkthrough.

```bash
cp research/crg_core/replication_example.json result.json
python -m research.crg_core.seal_replication result.json
python -m research.crg_core.replication_record result.json
```

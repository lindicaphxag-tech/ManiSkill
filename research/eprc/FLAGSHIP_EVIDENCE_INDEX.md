# Counterfactual Physical Repairability — flagship evidence index

This page is the compact entry point for the DEC / CRG / AMRC research line.
It intentionally excludes most implementation detail and separates verified
evidence from open claims.

## Research question

> What is the minimum physical counterfactual evidence needed for a frozen robot
> policy to certify that a requested local correction is repairable, impossible,
> or unsupported by its current local model?

## Surviving core

1. **DEC** — lift intervention-measured policy response into canonical physical
   command space so equivalent action charts can be compared.
2. **CRG** — convert the local physical response into a controller-authority
   constrained repairability set.
3. **Robust CRG** — return CERTIFIED_REPAIR / CERTIFIED_IMPOSSIBLE /
   INCONCLUSIVE under explicit local-map uncertainty.
4. **Certificate identifiability** — choose physical probes to reduce only the
   uncertainty relevant to the current repair certificate, rather than
   reconstructing the full local model.
5. **Fail-closed locality routing** — distinguish information shortage from a
   local-model validity failure.

## Strongest real frozen-policy evidence

### VQ-BeT / PushT

Frozen policy:
`lerobot/vqbet_pusht@390e5e4c079c880b22e873dad53ecfac706bc78a`

Public immutable summary:
`REAL_POLICY_VQBET_EVIDENCE_2026_10_06.md`

Observed mechanism:

- paired policy replay error: **0.0**;
- five-seed DEC q95 radius: **0.0**;
- stochastic map radius: **0.0**;
- fine/coarse operator drift: **~3.0126**;
- robust CRG: **INCONCLUSIVE**;
- AMRC exhausted its frozen planning budget and remained **INCONCLUSIVE**.

Interpretation: this state is not information-limited by policy RNG; the first
order local model is locality-limited.

## Prospective locality falsification

Protocol frozen before finer-scale outcomes:
`VQBET_LOCALITY_REFINEMENT_PROTOCOL.md`

Matched additional query budgets:

- same-scale repeats: **35 policy queries**;
- finer-scale probing: **35 policy queries**.

Observed:

- coarse/fine drift: **3.0127**;
- fine/finer drift: **3.4501**;
- contraction ratio: **1.1452**;
- frozen acceptance threshold: **0.75**;
- same-scale stochastic radius: **0.0**.

Pre-registered route:

`REJECT_FIRST_ORDER_LOCAL_MODEL`

This negative result is retained. Thresholds were not relaxed.

## Higher-order escalation was prospectively rejected

A two-scale centered-response jet was tested on five disjoint frozen PushT
states after its thresholds and promotion rule were frozen.

Result:

- jet rescues: **0 / 5**;
- final decision: **DROP_JET_FROM_FLAGSHIP**.

See:
`PROSPECTIVE_MULTISTATE_JET_RESULT_2026_10_06.md`

This prevents model complexity from being promoted simply because the first
order method failed.

## Proof-carrying rejection

For a certified repair set
`K = {G xi : ||xi|| <= r}`, a compact separating witness can be independently
verified without trusting the repair optimizer.

The robust form checks the support bound under
`||G_true - G_hat||_2 <= epsilon_G`.

See:

- `CRG_PROOF_CARRYING_IMPOSSIBILITY.md`
- `ROBUST_CRG_PROOF_CARRYING_IMPOSSIBILITY.md`

Standard convex separation is not claimed as new mathematics. The research
claim is whether intervention-identified repair sets are predictive enough to
make these certificates useful in frozen-policy deployment.

## External replication gate

Independent positive results are **not** required.

A machine-valid external result must bind:

- immutable source commit and frozen policy checkpoint;
- real policy/controller/task provenance;
- frozen intervention protocol;
- complete CRG decision counts;
- policy-query cost;
- false accepts / false rejects;
- at least one actual execution outcome;
- canonical evidence digest.

See:
`EXTERNAL_REPLICATION_GATE_V1.md`

Public replication request:
https://github.com/lindicaphxag-tech/lindicaphxag-tech/issues/76

Current independent eligible replications: **0**.

## Robotics-runtime adoption path

The cleanest current upstream handoff is LeRobot ACT relative actions, because
issue #3312 explicitly welcomes ACT integration and the proposed patch reuses
LeRobot's existing relative-action processor contract.

The handoff changes exactly:

1. ACT configuration;
2. ACT processor composition;
3. ACT processor regression test.

See:
`upstream/LEROBOT_ACT_RELATIVE_ACTIONS_HANDOFF.md`

This is **PR-ready handoff evidence only**, not LeRobot adoption.

## Explicitly not counted as external recognition

The following count as zero external-adoption credit:

- owner-authored CI;
- self-fork merges;
- stars/forks;
- synthetic-only tests;
- owner-authored replication records;
- compatibility with an upstream architecture without maintained adoption.

## Current promotion boundary

The method should not be called externally validated until at least one of:

1. a machine-valid independent result-bearing replication;
2. maintained robotics-runtime adoption / merge.

A stronger flagship event requires both real-policy evidence across a second
policy family and one external signal above.

L9 remains reserved for independent implementation/comparison plus sustained
external use, citation, or ecosystem adoption.

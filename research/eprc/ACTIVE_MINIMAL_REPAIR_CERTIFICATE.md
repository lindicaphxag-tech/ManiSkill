# Active Minimal Repair Certificate (AMRC)

## Problem

Full local system identification is often unnecessary for a concrete runtime
decision. A robot may only need to know whether one requested physical correction
is certifiably repairable or certifiably impossible.

AMRC therefore changes the query objective from:

> estimate the whole local Jacobian as accurately as possible

to:

> collect the minimum additional counterfactual evidence needed to resolve this
> specific repair request.

## Runtime object

Given a current physical-map estimate G, information matrix V, uncertainty scale
beta, certified support radius r, target correction d, and residual tolerance
tau, robust CRG has three outcomes:

- CERTIFIED_REPAIR;
- CERTIFIED_IMPOSSIBLE;
- INCONCLUSIVE.

For an inconclusive request, AMRC evaluates candidate support probes z by the
certificate that would result from the information update

    V' = V + z z^T.

It greedily selects the probe that first prefers an immediate certificate and,
otherwise, minimizes distance to either valid certificate boundary. Collection
stops as soon as REPAIR or IMPOSSIBLE is certified.

A symmetric physical probe costs exactly two frozen-policy evaluations
(+epsilon z and -epsilon z), so the planner reports explicit incremental query
cost.

## Why this is not generic active learning

The acquisition target is not prediction error, entropy, or full-parameter
recovery. It is the width of a *repairability certificate* for one requested
physical intervention. The stopping condition is semantic and operational:
additional probing stops when runtime action is justified or ruled out.

## Constructive consequence

The system can now return:

    REPAIR, 6 additional policy evaluations

or

    IMPOSSIBLE, 4 additional policy evaluations

rather than spending a fixed dense probing budget before every decision.

## Current deterministic witnesses

In the public CPU regression:

- a repair request aligned with one uncertain support axis is certified after
  3 targeted probes (6 symmetric policy evaluations), while a fixed two-axis
  round-robin needs 5 probes to accumulate the same directional evidence;
- a near-boundary impossible request automatically switches across both support
  axes, because the impossibility certificate depends on the global minimum
  information eigenvalue;
- already-certified requests cost zero new policy evaluations;
- budget exhaustion remains explicitly INCONCLUSIVE.

These are mechanism witnesses, not robot-policy performance claims.

## Real-policy gate

On VQ-BeT PushT and a second frozen policy family, compare:

1. fixed coordinate probing;
2. random Rademacher probing;
3. coded CASJ probing;
4. AMRC request-conditioned probing.

Freeze the repair requests before observing outcomes.

Primary endpoints:

- policy evaluations until first valid certificate;
- certificate outcome agreement with the fixed-budget reference;
- false-accept rate on held-out closed-loop trials;
- fraction of requests that remain inconclusive at a common query budget.

AMRC is rejected as a main contribution if it does not reduce policy-query cost
without increasing false accepts or materially changing valid certificate
decisions.

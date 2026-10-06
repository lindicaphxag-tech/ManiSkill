# Repairability Atlas — cross-policy physical routing

## Motivation

Training-free policy routing already exists, so selecting among policies is not itself a contribution.

The narrower CRG question is whether multiple frozen policies can be compared and routed using their state-local, intervention-identified physical repair sets rather than historical task score or semantic task similarity.

For policy k, define the local set

  K_k = { G_k xi : ||xi||_2 <= r_k },

after semantic lifting into one canonical physical-command space.

## Local repairability dominance

For nominal centered image balls K(A,r_A) and K(B,r_B), B is contained in A when:

1. Im(B) is contained in Im(A); and
2. r_B ||A^+ B||_2 <= r_A.

This defines a local repairability dominance relation. It can identify policies whose local physical repair coverage is redundant at a state, independently of raw action representation.

## Robust routing

For a requested physical correction d, each policy independently emits CERTIFIED_REPAIR, CERTIFIED_IMPOSSIBLE, or INCONCLUSIVE.

- route only to a policy with CERTIFIED_REPAIR;
- return atlas-level CERTIFIED_IMPOSSIBLE only when every policy certifies impossibility;
- otherwise abstain.

Among multiple certified policies, choose using worst-case residual plus an explicit switching cost. Task-history score is not used by the core router.

## Nearest-neighbor boundary

RoboRouter and mixture-of-experts work already route among robot policies/experts. The intended distinction here is state-local physical repairability: the router asks which frozen policy can realize this specific correction under current controller authority and model uncertainty.

## Decisive experiment

Use at least two frozen policy families on the same task and disturbance bank. Compare repairability-atlas routing against:

1. always use current policy;
2. oracle best fixed policy;
3. historical-success routing;
4. semantic/task-similarity routing when available;
5. random policy selection.

Primary endpoints: recovery success, unnecessary switches, false routes, abstention rate, and coverage added by the union of repairability sets.

## Kill criterion

If CRG routing does not outperform a simple historical-success router under matched policy pool and switching budget, keep CRG as a single-policy certificate and drop the atlas as a main contribution.
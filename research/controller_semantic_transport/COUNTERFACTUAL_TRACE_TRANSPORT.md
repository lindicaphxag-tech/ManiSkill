# Counterfactual Trace Transport (CT-CST)

Status: method extension, synthetic validation only.

## Why CST needs a second layer

The exact CST compiler is intentionally narrow. Joint position, joint velocity, Cartesian IK and torque controllers do not generally share one analytic action normal form.

Forcing them into one tensor conversion would recreate the bug class CST is meant to prevent.

CT-CST instead defines semantics by the short-horizon physical trace produced from one exactly restored simulator/controller state.

For controller C:

    Psi_C(s, z, u) = physical trace over H low-level steps.

Given a source trace from controller A, target action transport is:

    u_B* = argmin_u d(Psi_B(s, z_B, u), Psi_A(s, z_A, u_A))

subject to the target action box.

## Solver

Version 0 uses box-constrained damped Gauss-Newton:

1. restore the same target-controller state for every oracle query;
2. estimate the local action-to-trace Jacobian by central finite differences;
3. take a damped least-squares step inside a trust region;
4. clip only to the declared target action box;
5. repeat until the frozen residual gate or iteration budget is reached.

## Authority is stricter than optimization success

A candidate is executable only if all frozen gates pass:

- trace-relative residual below threshold;
- local action-to-trace Jacobian condition number below threshold;
- target action remains away from saturation;
- optimization materially improves over the initial action when an initial mismatch exists.

A low optimization loss alone is not a certificate.

## Counterfactual contract

Every target oracle query must restore identical simulator state, controller hidden state, scene/randomness, horizon and integration settings. Otherwise the Jacobian mixes action effects with state drift and the certificate is invalid.

## Claim boundary

Finite-difference Gauss-Newton, trajectory matching and simulator reset are not claimed as novel.

The narrower research hypothesis is:

> A type-directed exact compiler plus fail-closed counterfactual trace compilation can predict when robot actions are transportable across controller semantics, instead of treating action-space conversion as unconditional tensor remapping.

This is not promoted beyond a method candidate until it predicts success/failure on public ManiSkill controller conversions and transfers to a second stack.

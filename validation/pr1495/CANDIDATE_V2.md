# Clean Production Candidate v2

A clean fork-only production candidate now exists separately from this validation branch:

- fork PR: `lindicaphxag-tech/ManiSkill#12`
- branch: `research/controller-contract-adapter-v2`
- candidate SHA: `69dd520f81831478021ccd542e4b113b6a74e043`

## Design

The converter no longer assumes one fixed controller sign convention.

It measures the production `PDEEPoseController` normalized rotation mapping on basis actions and inverts the observed axis-separable gains.

This makes the converter compatible with both:

- the historical negative rotation gain;
- a sign-preserving controller such as the change proposed in upstream #1472.

## Fail-closed behavior

The adapter rejects controller contracts it cannot safely invert:

- cross-coupled rotation mapping;
- zero-gain rotation axis.

One-step infeasible targets are explicitly identified by the inversion helper and radially projected to the feasible normalized unit ball.

## Promotion gate

This candidate remains fork-only until all of the following are true:

1. CPU contract regression green;
2. direct semantic-fidelity gate green;
3. official-demo replay non-regressive against the frozen main baseline;
4. paired 100-demo audit shows no material regression.

The heavy evidence harness remains in this validation branch so the production candidate stays small.

## Why this is preferable to a synchronized flag day

A synchronized converter + controller change forces all downstream policies and datasets to migrate at once.

A controller-contract adapter is a compatibility layer: it lets the converter preserve requested physical rotation semantics across the sign migration represented by #1472.

This does not eliminate the need to fix controller semantics. It reduces migration coupling between the two fixes.

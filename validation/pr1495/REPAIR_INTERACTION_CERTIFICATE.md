# Repair Interaction Certificate

This note defines the interaction certificate used by the ManiSkill delta-pose validation harness.

## Motivation

A repair can be locally correct and still be unsafe to activate when another latent semantic defect compensates for the original behavior.

For a loss-like semantic error metric (L), evaluate four cells on identical inputs:

- (L_0 = L(\varnothing)): current system;
- (L_1 = L(R_1)): converter-only repair;
- (L_2 = L(R_2)): controller-only repair;
- (L_{12} = L(R_1 \oplus R_2)): composed repair.

## Interaction quantities

The certificate reports:

[
H_1 = L_1 - L_0
]

[
H_2 = L_2 - L_0
]

[
R_{12} = L_{12} - L_0
]

and the repair-interaction term

[
E_{12} = L_{12} - L_1 - L_2 + L_0.
]

Here (H_1) and (H_2) are singleton harms, (R_{12}) is the residual error of the composed repair relative to baseline, and (E_{12}) is the semantic epistasis term.

For the minimizing objective used by the rotation-fidelity assay, a strict compensating bundle satisfies, for tolerance (epsilon),

[
H_1 > epsilon,qquad
H_2 > epsilon,qquad
R_{12} \le epsilon.
]

This says that either singleton is harmful while the composed repair returns to the baseline semantic neighborhood.

## Statistical unit

Control calls within one trajectory are temporally correlated. They are therefore **not** treated as IID replicates.

The validation harness:

1. binds every request to its source `episode_id` and `step_in_episode`;
2. evaluates all four cells on exactly the same request corpus;
3. computes episode-level means;
4. resamples episodes, not individual calls, for the bootstrap confidence interval.

The resulting certificate reports both the pointwise strict condition and a stronger confidence-supported atomicity condition:

- lower CI bound of (H_1) exceeds (epsilon);
- lower CI bound of (H_2) exceeds (epsilon);
- upper CI bound of (R_{12}) is no greater than (epsilon).

## Authorization semantics

A semantic interaction certificate does not authorize physical execution.

If the strict condition holds:

- `R1` alone: reject;
- `R2` alone: reject;
- `R1 + R2`: advance to the execution-domain gate.

The next gate must independently establish replay / execution non-regression. Policy training is a later effect test, not a substitute for semantic fidelity.

## Claim boundary

This certificate establishes an interaction pattern for a frozen metric and frozen input corpus. It does not by itself establish:

- policy-performance improvement;
- end-to-end task non-regression;
- real-robot safety;
- external adoption.

Negative and null outcomes remain valid certificate outputs.

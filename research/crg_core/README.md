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
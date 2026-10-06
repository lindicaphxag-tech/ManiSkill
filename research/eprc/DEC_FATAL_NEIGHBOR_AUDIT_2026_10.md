# DEC fatal-neighbor audit — 2026-10

This file records the closest known ideas that can kill an over-broad Differential
Execution Contract (DEC) claim. It is intentionally stricter than a related-work
section.

## Claim that survives this audit

DEC does **not** claim novelty for Jacobians, task-space pullbacks, pseudoinverses,
inverse dynamics, executable-policy metadata, cross-embodiment alignment, or
counterfactual intervention in general.

The surviving claim is narrower:

> For an arbitrary frozen policy, identify the local map from **canonical physical
> support perturbations** to **canonical physical commands** using controlled
> black-box interventions, then use the identified map together with explicit
> controller semantics to decide local equivalence, support-restricted authority,
> bounded repair, or rejection.

The object of interest is therefore the support-conditioned frozen-policy response

[
J_{DEC}
=
rac{partial y_{mathrm{physical command}}}
     {partial s_{mathrm{physical support}}}.
]

Both numerator and denominator must be canonicalized physical quantities before
two DECs are compared.

## Fatal neighbor 1 — RMPflow / operational-space control

RMPflow and classical operational-space control already transform motion policies
between task/configuration spaces using known task maps, Jacobians, pullbacks and
pseudoinverses.

**Not ours:** Jacobian pullback, task-space transport, null-space reasoning,
pseudoinverse authority, geometric policy transformation.

**DEC separation:** DEC does not start from a designed RMP/task policy and a known
kinematic task map. It probes an arbitrary frozen learned policy to identify how
its action changes when external physical support variables are intervened on.
The controller/task-space Jacobian is only the semantic lift on the output side.

If DEC experiments reduce to known kinematic pullback without needing policy
interventions, the main claim fails.

## Fatal neighbor 2 — VERA / Jacobian inverse dynamics

VERA ("Turning Video Models into Generalist Robot Policies", 2026) explicitly
builds an embodiment-specific inverse dynamics model around a robot Jacobian,
including action-to-point/image-motion Jacobian fields and pseudoinverse action
recovery.

**Not ours:** learning action-to-effect Jacobians, Jacobian-structured inverse
dynamics, action recovery from visual motion, cross-embodiment translation through
embodiment Jacobians.

**DEC separation:** the primary DEC derivative points in the opposite causal
direction:

[
	ext{physical support intervention}
ightarrow
	ext{frozen policy output / canonical physical command}.
]

The optional action-to-effect map is only an auxiliary lift and must not be
presented as the contribution.

If the paper story can be told purely as "learn an action-to-effect Jacobian and
invert it", DEC has collapsed into a VERA-like neighbor and the claim fails.

## Fatal neighbor 3 — Same Weights, Different Robot / ExecSpec

Recent deployment-safety work formalizes that a checkpoint alone is not the
executable policy: unnormalization metadata and controller-facing conventions are
part of the execution specification.

**Not ours:** executable-policy specification, metadata drift detection,
unnormalizer certificates.

**DEC separation:** executable provenance is a prerequisite. DEC asks for a
state-dependent physical response that must be measured after the executable
runtime has been fixed.

The VQ-BeT checkpoint/runtime schema-drift assay in this repository is explicitly
treated as a provenance gate, not DEC evidence.

## Fatal neighbor 4 — action-Jacobian regularization

2026 work on action-Jacobian penalties differentiates policy actions with respect
to state during training to suppress high-frequency control.

**Not ours:** action Jacobians as a mathematical object, differentiating actions
with respect to state, Jacobian regularization, policy smoothing.

**DEC separation:** no policy gradients, weights, or training modification are
required. The intervention coordinates are selected physical supports in the
scene, and the derivative is used for black-box identification and runtime
equivalence/repair.

## Fatal neighbor 5 — cross-embodiment transfer

SHADOW, latent-space alignment, Mirage and related methods already transfer
skills/policies between embodiments through visual editing, learned shared latent
spaces, or execution strategies.

**Not ours:** first cross-embodiment transfer, first shared action/task space,
first zero-shot transfer.

**DEC separation:** cross-embodiment effect-space DEC is secondary. It is allowed
to remain only if a deployment-observable effect map plus support-conditioned DEC
predicts held-out transfer/repair success better than simpler embodiment/task
descriptors.

## Fatal neighbor 6 — counterfactual VLA intervention

CofactVLA and other recent VLA methods use counterfactual interventions to
deconfound or repair policy behavior.

**Not ours:** first counterfactual intervention in VLA/robotics, first test-time
repair, first counterfactual branch.

**DEC separation:** interventions are on physical scene-support variables and are
used to estimate a local external-support response operator of a frozen policy,
not to train/deconfound latent representations.

## What would falsify the paper-level DEC story

The flagship claim should be dropped or narrowed if any of the following holds:

1. raw action Jacobian or support-set overlap predicts held-out runtime decisions
   as well as lifted DEC;
2. static executable metadata predicts the same failures without interventions;
3. support-conditioned response is not stable across repeated probes;
4. canonical support orientation/units cannot be fixed without privileged state;
5. support-restricted authority does not outperform global-rank/clipping flags;
6. cross-policy DEC agreement disappears once runtime provenance is controlled;
7. useful repair cases require retraining the policy;
8. an existing method already estimates the same support->physical-command
   operator and uses it for the same runtime equivalence/authority decision.

## Preferred paper claim

Avoid:

> We introduce Jacobian-based cross-embodiment policy transport.

Prefer:

> We identify a frozen policy's local physical response to controlled scene-support
> interventions and test whether that response, after controller-semantic lifting,
> is a stable predictor of which runtime adaptations preserve physical behavior.

That statement remains falsifiable and separates DEC from the strongest neighbors
found in this audit.

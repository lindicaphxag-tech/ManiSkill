# Certified Closed-Loop Semantic Transport — novelty boundary (2026-10-06)

Status: **L8-candidate research method; no external adoption claim.**

## Prior art that this work does not claim

CST does not claim as novel:

- choosing absolute vs delta or joint vs task-space actions;
- universal / embodiment-agnostic action representations;
- action adapters that decode a canonical representation into robot commands;
- robot-policy retargeting, inverse kinematics, or controller tuning;
- bisimulation / approximate simulation as general control-theory concepts;
- executable-policy manifests or the observation that normalization metadata can
  change physical actions;
- forensic recovery of a finite grammar of undocumented action contracts.

Relevant recent boundaries include:

- *Demystifying Action Space Design for Robotic Manipulation Policies* (2026):
  large-scale empirical action-space design;
- *SPACE: Enabling Learning from Cross-Robot Data Toward Generalist Policies*
  (2026): Cartesian state-delta universal representation plus adaptive command
  execution;
- *Same Weights, Different Robot* (2026): executable policy specification and
  pre-rollout metadata mismatch certificates;
- ActionABI (2026): evidence-first forensic recovery of hidden action-tensor
  contracts with calibrated abstention.

## Narrow constructive hypothesis

The target problem is **controller migration for an already trained frozen
policy**, when controller semantics include state, preprocessing effects and
closed-loop dynamics.

The method asks three questions.

### 1. Is the source executable effect representable by the target?

At a fixed physical/controller state, let

    S = d augmented_observable / d source_action
    T = d augmented_observable / d target_action.

The synthesized local adapter is

    K = pinv(T) S

and the irreducible residual is

    R = (I - P_T) S.

If R is non-zero, exact local transport is impossible under the declared
adapter class. ||R||_2 is an unavoidable unit-action error lower bound, rather
than evidence that an optimizer merely failed.

### 2. Does one-step equivalence close over controller-owned state?

A linear controller-semantic transducer is

    z_next = A z + B u
    y      = C z + D u.

CST synthesizes a state relation and state-aware target adapter

    z_t = M z_s
    u_t = L z_s + K u_s

subject to both output commutation and next-state closure:

    C_t M + D_t L = C_s
    D_t K           = D_s
    M A_s           = A_t M + B_t L
    M B_s           = B_t K.

This distinguishes a true dynamic simulation relation from a one-step numeric
match.  In particular, target-delta -> absolute has no stateless action-only
solution but admits the stateful adapter

    absolute_target = previous_target + delta.

### 3. Does the local certificate survive execution?

For black-box controllers, CST estimates executable-effect Jacobians by paired
two-scale counterfactual rollouts from restored state.  The certificate is
refused when probe-scale instability is excessive or when held-out
counterfactual actions violate a frozen effect tolerance.

Given an incremental bound

    e[t+1] <= rho e[t] + ||R||_2 ||u[t]|| + slack[t],

the certificate propagates one-step transport error into a finite-horizon
behavior envelope. Model slack is explicit and is not hidden inside the action
conversion claim.

## Current evidence

- semantic morphism / stateful semantic compiler / saturation-effect tests:
  green;
- native ManiSkill target-delta hidden-state necessity: green;
- strict upstream-base-fail / clean-patch-pass for issue #429: green;
- closed-loop synthesis / irreducible lower bound / finite-horizon propagation:
  GitHub Actions #37407103809 green;
- native black-box PhysX effect identification and held-out
  delta-current -> absolute certification: GitHub Actions #37407148766 green;
- stateful linear simulation-relation synthesis: GitHub Actions #37407381190
  green.

These results are self-authored validation. They are not external adoption.

## What would actually make the claim materially stronger

1. A ManiSkill maintainer retains the minimal issue-429 fix / regression.
2. A second maintained stack (robomimic, IsaacLab, LeRobot, etc.) retains a
   CST-derived semantic test or repair.
3. A second controller family beyond joint-position charts demonstrates either
   a useful certified adapter or a correct impossibility/refusal result.
4. Held-out nonlinear controller-swap rollouts show that the certificate
   predicts the boundary between safe transport and refusal.
5. Independent downstream use reproduces the result.

## Paper-safe headline today

> Controller migration is not merely action-coordinate conversion.  CST treats
> it as proof-carrying synthesis of an executable simulation relation: it
> identifies whether the target controller can reproduce the source effect,
> synthesizes the minimum state-aware adapter when possible, emits an
> irreducible error witness when not, and falsifies the local certificate on
> held-out restored-state rollouts.

Do not currently claim:

- universal controller equivalence;
- nonlinear global guarantees;
- hardware safety;
- adoption by ManiSkill / IsaacLab / robomimic;
- that bisimulation, canonical action spaces, or action adapters themselves are
  new.

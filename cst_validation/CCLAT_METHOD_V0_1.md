# Certified Closed-Loop Action Transport (CCLAT) — v0.1

Status: research-method candidate. This document freezes the first closed-loop
formulation before native multi-controller evaluation.

## Problem

A frozen robot policy may emit actions for a source controller while deployment
uses a different target controller. Matching action tensors or one-step physical
targets is not sufficient when the controllers induce different closed-loop
state evolution.

Locally represent the source and target in one declared common state:

    x_src' = A_src x_src + B_src u_src
    x_tgt' = A_tgt x_tgt + B_tgt u_tgt

The common state can include physical state and any controller-owned semantic
state that is required by the declared contract.

We synthesize a stateful adapter

    u_tgt = K_x x_tgt + K_u u_src

rather than assuming a stateless action map.

## Exact local transport condition

Exact one-step common-state equivalence requires

    A_tgt + B_tgt K_x = A_src
    B_tgt K_u = B_src.

Therefore an exact linear state-feedback transport exists iff every column of

    [A_src - A_tgt, B_src]

lies in image(B_tgt).

This is a representability statement, not an optimizer-success statement.

### Minimum-norm synthesis

With the Moore-Penrose pseudoinverse:

    K_x = B_tgt^dagger (A_src - A_tgt)
    K_u = B_tgt^dagger B_src.

If the exact condition holds, this is a minimum-norm solution among local
linear adapters.

## Impossibility witness

Let

    P_tgt = B_tgt B_tgt^dagger

be the projector onto the target controller's locally executable effect image.
The unavoidable operator residual is

    E = (I - P_tgt) [A_src - A_tgt, B_src].

If E != 0, no local linear state-feedback adapter of the declared form can make
the two one-step models identical.

The implementation returns the dominant right-singular vector of E, split into

    (x_witness, u_witness),

together with E [x_witness; u_witness]. This is an explicit source
state/action direction that the target input image cannot compensate.

The spectral norm

    ||E||_2

is the worst unavoidable one-step residual over unit combined state/action
directions under the local model.

## Finite-horizon certificate

For

    e_t = x_tgt - x_src,

the synthesized adapter gives

    ||e_{t+1}|| <= rho ||e_t|| + delta,

where

    rho = ||A_tgt + B_tgt K_x||_2

and, over a declared local region

    ||x_src|| <= X,
    ||u_src|| <= U,

we use

    delta = ||R_x||_2 X + ||R_u||_2 U,

with

    R_x = A_tgt + B_tgt K_x - A_src,
    R_u = B_tgt K_u - B_src.

The implementation propagates this recurrence directly. If rho < 1, the usual
geometric bound follows. If the transport is exact and the common initial state
is identical, the certified deviation is zero in the frozen local model.

This is a local model certificate, not a global nonlinear robot-safety proof.

## Relationship to existing CST layers

CST currently has four distinct levels:

1. chart semantics:
   native action -> physical command -> physical target -> target native action;
2. hidden controller state:
   absolute / delta-current / delta-target state machines and trace compilation;
3. controller effects:
   clipping/saturation must commute with the declared physical semantics;
4. closed-loop transport (this document):
   controller/plant local dynamics, state-feedback adapter synthesis,
   structural impossibility witnesses, and finite-horizon deviation bounds.

The fourth level must not be inferred from success at the first three levels.

## Frozen v0.1 evidence

GitHub Actions run 37407305028:
- closed-loop module compiles;
- 8/8 tests pass;
- exact scaled-input transport;
- exact compensation of local state-dynamics mismatch;
- rank-deficient target impossibility witness;
- dynamics-only unrepresentability;
- minimum-norm redundant-target adapter;
- zero finite-horizon bound for exact transport;
- geometric finite-horizon bound for a contractive approximate case;
- 200 randomized exact reparameterizations.

## Novelty boundary

CCLAT does not claim that any of the following are new:
- linear state-space models;
- state feedback;
- pseudoinverse control allocation;
- controllability / input-image analysis;
- bisimulation or approximate bisimulation;
- induced-norm finite-horizon error propagation.

The research hypothesis is narrower:

> controller migration for frozen robot policies should be treated as a
> proof-carrying closed-loop semantic compilation problem, where the system
> either synthesizes a stateful adapter with an explicit behavioral deviation
> certificate or returns a concrete representability witness explaining why
> the target controller cannot preserve the declared source behavior.

Whether this framing and implementation are novel enough for publication
requires comparison against the closest robot-policy portability and formal
controller-refinement literature. No first-of-kind claim is made here.

## Promotion gates

The closed-loop layer is not promoted beyond L8-candidate until all of the
following are satisfied:

1. Native nonlinear assay:
   estimate/freeze local models from two real ManiSkill controller executions
   and test certified vs observed H-step deviation on held-out states/actions.
2. Stateful augmented assay:
   include at least one controller-owned hidden state in the common/lifted
   state and show that omitting it invalidates the certificate.
3. Negative calibration:
   structurally unrepresentable pairs must be rejected before rollout, with
   observed failures retained rather than threshold-tuned away.
4. Second maintained stack:
   reproduce the same semantic phenomenon in an independent public framework.
5. External retention:
   a maintained upstream repository retains a CST/CCLAT-derived fix, contract,
   test, or adapter.

L9 additionally requires independent reuse or strong external paper-level
validation.

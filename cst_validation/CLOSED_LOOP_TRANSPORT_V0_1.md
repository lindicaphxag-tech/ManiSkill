# Certified Closed-Loop Semantic Transport — V0.1

Status: research hypothesis and executable method core. Not an external-adoption claim.

## Problem

A static action converter asks whether a source action can be rewritten in a
target controller chart. That is insufficient for controller migration because
execution is closed-loop and controller-owned state can be part of action
meaning.

We instead declare a shared augmented one-step observable whose coordinates may
include both physical variables and controller-semantic state. Local source and
target executable effects are

    S = d observable / d source_action
    T = d observable / d target_action.

The compiler synthesizes

    K = pinv(T) S.

The irreducible residual is

    R = S - T K = (I - P_T) S.

If R != 0, the source has a local executable-effect direction outside the
target controller image. This is a representability failure, not an optimizer
failure. For unit-norm source action perturbations,

    ||R||_2

is an unavoidable local worst-case error lower bound for every linear adapter.

## Closed-loop propagation

Given an incremental error inequality

    e[t+1] <= rho e[t] + ||R||_2 ||u[t]|| + slack[t],

the method emits an H-step behavior envelope. When rho < 1 and the disturbance
term is uniformly bounded by d,

    e[H] <= rho^H e[0] + (1-rho^H)/(1-rho) d

and the asymptotic envelope is d/(1-rho).

The model slack term is explicit. It is not hidden inside the action-transport
claim.

## Hidden-state requirement

A physical-only observable can produce a false equivalence certificate. If one
controller updates a persistent target state and another does not, the physical
one-step effect can match while the augmented state effect differs. Therefore
strong certificates must include every controller-owned state variable whose
future action interpretation depends on its history.

## Current claim boundary

This module currently certifies local linear executable-effect transport and
propagates a declared incremental bound. It does not yet prove nonlinear global
equivalence, task success, or robot safety. The next native gate is to estimate
local executable-effect Jacobians from independent ManiSkill controller
rollouts and check whether the predicted certificate matches held-out
controller-swap trajectory error.

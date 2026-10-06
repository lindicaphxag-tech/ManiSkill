# Certified Closed-Loop Semantic Transport v0.1

## Research question

Given a frozen robot policy that was designed around controller A, when can its
actions be executed through controller B without changing the local closed-loop
physical behavior?

The object of study is **not** tensor-format conversion.  It is the composed
policy-controller-plant behavior.

For local source and target models

```
source: x' = A_s x + B_s u_s
target: x' = A_t x + B_t u_t
```

we synthesize a stateful adapter

```
u_t = K_x x + K_u u_s.
```

Exact local transport requires

```
A_t + B_t K_x = A_s
B_t K_u = B_s.
```

Equivalently, every column of

```
D = [A_s - A_t, B_s]
```

must lie in `image(B_t)`.

This gives a directly checkable feasibility condition instead of treating
conversion failure as an optimizer failure.

## Constructive impossibility witness

The minimum-norm adapter is

```
K = pinv(B_t) D.
```

The unavoidable unmatched component is

```
R = (I - B_t pinv(B_t)) D.
```

If `R != 0`, exact local transport through controller B is impossible.  The
top right singular vector of R gives a concrete combined state/action
perturbation that asks for a physical direction the target controller cannot
produce.  The spectral norm `||R||_2` is an exact-local-transport lower bound
for unit-norm combined perturbations.

## Stateful controller handshake

The state x may be augmented with controller state (target qpos, integrator,
filter state, reference state, etc.).  This is important: an action-only
converter can be wrong even when the two action vectors have compatible
dimensions.  The synthesized `K_x` is the first explicit state-handshake
mechanism in this prototype.

## Finite-horizon certificate

Let the adapted target matrices be

```
A_hat = A_t + B_t K_x
B_hat = B_t K_u.
```

For source states/actions bounded by `X` and `U`,

```
delta <= ||A_hat-A_s|| X + ||B_hat-B_s|| U.
```

With `rho = ||A_hat||_2`, trajectory error satisfies

```
||e_H|| <= rho^H ||e_0|| + sum_{k=0}^{H-1} rho^k delta.
```

The implementation reports this bound even when rho >= 1, but labels whether
the adapted target is contractive.

## Current evidence boundary

Supported now:
- exact feasibility test for local linearized shared-state models;
- minimum-norm stateful adapter synthesis;
- constructive impossibility witness;
- explicit EXACT / APPROXIMATE / IMPOSSIBLE result;
- finite-horizon norm bound;
- randomized exact-recovery tests and impossible-direction tests.

Not yet supported:
- nonlinear region-wide proof;
- automatic Jacobian extraction from ManiSkill / IsaacLab controllers;
- real-robot safety;
- external maintainer adoption;
- a claim that all controller swaps can or should be repaired.

## Upstream anchor

ManiSkill issue #429 reports 0% success for one
`pd_joint_delta_pos -> pd_joint_pos` conversion path, and a maintainer notes
that fully accurate action-space conversion is a non-trivial research problem.
The upstream patch is intentionally kept separate from this research prototype.

The research goal is broader: characterize when controller migration is
possible, synthesize the minimal stateful adapter when it is, and return a
witness when it is not.

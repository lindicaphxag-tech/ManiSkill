# EPRC v0.2 — Differential Execution Contracts

## Why the claim is narrower now

A 2026 executable-policy-specification line already establishes that checkpoint
weights alone do not determine robot execution: unnormalization metadata and
controller-facing conventions are part of the executable policy.

EPRC therefore does **not** claim novelty for executable-policy specification.

The remaining research question is harder and state-dependent:

> Can the local physical execution contract of a frozen policy be *identified
> from controlled interventions*, and can that contract be compared across
> action representations / controllers in a representation-invariant way?

## Differential execution contract

Let a frozen policy/controller stack produce action coordinates \(a\), and let
\(y=\Phi(a,z)\) be the canonical physical command under runtime semantics
\(z\).

For physical support coordinates \(s\), define

\[
J_{phys}
=
\frac{\partial y}{\partial s}
=
\frac{\partial \Phi}{\partial a}
\frac{\partial a}{\partial s}.
\]

CASJ estimates the second factor from black-box support interventions.
CST/CSIR supplies or validates the first factor.

The **Differential Execution Contract (DEC)** is not the raw Jacobian tensor.
Its minimal representation separates physical response geometry from physical gain:

\[
\mathcal D
=
(P_{\mathrm{Im}(J_{phys})},\; \sigma(J_{phys})/\sigma_1,\;\|J_{phys}\|_F).
\]

The projector and normalized spectrum describe response geometry. The Frobenius gain is retained because, after semantic lifting into common physical units, a 7x larger response is a real physical difference rather than a harmless coordinate change. Action-coordinate changes are removed by the chain-rule lift; physical sensitivity is not normalized away.

## Representation invariance

Suppose another controller uses an invertible local action chart

\[
a' = R a.
\]

Then

\[
J'_{action}=R J_{action},
\qquad
\frac{\partial \Phi'}{\partial a'}=\frac{\partial \Phi}{\partial a}R^{-1},
\]

so

\[
J'_{phys}=J_{phys}.
\]

The public capsule now contains a regression test for exactly this condition:
two raw action Jacobians can look strongly different, yet become identical after
semantic lifting.

## Why this matters

A cross-policy experiment should **not** require equal raw Jacobians. Different
policies and controllers may parameterize actions differently.

The stronger transferable claim is:

> after semantic lifting into canonical physical command space, independently
> probed policies can expose the same local differential execution contract.

That gives EPRC a falsifiable cross-policy target that static metadata
certificates cannot provide.

## Required experiment

For at least two policy families on the same physical task:

1. freeze checkpoint and runtime configuration;
2. perform identical support interventions;
3. estimate action-space CASJ independently;
4. lift each Jacobian through its controller semantics;
5. compare DEC signatures;
6. test whether DEC agreement predicts the same PASS / TRANSPORT / REPAIR /
   REJECT decision on held-out disturbances.

### Primary metric

DEC agreement must predict held-out repair-decision agreement better than:

- raw action-Jacobian distance;
- relevant-object-set overlap;
- static action-metadata equality;
- contract-class label alone.

If it does not, the DEC abstraction is not justified.

## Kill criteria

Reject the DEC claim if:

- semantic lifting does not reduce cross-controller disagreement;
- DEC similarity fails to predict held-out runtime decisions;
- a static metadata certificate performs equally well;
- results depend on privileged simulator state unavailable to deployment;
- only one policy family exhibits stable support response.


## Correction: physical gain is part of the contract

An earlier draft normalized away global gain. That was too weak: once action semantics have been lifted into canonical physical units, global gain controls disturbance sensitivity, repair radius and saturation risk. The executable signature therefore preserves `||J_phys||_F`, and the regression suite explicitly rejects `J_phys` and `7.5 J_phys` as equivalent contracts.

## Nonlinear chart boundary

Representation invariance is stated for smooth local action diffeomorphisms, not only linear maps. If `a'=h(a)` with nonsingular local Jacobian `Dh`, then the action-space CASJ transforms by `Dh` and the semantic lift by `(Dh)^-1`, so the physical DEC is unchanged. If `Dh` loses rank or becomes numerically singular, the change is treated as authority loss rather than harmless reparameterization.

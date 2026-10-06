# DEC local-reparameterization theorem boundary

DEC should be invariant to a change of action coordinates, but not invariant to a change in physical authority.

## Proposition 1 — local action-chart invariance

Let a frozen policy/controller stack have canonical physical command y and local support coordinate s. Let a be one action chart and let a' = h(a) be a smooth local diffeomorphism with nonsingular Dh at the operating point.

Then:

  J_action' = Dh J_action

and the semantic lift in the new chart is:

  dPhi'/da' = dPhi/da (Dh)^(-1).

Therefore:

  J_phys' = (dPhi/da)(Dh)^(-1)(Dh)J_action = J_phys.

This is the precise sense in which DEC is representation invariant. The public regression uses a nonlinear cubic chart h(a)=a+beta*a^3, not only a constant linear matrix.

## Proposition 2 — authority loss is not a coordinate change

If the local action-to-physical map loses rank, as under clipping, saturation, a dead actuator, or a non-injective controller map, there is no local diffeomorphism to cancel.

The rank loss is therefore a physical contract change, not a representation nuisance.

EPRC must reject exact transport when the local chart certificate is singular or numerically ill-conditioned.

## Research consequence

The full DEC story is now stratified:

1. local diffeomorphic reparameterization -> same physical contract;
2. full-rank but physically different lifted Jacobian -> different contract;
3. rank loss -> authority boundary / phase change;
4. unstable support identification -> no contract claim.

This boundary is stronger than comparing action tensors or metadata. It gives a falsifiable distinction between harmless representation changes and deployment changes that alter what the robot can physically do.
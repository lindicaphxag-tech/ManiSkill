# CRG v0.1 — Certified Repairability Geometry

## Core object

CRG asks a stronger question than DEC:

> Given a frozen policy, current controller authority, and intervention-identified local response, which physical corrections are actually repairable before execution?

Let `J` be the CASJ action-support Jacobian and `C` the semantic lift from action coordinates to canonical physical commands. Define `G = C J`.

A scalar Euclidean norm on raw support coordinates is not physically meaningful
when coordinates mix units such as pixels and radians, and it is not invariant
to a change of support chart. CRG therefore uses an explicit positive-definite
support metric `M`:

`B_M(r) = { xi : xi^T M xi <= r^2 }`.

Writing `xi = M^{-1/2} u`, the policy-consistent physical correction set is:

`K_M(r) = { G M^{-1/2} u : ||u||_2 <= r }`.

The identity metric is valid only when the support coordinates have already
been declared dimensionless/canonical.

The controller action box further limits `r`. If nominal action is `a0`, action row `J_i` has norm `||J_i||`, and the nearest lower/upper action margin is `m_i`, then every counterfactual repair in the metric trust region is guaranteed
executable when:

`r <= m_i / ||(J M^{-1/2})_i||_2`

for every active action row.

Therefore the conservative certified radius is:

`r_cert = min(r_trust, min_i m_i / ||(J M^{-1/2})_i||_2)`.

This produces the Certified Repairability Ellipsoid:

`K_cert = { C J M^{-1/2} u : ||u||_2 <= r_cert }`.

## Constructive repair

For target canonical physical correction `d`, solve:

`min_u ||G M^{-1/2} u - d||_2  subject to ||u||_2 <= r_cert`.

The implementation solves the trust-region least-squares problem by SVD and the KKT multiplier. It returns the nearest executable correction, not merely a class label.

## Unrepairability certificate

For the projection `p` of `d` onto `K_cert`, let `n = d - p`. The support function of the ellipsoid image is:

`h_K(n) = r_cert ||G^T n||_2`.

If:

`n^T d - h_K(n) > 0`,

then `n` is a separating hyperplane certificate proving that the requested physical correction lies outside the certified repairability set.

This distinguishes at least two failure modes:

- response-image failure: the desired correction contains a physical direction the frozen policy's local intervention response cannot produce;
- authority/trust failure: the direction is producible, but not within current action bounds or the certified local region.

## Novelty boundary

CRG does not claim invention of nullspaces, trust-region least squares, ellipsoids, support functions, or action manifolds.

Recent work already studies learned action manifolds and even irreducible distance to a frozen decoder image. CRG's narrower target is state-dependent and intervention-grounded:

> identify a local repair map from black-box physical interventions, intersect it with controller authority and local validity, then synthesize a repair or emit an explicit outside-set certificate.

## Decisive empirical test

For held-out disturbances, compare predicted `distance-to-K_cert` / separation margin against actual closed-loop recovery success.

The key falsifier is simple: if CRG margin does not predict real repair success better than perturbation magnitude, raw CASJ norm, controller headroom, or uncertainty baselines, the geometry is not useful.

## Required next experiment

Use at least two frozen policy families on the same task. Estimate `J` independently from interventions, lift through each controller's semantics, construct `K_cert`, and test whether repairability predictions transfer across action representations.

## Support-chart invariance

If another support chart is `xi' = R xi`, then

`J' = J R^{-1}`

and the physical metric transforms as

`M' = R^{-T} M R^{-1}`.

The induced ellipsoid in physical-command space is unchanged because

`J' M'^{-1} J'^T = J M^{-1} J^T`.

The implementation has an explicit non-orthogonal chart regression: certified
radius, synthesized physical correction, residual, and signed repairability
margin must remain unchanged after the joint `(J, M)` transformation.

This is a claim boundary, not decoration: CRG must not claim representation
invariance if the support metric is omitted for mixed-unit coordinates.

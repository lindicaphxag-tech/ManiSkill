# Anisotropic locality-certified repairability

## Motivation

The first real VQ-BeT evidence separated two failure axes:

- repeated-policy stochasticity could be essentially zero;
- finite-difference locality could still fail badly.

The prospective five-state study then showed that repeated-probe stability and
scale locality vary independently across states.

A single scalar trust radius therefore conflates two questions:

1. which physical support directions have a locally supported first-order model?
2. how far may each supported direction move before locality or controller
   authority becomes invalid?

## Directional locality profile

For each physical support coordinate i, compare centered-derivative columns at
coarse, fine, and finer radii:

    D1_i = ||G_coarse[:,i] - G_fine[:,i]||
    D2_i = ||G_fine[:,i] - G_finer[:,i]||
    q_i  = D2_i / D1_i.

Under a frozen contraction threshold, a direction is admitted only when its
observed scale drift contracts.

The resulting local support set is not a ball. It is an axis-aligned ellipsoid:

    xi = R u,  ||u||_2 <= 1,

where R=diag(r_i) contains direction-specific certified radii.

## Controller authority

For nominal action a0 and action-support Jacobian J, action row k changes by

    J_k R u.

Its worst magnitude inside the ellipsoid is

    ||J_k R||_2.

The locality ellipsoid is therefore uniformly scaled only as much as necessary
to satisfy every controller bound, preserving its observed anisotropy.

## Why this is more than a larger trust region

A global ball must use the smallest trusted radius in every direction. If one
support coordinate is unstable, that can collapse the entire repair set.

The anisotropic set instead fails closed only along unsupported directions while
retaining well-supported physical directions. It can therefore be both:

- less permissive in a demonstrably nonlocal direction; and
- less conservative in independently stable directions.

## Uncertainty

With per-column map-error bounds epsilon_i, the scaled map-error operator obeys

    ||E R||_2 <= ||E R||_F
               <= sqrt(sum_i (epsilon_i r_i)^2).

This gives an independently checkable conservative uncertainty bound for the
anisotropic repair set.

## Novelty boundary

Ellipsoidal trust regions, directional finite-difference diagnostics, and
support-function bounds are standard optimization tools and are not claimed as
new mathematics.

The claim under test is narrower:

> counterfactual physical interventions can identify a direction-dependent
> validity region for a frozen robot policy, and using that region for runtime
> repair is more selective than a single scalar trust radius.

## Required prospective test

On a frozen multistate bank, compare:

1. scalar radius chosen from the worst support direction;
2. scalar radius tuned per state;
3. anisotropic locality-certified radii.

At matched false-accept rate, anisotropic CRG must either:

- certify more actually valid repairs; or
- reject unsupported directions earlier with fewer policy queries.

If neither occurs, this component is removed from the flagship claim.

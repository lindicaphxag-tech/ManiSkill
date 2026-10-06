# Stable episode-1 source-level interpolation protocol

Status: **preregistered before observing intermediate alpha outcomes**.

## Question

Does the stable episode-1 main→v2 execution discordance cross a narrow basin boundary along a source-level interpolation between the legacy converter rotation action and the clean v2 rotation action?

## Frozen coarse grid

`alpha ∈ {0, 0.1, 0.25, 0.5, 1.0}`.

For the rotation action returned by the converter:

`a(alpha) = (1-alpha) a_main + alpha a_v2`.

The interpolation is implemented inside a generated source checkout, not by runtime monkeypatching.

## Endpoint gate

No intermediate alpha is causally interpreted unless:

- alpha=0 reproduces canonical main success set `{0,1,3,4,5,6,7,8,9}`;
- alpha=1 reproduces canonical v2 success set `{0,3,4,5,6,7,8,9}`.

If either endpoint fails, the workflow exits non-zero and the scan is recorded only as an invalid intervention.

## No adaptive thresholding in phase 1

The five-point grid is frozen before results. A second-stage refinement is allowed only after a valid coarse run and must be preregistered around the observed transition interval.

## Claim boundary

Even a valid transition is evidence only for the frozen PegInsertionSide replay protocol. It is not a general dynamical-systems law, safety radius, or policy-performance guarantee.

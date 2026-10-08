# Semantic–Execution Decoupling Curve — preregistered protocol

Status: **frozen before repeated intermediate-alpha outcomes are observed**.

## Starting evidence

A valid source-level coarse interpolation already passed both endpoint gates:

- alpha=0 reproduces canonical current-main success set
  `{0,1,3,4,5,6,7,8,9}` (9/10);
- alpha=1 reproduces canonical clean-v2 success set
  `{0,3,4,5,6,7,8,9}` (8/10).

Single-run intermediate outcomes were non-monotone:

- alpha=0.0: episode 1 success;
- alpha=0.1: failure;
- alpha=0.25: failure;
- alpha=0.5: success;
- alpha=1.0: failure.

Those intermediate points are **not yet promoted to repeatable evidence**.

## Frozen alpha grid

```text
alpha in {0.0, 0.1, 0.25, 0.5, 1.0}
```

No alpha is added or removed after seeing repeated outcomes in this phase.

## Two evidence planes

### Plane A — paired semantic fidelity

Capture one immutable request corpus from the exact current-main source under
the first 10 official PegInsertionSide demonstrations.

Every alpha variant receives the same:

- delta pose;
- source episode id;
- within-episode call index;
- controller action bounds/configuration.

Metric:
episode-weighted mean converter-to-controller SO(3) target error.

This is a direct semantic metric, not task success.

### Plane B — execution topology

For each alpha, replay the same first 10 official demonstrations in **5 fresh
Python processes**.

Record:

- exact success episode set;
- episode-1 success frequency;
- total success count;
- exact-repeatability of the success set.

The endpoints must continue to reproduce their canonical success sets in all
five repeats. Otherwise the execution curve is invalidated.

## Frozen hypotheses

### H-curve-1 — semantic path

Test whether semantic error decreases monotonically (within numerical tolerance)
as alpha moves from legacy toward clean-v2 semantics.

Failure of monotonicity is reportable and does not invalidate the assay.

### H-curve-2 — execution path

Test whether episode-1 success is non-monotone over the same alpha ordering.

A non-monotone pattern requires at least two success/failure transitions in the
ordered alpha sequence and exact repeatability at the participating alpha
points.

### H-curve-3 — decoupling

The strongest decoupling witness is:

```text
semantic fidelity improves monotonically
AND
execution success is non-monotone
```

This would show that a scalar semantic-repair progress coordinate does not
induce a scalar task-success radius.

If semantic fidelity is also non-monotone, report a coupled non-monotone path
instead. Do not relabel it as decoupling.

## No adaptive refinement yet

Do not refine the alpha grid until this repeated curve is complete.

If a repeatable transition structure exists, a second-stage refinement may be
preregistered around **all** observed transition intervals. Do not select only
the visually cleanest transition.

## Claim boundary

This is one frozen PegInsertionSide replay protocol. It is not a general
dynamical-systems theorem, policy-training result, or physical safety radius.

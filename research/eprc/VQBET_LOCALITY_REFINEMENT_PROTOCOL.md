# Prospective locality-refinement gate — VQ-BeT / PushT

**Freeze order:** this protocol is committed before the finer-scale outcomes are
read or used to change thresholds.

## Motivation

The frozen VQ-BeT baseline at workflow `37456801175` was deterministic across
five RNG seeds but locality-limited:

- RNG stochastic operator radius: 0;
- fine/coarse scale drift: 3.0126126299;
- robust CRG: INCONCLUSIVE;
- information-only AMRC budget: exhausted, still INCONCLUSIVE.

The next experiment tests whether reducing the *physical locality scale* resolves
that failure more efficiently than collecting more same-scale repetitions.

## Frozen scales

The original dimensionless support chart is retained:

- coarse: 0.50 -> [8 px, 8 px, 0.04 rad] coordinate probes;
- fine: 0.25 -> [4 px, 4 px, 0.02 rad];
- finer: 0.125 -> [2 px, 2 px, 0.01 rad].

The support metric, environment reset seed, exact-state restoration, checkpoint,
controller/action space, and paired-randomness seeds remain unchanged.


## Frozen additional-query bank

The refinement and matched same-scale baseline use the same five new paired
policy-randomness seeds:

```text
20261001, 20261002, 20261003, 20261004, 20261005
```

For each seed, both the 0.25 and 0.125 central-difference maps are measured.
With three support coordinates, one central map costs 7 logical policy queries
(one baseline plus six signed coordinate interventions). Therefore:

- additional 0.25 same-scale baseline: **35** logical policy queries;
- additional 0.125 locality refinement: **35** logical policy queries.

The two arms are thus query-budget matched and seed-paired. These seeds and the
35-vs-35 accounting are frozen before either arm is read.

## Frozen comparison

Let

- D_1 = ||G_0.50 - G_0.25||_2;
- D_2 = ||G_0.25 - G_0.125||_2.

The primary locality diagnostic is the contraction ratio

    q = D_2 / D_1.

Before observing D_2:

- **contracting locality:** q <= 0.75;
- **non-contracting locality:** q > 0.75.

The 0.75 threshold is a diagnostic gate, not a theorem or tuned performance
threshold.

## Certificate policy

If locality contracts:

1. use the 0.125-scale replicate center as the local map;
2. use max(finer-scale stochastic radius, D_2) as the empirical map uncertainty;
3. shrink the support trust radius from 0.50 to **0.125**;
4. recompute the same robust CRG decision and residual tolerance (4.0);
5. do not change the held-out disturbance.

If locality does not contract, the first-order local model is considered
unsupported for this state. The runtime response is **REPLAN / richer local
model**, not more same-scale probing.

## Matched-query baseline

The same number of additional black-box policy evaluations used by the
finer-scale experiment is credited to a same-scale-repeat baseline. Because the
baseline five-seed stochastic radius is already exactly zero, additional
same-scale repeats can only win if they change the observed map or expose
previously unseen stochastic variation.

## Promotion gate

This experiment supports the evidence-action routing claim only if:

- the frozen finer-scale protocol executes without post-hoc threshold changes;
- the routing decision is determined from the above gate;
- no result is discarded for being INCONCLUSIVE or non-contracting.

A single state does **not** establish a general result. It is a mechanism
witness used to design the later multi-state prospective benchmark.

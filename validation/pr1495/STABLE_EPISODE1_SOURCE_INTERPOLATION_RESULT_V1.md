# Stable Episode-1 Source-Level Interpolation Result V1

Workflow: `37460864249` — **success**

Artifact:

- ID: `11412918086`
- zip SHA-256: `4fbde08c4fa2f97b84a1c7981a40aa1ab0c8c7b5ac6d0a812261851872793969`

## Endpoint qualification

The preregistered endpoint gate passed exactly:

- alpha=0.0 reproduces canonical current-main success set
  `{0,1,3,4,5,6,7,8,9}` = **9/10**;
- alpha=1.0 reproduces canonical clean-v2 success set
  `{0,3,4,5,6,7,8,9}` = **8/10**.

Therefore the intermediate source-level interpolation points are valid for the
frozen protocol's causal-path interpretation.

## Frozen coarse path

| alpha | successes | episode 1 |
| ---: | ---: | --- |
| 0.00 | 9/10 | success |
| 0.10 | 8/10 | fail |
| 0.25 | 8/10 | fail |
| 0.50 | 9/10 | success |
| 1.00 | 8/10 | fail |

The shared failure episode 2 remains failed throughout.

## Result

The execution path is **not monotone** on the preregistered coarse grid.

Observed episode-1 sequence:

```text
success -> fail -> fail -> success -> fail
```

There are at least three coarse success/failure transitions:

```text
[0.00, 0.10]
[0.25, 0.50]
[0.50, 1.00]
```

This falsifies a simple one-threshold interpretation of the repair path for
this frozen replay protocol.

## What is established

- both endpoint implementations are reproduced by source-level variants;
- the coarse repair path contains multiple execution-outcome regions;
- the previously observed main-vs-v2 execution difference is reachable through
  source-level interpolation rather than a non-equivalent runtime monkeypatch;
- a scalar alpha is not, by itself, a valid monotone task-success authority
  score on this protocol.

## What is not established yet

The intermediate alpha points were each observed in one execution in this
workflow.

Therefore this result does **not yet** establish that every intermediate
success/failure region is repeatability-qualified.

It also does not yet establish that semantic fidelity changes monotonically
along alpha.

## Frozen next gate

`SEMANTIC_EXECUTION_DECOUPLING_PROTOCOL.md` preregisters the next assay before
repeated intermediate-alpha outcomes are observed:

- same alpha grid: 0, 0.1, 0.25, 0.5, 1.0;
- five fresh-process replay repeats at every alpha;
- one immutable current-main request corpus;
- paired SO(3) semantic fidelity at every alpha;
- endpoint reproduction required;
- no adaptive alpha refinement during phase 1.

A strong semantic-execution decoupling claim is allowed only if semantic
fidelity improves monotonically while the repeated execution path remains
non-monotone.

## Claim boundary

This is a source-level counterfactual on the first 10 official
`PegInsertionSide-v1` demonstrations under one frozen replay protocol.

It is not a general dynamical-systems law, learned-policy performance claim, or
robot safety radius.

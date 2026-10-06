# Episode-1 Prefix Intervention V1 — Invalidated by Endpoint Gate

Workflow: `37410040182`

Artifact:

- ID: `11387854817`
- zip SHA-256: `3022c8e0529f0224b963a95bc411a262d46ad1b68c659ee335f28007b3be706f`

## Preregistered requirement

The intervention path was only interpretable if both endpoint checks held:

1. `candidate_prior, k=0` reproduces the stable candidate episode-1 failure;
2. `main_prior, k=256` reproduces the stable current-main episode-1 success.

## Observed result

The first endpoint passed:

[
candidate_prior,k=0 \Rightarrow fail.
]

The second endpoint failed:

[
main_prior,k=256 \Rightarrow fail.
]

Every tested prefix in both prior-context conditions failed episode 1:

[
k\in\{0,1,2,4,8,16,32,64,128,256\}.
]

The report therefore correctly emitted:

`valid_for_causal_interpretation = false`

and the workflow exited non-zero.

## Why no causal conclusion is allowed

The repeatability-qualified direct source comparison establishes that:

- current main succeeds on episode 1 in 5/5 fresh-process repeats;
- clean adapter v2 fails episode 1 in 5/5 fresh-process repeats.

Therefore a purported “full main” endpoint that still fails does not reproduce the intervention endpoint it claims to represent.

The prefix scan cannot be interpreted as evidence that no prefix is sufficient.

It is evidence that the first interposition method is not endpoint-equivalent to the frozen direct-source measurement regime.

## Diagnostic clue

The invalid full-main intervention still recorded **195** target converter calls.

The direct current-main trace records **186** target converter calls.

That mismatch is itself inconsistent with exact endpoint reproduction.

## Follow-up audit

A separate endpoint-regime audit now compares:

1. direct current-main checkout with `count=2`;
2. direct current-main checkout with `count=10`;
3. direct clean-v2 checkout with `count=2`;
4. clean-v2 checkout with the entire production `conversion.py` replaced byte-for-byte by the frozen current-main version, with `count=2`.

This separates:

- a `count=2` measurement-regime difference;
- a monkeypatch/interposition-equivalence defect;
- an unexpected additional runtime difference.

## Claim boundary

This document records an invalidated causal experiment.

It does **not** weaken the established repeatability-qualified execution regression, because that result comes from the direct-source 5-repeat certificate rather than this intervention.

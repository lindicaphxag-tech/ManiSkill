# Stable Episode-1 Prefix Intervention — Preregistered Protocol

Status: **frozen before observing intervention outcomes**

## Starting evidence

The measurement-qualified replay certificate identifies episode 1 as the stable baseline-only success:

- current main: success in 5/5 repeats;
- clean v2: failure in 5/5 repeats.

The first-divergence witness orders the observable differences as:

1. physical action differs at converter call 0;
2. controller state differs at call 1;
3. requested delta differs at call 2;
4. clipping schedules diverge later.

Adapter v2 and adapter v2 + #1472 remain physically trace-identical.

## Question

Is the stable execution regression caused by an **early prefix** of representation-induced action differences, or is the effect distributed across the entire episode?

## Intervention

Run the clean v2 source, but for episode 1 replace the first (k) converter outputs with the historical-main converter output.

After call (k-1), immediately return to clean v2.

Frozen prefix grid:

[
k \in {0,1,2,4,8,16,32,64,128,256}.
]

Two prior-episode contexts are retained:

- `candidate_prior`: episode 0 uses the candidate converter;
- `main_prior`: episode 0 uses the historical-main converter.

Only the first two official episodes are replayed, preserving serial context through the target episode while avoiding irrelevant later episodes.

## Mandatory endpoint checks

Before interpreting the path:

- `candidate_prior, k=0` must reproduce episode-1 **failure**;
- `main_prior, k=256` must reproduce episode-1 **success**.

If these endpoint checks fail, the intervention surface is invalid for causal interpretation.

## Frozen interpretations

If a small prefix restores success:

> evidence supports early closed-loop amplification of a localized semantic-migration difference.

If only a long/full prefix restores success:

> evidence supports a distributed behavior-compatibility effect rather than one localized trigger.

If no prefix restores success despite a valid main endpoint being expected:

> the implementation of the intervention is invalid or an additional context variable is missing.

If outcomes are non-monotone in (k):

> report the non-monotone repair path; do not collapse it to a scalar robustness radius.

## Non-claims

This scan is not:

- a general robustness radius;
- a proof of dynamical instability;
- a learned-policy experiment;
- a physical safety certificate.

It is a controlled counterfactual over one repeatability-qualified discordant episode.

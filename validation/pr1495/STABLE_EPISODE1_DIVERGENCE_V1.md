# Stable Episode-1 Divergence Result V1

Status: **mechanism witness on the repeatability-qualified stable discordance**

## Evidence chain

Repeatability certificate:

- workflow `37407944746`
- current main succeeds on episode 1 in **5/5** fresh-process repeats;
- clean adapter v2 fails on episode 1 in **5/5** fresh-process repeats.

Serial-context first-divergence workflow:

- workflow `37409297375`
- current main SHA: `107c9528b23b55bd276cf723c260a45ae7ce00ec`
- adapter v2 SHA: `bd0e4feae2491a0d433107210ce8c16b8e8fb69a`
- controller fix: `eed9be164797d41540421bda8adb3840377d7087`

The trace is captured while replaying the first 10 official demonstrations; episode 1 is not converted as an isolated replacement protocol.

## Adapter controller-invariance

Adapter v2 vs adapter v2 + controller fix:

- aligned calls: **195**
- call counts: **195 vs 195**
- first physical-action divergence: **none**
- first controller-state divergence: **none**
- first request divergence: **none**
- clipping schedule identical: **true**
- max physical scaled action L2: **0.0**
- max request position delta: **0.0 m**
- max request rotation delta: approximately numerical zero
- mean local SO(3) error: identical (**0.0307423°**)

Therefore the residual episode-1 regression is not explained by the #1472 sign migration.

## Main vs clean adapter v2

- aligned calls: **186**
- main call count: **186**
- candidate call count: **195**
- first physical-action divergence: **call 0**
- first controller-state divergence: **call 1**
- first requested-delta divergence: **call 2**
- clipping schedule identical over aligned calls: **false**

Later amplification reaches:

- max physical scaled action L2: **0.1207906**
- max requested position delta: **0.0689783 m**
- max requested rotation delta: **5.96934°**

Mean local converter→controller SO(3) error over aligned calls:

- main: **0.0299375°**
- v2: **0.0322298°**

At call 0, before any state/request divergence:

- requested delta is identical;
- both are unsaturated;
- main local SO(3) error: **3.79e-05°**
- v2 local SO(3) error: **0°**
- physical scaled action L2 difference: **6.62e-07**

Thus an initially microscopic representation-induced action difference appears before state divergence and is subsequently amplified by the closed loop.

## Interpretation

The trace supports:

[
a_0^{main} \ne a_0^{repair}
\rightarrow
s_1^{main} \ne s_1^{repair}
\rightarrow
r_2^{main} \ne r_2^{repair}
]

as an observed ordering.

It does **not** yet establish that the call-0 difference is causally sufficient for the final task outcome.

The later clipping-schedule divergence is downstream of the initial state/request divergence in this trace and therefore should not be treated as the first cause.

## Next preregistered causal test

Perform a **serial-context prefix intervention** on episode 1:

- use the clean v2 implementation;
- replace only the first (k) episode-1 converter outputs with the historical main converter;
- return to clean v2 immediately after the prefix;
- preserve the preceding serial context;
- scan a frozen prefix-length grid;
- require endpoint reproduction before interpreting any transition.

If a short main prefix restores the candidate outcome, the result supports early closed-loop sensitivity along the repair path.

If only the full main mapping restores the outcome, the effect is distributed rather than localized.

## Claim boundary

Established:

- stable execution discordance at episode 1;
- immediate action→state→request divergence ordering;
- controller-fix invariance of the clean adapter trace.

Not established:

- causal sufficiency of the first action difference;
- a general robustness radius;
- policy-level impact;
- physical safety.

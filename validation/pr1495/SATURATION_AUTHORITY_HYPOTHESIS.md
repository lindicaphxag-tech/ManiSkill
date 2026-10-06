# Saturation-Authority Hypothesis — preregistered before rerun

Status: **mechanistic hypothesis frozen before evaluating the revised candidate**

## Triggering negative result

Same-base gate run: `37403056943`

Frozen comparison:

- current main: 9/10, successful episodes 0–8, 1424 saved steps;
- contract adapter v2: 8/10, successful episodes 0–7, 1205 saved steps;
- contract adapter v2 + controller fix: 8/10, successful episodes 0–7, 1205 saved steps.

The two adapter cells have identical successful episode sets and identical saved-step counts.

Therefore the adapter is controller-sign invariant in this assay, but execution regresses relative to current main specifically through loss of episode 8.

## Code-level mechanism

The ManiSkill trajectory-conversion loop uses rotation-action norm for **two roles**:

1. numeric clipping;
2. control-flow authority.

When `||arm_action[3:]|| > 1`, the caller:

- clips the rotation action to the unit sphere;
- sets `flag = False`;
- performs another residual-correction iteration, up to four iterations.

The first contract-adapter v2 implementation instead normalized an infeasible rotation **inside the converter** before returning it.

That changed:

```
unclipped requested norm > 1
    -> caller sees clipping
    -> caller retries residual
```

into:

```
converter privately clips to norm = 1
    -> caller sees no clipping
    -> caller treats request as one-step feasible
    -> caller breaks after one execution step
```

The local physical direction can therefore be semantically correct while the caller-level control protocol is wrong.

## Hypothesis

The episode-8 regression is caused by loss of the caller's saturation/retry signal, not by controller-sign dependence.

## Intervention

Revised clean candidate:

`lindicaphxag-tech/ManiSkill@bd0e4feae2491a0d433107210ce8c16b8e8fb69a`

The converter now returns the **unclipped** normalized inverse action and separately marks whether its norm exceeds one. The existing caller remains responsible for clipping and scheduling residual retries.

## Frozen predictions

Before observing the rerun:

1. CPU controller-contract tests remain green.
2. Historical and sign-preserving controller variants remain execution-identical or near-identical.
3. The revised candidate should recover at least the episode-8 behavior lost by the internally clipping draft if saturation-authority loss was causal.
4. If episode 8 does not recover, this hypothesis is falsified or incomplete; no post-hoc gate relaxation is allowed.
5. A 10-demo recovery is still not sufficient for upstream promotion; the larger paired audit remains required.

## Research implication if supported

The semantic boundary includes not only:

- value representation;
- frame;
- unit;
- sign / gain;

but also **ownership of control-flow effects induced by boundary values**.

In this case, out-of-range magnitude acts as an implicit control token granting the caller authority to schedule residual correction.

Thus:

[
ValueEquivalent(a) \not\Rightarrow ProtocolEquivalent(a)
]

and a safe semantic migration may need to preserve **control authority**, not only the physical action after clipping.

## Claim boundary

This document is a preregistered mechanistic prediction, not evidence that the revised candidate succeeds.

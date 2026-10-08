# SUPERSEDED — source-episode target was based on invalid output identity

This preregistration is retained for audit history, but its causal target is invalid.
The original same-base output HDF5 keys were recorder-local renumbered identities,
not source demonstration episode IDs. See
`SOURCE_EPISODE_IDENTITY_CORRECTION.md`.

The code-level saturation/retry ownership observation remains valid, but this
document must not be cited as evidence that it caused the observed replay-count
regression.

---

# Saturation-Authority Hypothesis — preregistered before rerun

Status: **historical preregistration; source-episode causal target superseded by provenance correction**

## Source-identity correction

The original hypothesis below was preregistered from a replay summary that treated saved output groups such as `traj_0..traj_7` as source demonstration IDs.

That identity assumption is invalid: ManiSkill `RecordEpisode` renumbers retained output trajectories consecutively after failed trajectories are dropped.

The public correction is:

- `validation/pr1495/SOURCE_EPISODE_IDENTITY_CORRECTION.md`.

The canonical repeatability-qualified execution result is now:

- current main: `{0,1,3,4,5,6,7,8,9}` = **9/10 in 5/5 fresh-process repeats**;
- clean adapter v2: `{0,3,4,5,6,7,8,9}` = **8/10 in 5/5 fresh-process repeats**;
- stable baseline-only success: **source episode 1**;
- shared failure: **source episode 2**.

A direct source-episode-8 trace later showed episode 8 succeeds under main, v2, and v2+#1472. Therefore all historical text below that names episode 8 as the regression target is retained only as an audit trail and is **not current evidence**.

The clipping/retry ownership observation remains a valid code-level protocol contract, but its causal responsibility for the stable execution regression is **not established**.

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


## Prospective outcome — falsified as the primary explanation

Public same-base rerun: `37404012255`.

The revised candidate preserved the caller's >1 saturation/retry signal, but the execution result remained:

- current main: 9/10, successful episodes 0–8;
- revised adapter: 8/10, successful episodes 0–7;
- revised adapter + controller fix: 8/10, successful episodes 0–7.

Therefore prediction 3 was not supported: episode 8 did **not** recover.

This falsifies saturation-authority loss as the primary cause of the 9→8 regression.

The protocol-effect observation remains valid as a software-contract property, but it must not be presented as the causal explanation for episode 8.

A subsequent first-divergence assay (`37405141224`) shows identical clipping schedules between main and the revised adapter, further excluding clipping/retry schedule as the differentiating mechanism.


## Prospective result status

Follow-up same-base run: `37406432296`

Observed:

- current main: **8/10**, episodes 0–7, 1238 steps;
- revised adapter: **8/10**, episodes 0–7, 1238 steps;
- revised adapter + controller fix: **8/10**, episodes 0–7, 1238 steps;
- exact episode-set parity across all three cells: **true**.

The workflow-level rule emitted `advance_candidate_v2` because both adapter cells were non-regressive relative to that run's baseline.

However, the earlier same-base run `37403056943` had current main at **9/10** with episode 8 successful while the adapter cells were 8/10.

Because the frozen baseline implementation and frozen official inputs changed from 9/10 to 8/10 across runs, the prospective episode-8 prediction is **not confirmed** by `37406432296`. The new run is compatible with the revised adapter being non-regressive, but it cannot distinguish true episode-8 recovery from replay-level simulation variability.

Status of the preregistered hypothesis:

```
saturation-authority mechanism: code-level plausible
CPU contract intervention: passed
prospective episode-8 recovery: INCONCLUSIVE
single-run execution authorization: BLOCKED
```

No post-hoc claim of mechanism confirmation is permitted from the 8/10 parity run.

A dedicated baseline repeatability probe now compares default and enhanced-determinism replay regimes before any further single-run execution claim is accepted.

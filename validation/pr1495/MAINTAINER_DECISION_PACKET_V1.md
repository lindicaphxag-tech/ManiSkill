# PR #1495 — maintainer decision packet v1

Target upstream PR: `mani-skill/ManiSkill#1495`

Current production head:
`69facfaafaa0ef233d36ef19e6cd9a0f03532ee0`

## One-line decision question

Should trajectory conversion derive normalized rotational actions from the **active `PDEEPoseController` action mapping** and encode the requested relative rotation in the controller's XYZ-Euler contract, rather than emitting compact axis-angle values under an assumed sign convention?

## Small upstream surface

- production files changed: **2**;
- upstream PR remains mergeable;
- converter probes the controller's production action mapper rather than assuming `rot_lower` or `rot_upper` sign;
- unsupported zero/non-finite or non-axis-separable rotation mappings fail explicitly.

## What is established

### 1. Representation contract

`PDEEPoseController` consumes XYZ Euler through its rotation matrix construction, while the legacy converter emitted compact axis-angle values.

Focused regressions cover:

- compound non-commuting XYZ rotations;
- positive and negative controller scale conventions;
- anisotropic per-axis scales;
- zero-scale rejection;
- non-axis-separable mapping rejection.

### 2. Paired semantic mechanism

Public workflow `37401619096` evaluated four repair cells on **identical requests** over two independently frozen request corpora.

Baseline-generated corpus, episode-weighted mean SO(3) error:

- main: `0.019900°`;
- converter-only: `2.719173°`;
- controller-only: `2.716609°`;
- composed: `0.013969°`.

Composed-generated corpus:

- main: `0.021249°`;
- converter-only: `2.829643°`;
- controller-only: `2.826887°`;
- composed: `0.014337°`.

Both corpora satisfy the strict compensating-defect pattern under the frozen criterion. This is mechanism evidence, not task-performance evidence.

### 3. Native controller assay

Exact-head native validation on Kaggle T4 / SAPIEN showed the converter reconstructs an unsaturated one-step target much more closely than the legacy axis-angle path:

- current converter: about `5.36e-9 rad` orientation error;
- legacy axis-angle path: about `1.06e-3 rad`.

The saturated multi-step case is mixed; no broad superiority claim is made.

### 4. Execution evidence is intentionally separate

A repeatability-qualified first-10 PegInsertionSide replay protocol produced:

- current main: exact success set `{0,1,3,4,5,6,7,8,9}` in **5/5** fresh processes;
- clean contract adapter v2: exact success set `{0,3,4,5,6,7,8,9}` in **5/5** fresh processes.

Thus the clean v2 failed the current execution non-regression gate because episode 1 is a stable baseline-only success.

This is why the PR does **not** claim that semantic correctness automatically improves task success.

## What is not established

- no policy-training improvement claim;
- no all-task ManiSkill superiority claim;
- no real-robot safety claim;
- no proof that every controller implementation should keep this exact API in ManiSkill 4;
- no upstream adoption until maintainers review/retain the patch.

## Why the current PR differs from the early converter-only attempt

The early converter-only fix implicitly assumed a controller sign convention and interacted badly with the independent controller sign bug.

The current PR instead probes the active production action mapper. It is designed to remain correct under both the current negative-scale behavior and the positive-scale mapping proposed in #1472, while rejecting mappings that cannot be represented as independent per-axis scaling.

## Requested maintainer decision

The useful review question is therefore narrow:

> Is the active controller action mapper the correct source of truth for trajectory conversion under the current ManiSkill 3 controller contract?

If yes, the current patch keeps the upstream surface small and the regression tests local to conversion.

If maintainers prefer to redesign this controller contract in ManiSkill 4, the patch can remain explicitly scoped to current main rather than being treated as a forward-compatible API guarantee.

## Evidence hygiene

Self-authored validation does not count as external adoption. Contradictory results are retained. The latest current-head GitHub Actions validation is tracked separately so stale-head evidence is not presented as exact-head CI.
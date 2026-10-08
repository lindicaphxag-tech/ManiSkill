# Native ManiSkill delta-pose assay

> **Reviewer shortcut:** the current one-page maintainer decision packet is
> [PR1495_MAINTAINER_DECISION.md](https://github.com/lindicaphxag-tech/ManiSkill/blob/handoff/pr1495-maintainer-decision/validation/PR1495_MAINTAINER_DECISION.md).
> It binds the current upstream head `69facfaa...`, the 1-commit/2-file review
> shape, exact-current-head **13/18 passed** compatibility closure, native v15
> evidence, and the single remaining controller-contract question.


This reproducibility package exercises the ManiSkill native PickCube environment and its production delta-pose controller. It compares legacy and repaired multi-axis rotation conversion against the same requested target, then measures controller-target error and closed-loop orientation error at 1, 16, and 64 steps.

## New native task-level pipeline evidence (2026-10-08)

A public CPU-only **official PegInsertionSide Diffusion Policy pipeline** has
now completed end-to-end, separately replaying source trajectories under the
frozen baseline and #1495 + #1472 composition, pairing on identical source
episode seeds, completing actual gradient updates and episode evaluation, and
closing cleanly on Python 3.11.

- [Full green GitHub Actions run #37713921020](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37713921020)
- [Public reproducibility evidence and source/dataset hashes](../kaggle_diffusion_policy_peg/README.md)
- Baseline conversion **6/8**, composed conversion **6/8**,
  shared **six** source seeds, **893 transitions per arm**;
  approximately **4.40M parameters**, two optimizer steps per arm.
- **Both arms: 0% success** in tiny two-episode, 20-step-horizon smoke
  evaluations. This run confirms the pipeline, **not learned-policy
  performance superiority** or a causal benefit attributable to #1495.
- The reproduction shims address headless rendering, Gymnasium 1.2
  terminal-info layout and process cleanup **only within the isolated
  assay**; they are not part of the two-file upstream PR.
- The follow-up **full four-cell official replay** is complete:
  [public SUCCESS run 37715587885](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37715587885).
  Of eight fixed source demos per arm, **baseline 6/8; current #1495 alone
  6/8; exact #1472 alone 0/8; combined #1495 + #1472 6/8**. Full four-way
  successful-seed intersection is **zero**. The converter-only arm is no
  better than baseline on this outcome.

- **NEW: 100 original fixed demonstrations — exact source-identity audit passed.**
  [Original physical four-arm replay #37719545972](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37719545972)
  produced **90/100 baseline, 91/100 converter-only, 1/100 controller-only,
  91/100 combined**.
  [Independent source-seed audit #37746202004](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37746202004)
  downloaded the original ZIP artifact and recomputed all 100 binary rows,
  pairwise source-seed intersections, hashes and summary counts.
  The descriptive original-denominator interaction is **89/100**, with only
  **one** four-way shared successful source demo. This supports a strong
  **converter/controller compatibility interaction** in the frozen
  demonstration conversion task; it does **not** show #1495-alone task
  improvement or usable four-arm Diffusion Policy training evidence.
  [Reviewer-ready decision packet](https://github.com/lindicaphxag-tech/ManiSkill/blob/handoff/pr1495-maintainer-decision/validation/PR1495_MAINTAINER_DECISION.md)
  now reflects these raw-data-audited results.

- A separate **original indices 100–199** cohort was precommitted before
  inspecting the 0–99 outcome, with thresholds that can be falsified:
  [frozen heldout protocol](../kaggle_diffusion_policy_peg/FROZEN_NEXT_COHORT_100_199.md).
  [Holdout CI #37745942944](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37745942944)
  was started and requires an actual completed outcome before any heldout
  benefit is claimed.

This evidence is linked here because this README is already referenced by
the upstream maintainer-facing discussion, avoiding repeated comment spam.

## Reproduction

- Public Kaggle GPU kernel: <https://www.kaggle.com/code/oblivicore/maniskill-native-delta-pose-assay>
- Hardware requested: NVIDIA Tesla T4; the run uses GPU rendering. PhysX simulation remains on CPU.
- Current upstream source under validation: ManiSkill #1495 head `69facfaafaa0ef233d36ef19e6cd9a0f03532ee0` on `fix/delta-pose-euler-action`.
- Kernel runner: [`run_assay.py`](run_assay.py). Build the single-file Kaggle upload with `python research/kaggle_native_assay/build_kaggle_kernel.py --output <kernel-directory>`. The runner verifies the checkout SHA, installs the environment, enables SAPIEN GPU rendering, and runs the PR unit tests plus a hash-identified native rollout harness. Current runs also emit a complete `pip freeze --all` environment snapshot.
- The manifest records byte sizes and SHA-256 hashes for the result, run log, and resolved environment. Verify a downloaded bundle with `python research/kaggle_native_assay/audit_results.py <bundle-directory>`.
- Historical runs [`results/v9/`](results/v9/) and [`results/v10/`](results/v10/) used frozen research commit `102c584f90af83d862ce32ca05a23112603be2ed`; they are not exact-head validation of #1495. Exact-head v12/v13/v14 artifacts are in [`results/pr1495_head_v12/`](results/pr1495_head_v12/), [`results/pr1495_head_v13/`](results/pr1495_head_v13/), and [`results/pr1495_head_v14/`](results/pr1495_head_v14/).

The runner omits ManiSkill's Linux extra `mplib==0.1.1`, which has no compatible Python 3.13 distribution, because this PickCube controller assay does not invoke motion planning. All other listed runtime dependencies are installed. This is an explicit scope limitation, not a full dependency-installation claim.

## Results

The v9 and v10 runs passed on Linux x86_64, Python 3.13.15, PyTorch 2.11.0+cu128, and SAPIEN 3.0.3, with CUDA available and the GPU render backend active. Their orientation measurements are identical. Those results describe only their frozen research commit, not the current #1495 head.

| Regime | Horizon | Legacy final orientation error | Repaired final orientation error |
|---|---:|---:|---:|
| Within per-step rotation limit: target XYZ Euler `[0.035, -0.028, 0.042]` rad | 16 | 0.00099086 rad | 0.00013078 rad |
| Composed multi-step target `[0.55, -0.48, 0.62]` rad | 16 | 0.21240359 rad | 0.22804119 rad |
| Same composed target | 64 | 0.00053337 rad | 0.00009818 rad |

For the unsaturated target, first-step controller-target error changes from `0.00105560` rad (legacy) to `5.36e-9` rad (repaired). Physical orientation error after one simulation step is about `0.0355` rad for both, so target reconstruction is not instantaneous physical tracking.

The native controller clips each Euler axis to `[-0.1, 0.1]` rad per step. The larger target is therefore saturated; at 16 steps the repaired path is slightly worse, while by 64 steps both converge near zero and the repaired path is lower in this deterministic run. This mixed horizon result does not establish general task success or broad performance superiority.

## Public rerun (v10)

Kernel version 10 is public and completed successfully at the Kaggle URL above. It emitted the same orientation measurements as v9 on the frozen test source commit. The repeated run confirms execution reproducibility for this one deterministic setup; it is not independent seed replication or statistical validation. Both runs report Tesla T4 hardware and GPU rendering, while PhysX remains CPU-based.

## Exact PR-head validation (v12)

Kaggle kernel version 12 cloned and checked out #1495 head `875ae4d8777678119b2f192ee186c6c15e6894d5` and completed on a Tesla T4 with Python 3.13.15, PyTorch 2.11.0+cu128, SAPIEN 3.0.3, CUDA available, and GPU rendering. The upstream `tests/test_action_conversion.py` and the hash-identified native controller rollout both passed: 10 tests total. The run emitted dependency/deprecation warnings; they did not fail the tests.

| Regime | Horizon | Legacy final orientation error | PR #1495 final orientation error |
|---|---:|---:|---:|
| Unsaturated XYZ target `[0.035, -0.028, 0.042]` rad | 16 | 0.00099086 rad | 0.00013078 rad |
| Composed saturated XYZ target `[0.55, -0.48, 0.62]` rad | 16 | 0.21240359 rad | 0.22804119 rad |
| Same composed target | 64 | 0.00053337 rad | 0.00009818 rad |

For the unsaturated one-step command, target reconstruction error was `5.36e-9` rad for PR #1495 and `0.00105560` rad for the legacy axis-angle conversion. The repaired path is worse at the 16-step saturated horizon, so this run does not support a blanket superiority claim. It is one deterministic seed and one environment, not a statistical policy-performance result.

The first exact-head attempt, kernel v11, stopped before tests because Kaggle did not stage a separate harness file. The v12 builder embeds that harness in the uploaded script; the v12 console log and manifest are preserved with the result.

## Updated PR-head validation (v13)

Kaggle kernel version 13 checked out the updated #1495 head `5a09b2a4f5a1b1076f88ba01cdacf1683f5494af`. This head adds three edge-case tests without changing the implementation. On the same Tesla T4 stack, all 12 conversion tests and the native controller rollout passed: **13 passed**. It emitted 599 dependency/deprecation warnings. The native measurements match v12 because the code under test is unchanged; v13 verifies the new test cases on the Kaggle stack.

The v13 table values match v12: unsaturated 16-step final error was `0.00013078 rad` for #1495 and `0.00099086 rad` for the legacy baseline; the saturated 16-step result remains worse for #1495 (`0.22804` vs `0.21240 rad`), while at 64 steps it is lower (`0.00009818` vs `0.00053337 rad`). This remains one deterministic rollout seed, not a policy-learning benchmark or significance test.

## Batched rotation stress test (v14)

The current PR head adds a seeded 128-case batched XYZ Euler → quaternion → Euler → matrix round trip, alongside the scale-mapping boundary cases. The exact-head conversion suite passed 13 tests locally. Kaggle v14 checked out commit `fcbf03331985e88e0ba0805c0260dfb8ce7485c2`; all 13 conversion tests plus the native controller rollout passed (**14 passed**, 599 dependency/deprecation warnings). Its hashes, run record, measurements, and console log are in [`results/pr1495_head_v14/`](results/pr1495_head_v14/).

The v14 native measurements match v12/v13. The 128-case test exercises the representation round trip only; it is not 128 robot rollouts or independent task seeds. The policy/controller performance evidence remains the same single-seed experiment.

After v14, GitHub rewrote the PR branch into one commit (`69facfa…`). The v14 checkout (`fcbf033…`) and current PR head have identical Git tree SHA `ff9427533266cc6cabc42e53a0255ca236ae9238`; a direct tree diff is empty. Thus the v14 run tested the exact same source files as the current head. The runner is now pinned to the current commit SHA for future reruns.

Kaggle v15 completed successfully against the current PR commit on a Tesla T4. It passed the upstream conversion suite and native rollout (**14 passed**), and captured `pip freeze --all` as a hashed artifact. The complete v15 bundle is preserved in [`results/pr1495_head_v15/`](results/pr1495_head_v15/); `audit_results.py` verifies all three artifact hashes, the exact source commit, and the embedded harness hash. The resolved environment snapshot SHA-256 is `2cfbc0b4e41781c795fab01db83a5c217a903a53ee1d20964db8a08593a66d3d`.

## Exact squashed-head GitHub compatibility closure

After review-hygiene squashing, the current upstream PR head is:

`69facfaafaa0ef233d36ef19e6cd9a0f03532ee0`

and the upstream PR is again **1 commit / 2 files**.

A separate public validation branch,
`validation/pr1495-squashed-head-v1`, binds directly to that commit and proves
the production/test blobs before executing either compatibility path.

Public workflow run **37687749068 — success**:

- current / legacy mapper: **13 passed**;
- exact #1472 controller and controller-test blobs overlaid on the same squashed
  converter: **18 passed**.

The #1472 job verifies the exact controller source/test blob hashes before
running the combined tests. The legacy job verifies the current conversion and
test blobs against the squashed upstream PR head before execution.

This closes the gap created by the history rewrite: v14 remains native
tree-identical evidence, while run 37687749068 is the explicit
**current-commit identity-bound compatibility check**.

Neither result establishes learned-policy task success or maintainer acceptance.

## Relation to upstream PR #1495

The current runner pins PR head `69facfaafaa0ef233d36ef19e6cd9a0f03532ee0`, which adds a fixed-seed batch rotation round trip on top of anisotropic-scale and invalid-mapping tests. It overlays only the hash-recorded native rollout harness; the ManiSkill source remains unchanged at the pinned PR commit. The v14 run checked out the tree-identical predecessor `fcbf033…`; v13 validates the preceding test-only head `5a09b2a…`; v12 validates `875ae4d…`; the earlier v9/v10 runs do not check out any PR head and remain mechanistic evidence for their frozen research source only. A passing Kaggle run is validation evidence, not proof that #1495 is accepted or merged.

The v9/v10 runs repeat the same source commit, seed, and deterministic setup; they are not independent-seed replications. The v12/v13/v14 exact-head runs use the same deterministic rollout seed and do not provide independent statistical replication. All results remain a narrow controller-conversion regression, with no general performance-superiority claim.

## Scope and evidence limits

This is one deterministic, native PickCube controller assay on one software stack and one GPU-rendering configuration. It does not test pick success, policy learning, multiple robots, hardware transfer, GPU physics, seed variance, or statistical significance. The T4 accelerates rendering; the dynamics simulation is not claimed to run on GPU. The result supports a narrowly scoped controller-space conversion regression only. It does not establish upstream adoption, maintainer acceptance, merge, or an L8/L9 research gate.

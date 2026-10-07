# Native ManiSkill delta-pose assay

This reproducibility package exercises the ManiSkill native PickCube environment and its production delta-pose controller. It compares legacy and repaired multi-axis rotation conversion against the same requested target, then measures controller-target error and closed-loop orientation error at 1, 16, and 64 steps.

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

Kernel v15 is being run against the current PR commit. It additionally captures `pip freeze --all` and includes that snapshot in the hashed manifest, so the resolved runtime can be audited rather than inferred from only the major framework versions.

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

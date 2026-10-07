# Native ManiSkill delta-pose assay

This reproducibility package exercises the ManiSkill native PickCube environment and its production delta-pose controller. It compares legacy and repaired multi-axis rotation conversion against the same requested target, then measures controller-target error and closed-loop orientation error at 1, 16, and 64 steps.

## Reproduction

- Public Kaggle GPU kernel: <https://www.kaggle.com/code/oblivicore/maniskill-native-delta-pose-assay>
- Hardware requested: NVIDIA Tesla T4; the run uses GPU rendering. PhysX simulation remains on CPU.
- Frozen test source commit: `102c584f90af83d862ce32ca05a23112603be2ed` on `research/native-delta-pose-assay`.
- Kernel runner: [`run_assay.py`](run_assay.py). It verifies the checkout SHA, installs the environment, enables SAPIEN GPU rendering, and runs conversion and native controller tests. It emits `assay_result.json`, `experiment_log.json`, and `artifacts_manifest.json`.
- The manifest records byte sizes and SHA-256 hashes for the result and run log. Verify a downloaded bundle with `python research/kaggle_native_assay/audit_results.py research/kaggle_native_assay/results/v10`.
- Recorded runs: [`results/v9/`](results/v9/) and [`results/v10/`](results/v10/).

The runner omits ManiSkill's Linux extra `mplib==0.1.1`, which has no compatible Python 3.13 distribution, because this PickCube controller assay does not invoke motion planning. All other listed runtime dependencies are installed. This is an explicit scope limitation, not a full dependency-installation claim.

## Results

The v9 and v10 runs passed on Linux x86_64, Python 3.13.15, PyTorch 2.11.0+cu128, and SAPIEN 3.0.3, with CUDA available and the GPU render backend active. Their orientation measurements are identical.

| Regime | Horizon | Legacy final orientation error | Repaired final orientation error |
|---|---:|---:|---:|
| Within per-step rotation limit: target XYZ Euler `[0.035, -0.028, 0.042]` rad | 16 | 0.00099086 rad | 0.00013078 rad |
| Composed multi-step target `[0.55, -0.48, 0.62]` rad | 16 | 0.21240359 rad | 0.22804119 rad |
| Same composed target | 64 | 0.00053337 rad | 0.00009818 rad |

For the unsaturated target, first-step controller-target error changes from `0.00105560` rad (legacy) to `5.36e-9` rad (repaired). Physical orientation error after one simulation step is about `0.0355` rad for both, so target reconstruction is not instantaneous physical tracking.

The native controller clips each Euler axis to `[-0.1, 0.1]` rad per step. The larger target is therefore saturated; at 16 steps the repaired path is slightly worse, while by 64 steps both converge near zero and the repaired path is lower in this deterministic run. This mixed horizon result does not establish general task success or broad performance superiority.

## Public rerun (v10)

Kernel version 10 is public and completed successfully at the Kaggle URL above. It emitted the same orientation measurements as v9 on the frozen test source commit. The repeated run confirms execution reproducibility for this one deterministic setup; it is not independent seed replication or statistical validation. Both runs report Tesla T4 hardware and GPU rendering, while PhysX remains CPU-based.

## Relation to upstream PR #1495

The frozen assay commit is `102c584f90af83d862ce32ca05a23112603be2ed` on the fork's `research/native-delta-pose-assay` branch. The public #1495 head was subsequently updated to `875ae4d8777678119b2f192ee186c6c15e6894d5`, adding a runtime probe of the active controller's signed action scale. The Kaggle v9/v10 runs do **not** check out that PR head; they are mechanistic regression evidence for the frozen assay source only. They must not be described as exact-head CI or as proof that #1495 is accepted or merged.

The two recorded runs use the same source commit, seed, and deterministic setup. They confirm that this narrow measurement repeated identically; they are not independent-seed replications. The assay's repaired unsaturated first-command error is below `1e-5` rad, compared with about `1.06e-3` rad for the legacy conversion. For the larger saturated target, the repaired final error is worse at 16 steps and lower at 64 steps. No general performance-superiority claim follows from these runs.

## Scope and evidence limits

This is one deterministic, native PickCube controller assay on one software stack and one GPU-rendering configuration. It does not test pick success, policy learning, multiple robots, hardware transfer, GPU physics, seed variance, or statistical significance. The T4 accelerates rendering; the dynamics simulation is not claimed to run on GPU. The result supports a narrowly scoped controller-space conversion regression only. It does not establish upstream adoption, maintainer acceptance, merge, or an L8/L9 research gate.

# Native ManiSkill delta-pose assay

This reproducibility package exercises the ManiSkill native PickCube environment and its production delta-pose controller. It compares legacy and repaired multi-axis rotation conversion against the same requested target, then measures controller-target error and closed-loop orientation error at 1, 16, and 64 steps.

## Reproduction

- Public Kaggle GPU kernel: <https://www.kaggle.com/code/oblivicore/maniskill-native-delta-pose-assay>
- Hardware requested: NVIDIA Tesla T4; the run uses GPU rendering. PhysX simulation remains on CPU.
- Exact upstream source under validation: ManiSkill #1495 head `5a09b2a4f5a1b1076f88ba01cdacf1683f5494af` on `fix/delta-pose-euler-action`.
- Kernel runner: [`run_assay.py`](run_assay.py). Build the single-file Kaggle upload with `python research/kaggle_native_assay/build_kaggle_kernel.py --output <kernel-directory>`. The runner verifies the checkout SHA, installs the environment, enables SAPIEN GPU rendering, and runs the PR unit tests plus a hash-identified native rollout harness. It emits `assay_result.json`, `experiment_log.json`, and `artifacts_manifest.json`.
- The manifest records byte sizes and SHA-256 hashes for the result and run log. Verify a downloaded bundle with `python research/kaggle_native_assay/audit_results.py <bundle-directory>`.
- Historical runs [`results/v9/`](results/v9/) and [`results/v10/`](results/v10/) used frozen research commit `102c584f90af83d862ce32ca05a23112603be2ed`; they are not exact-head validation of #1495. Exact-head v12 artifacts and the raw Kaggle console log are in [`results/pr1495_head_v12/`](results/pr1495_head_v12/).

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

## Relation to upstream PR #1495

The current runner pins PR head `5a09b2a4f5a1b1076f88ba01cdacf1683f5494af`, which adds tests for anisotropic scales and rejected invalid mappings. It overlays only the hash-recorded native rollout harness; the ManiSkill source remains unchanged at the pinned PR commit. The earlier v12 run validates the immediately preceding head `875ae4d…`; the earlier v9/v10 runs do not check out either PR head and remain mechanistic evidence for their frozen research source only. A passing Kaggle run is validation evidence, not proof that #1495 is accepted or merged.

The v9/v10 runs repeat the same source commit, seed, and deterministic setup; they are not independent-seed replications. The v12 exact-head run is one paired baseline comparison. All results remain a narrow controller-conversion regression, with no general performance-superiority claim.

## Scope and evidence limits

This is one deterministic, native PickCube controller assay on one software stack and one GPU-rendering configuration. It does not test pick success, policy learning, multiple robots, hardware transfer, GPU physics, seed variance, or statistical significance. The T4 accelerates rendering; the dynamics simulation is not claimed to run on GPU. The result supports a narrowly scoped controller-space conversion regression only. It does not establish upstream adoption, maintainer acceptance, merge, or an L8/L9 research gate.

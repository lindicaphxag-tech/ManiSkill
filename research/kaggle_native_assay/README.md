# Native ManiSkill delta-pose assay

This reproducibility package exercises the ManiSkill native PickCube environment and its production delta-pose controller. It compares the legacy and repaired multi-axis rotation conversion against the same requested target, then measures controller target error and closed-loop orientation error at 1, 16, and 64 steps.

## Reproduction

- Public Kaggle GPU kernel: <https://www.kaggle.com/code/oblivicore/maniskill-native-delta-pose-assay>
- Hardware requested: NVIDIA Tesla T4; the run uses GPU rendering. PhysX simulation remains on CPU.
- Frozen test source commit: `102c584f90af83d862ce32ca05a23112603be2ed` on `research/native-delta-pose-assay`.
- Kernel runner: [`run_assay.py`](run_assay.py). It verifies the checkout SHA, installs the environment, enables SAPIEN GPU rendering, and runs both conversion and native controller tests. It emits `assay_result.json`, `experiment_log.json`, and `artifacts_manifest.json`.
- Recorded v9 artifacts: [`results/v9/`](results/v9/).

The runner omits ManiSkill's Linux extra `mplib==0.1.1`, which has no compatible Python 3.13 distribution, because this PickCube controller assay does not invoke motion planning. All other listed runtime dependencies are installed. This is an explicit scope limitation, not a full dependency-installation claim.

## Results (v9)

The run passed on Linux x86_64, Python 3.13.15, PyTorch 2.11.0+cu128, SAPIEN 3.0.3, with CUDA available and the GPU render backend active.

| Regime | Horizon | Legacy final orientation error | Repaired final orientation error |
|---|---:|---:|---:|
| Within per-step rotation limit: target XYZ Euler `[0.035, -0.028, 0.042]` rad | 16 | 0.00099086 rad | 0.00013078 rad |
| Composed multi-step target `[0.55, -0.48, 0.62]` rad | 16 | 0.21240359 rad | 0.22804119 rad |
| Same composed target | 64 | 0.00053337 rad | 0.00009818 rad |

For the unsaturated target, first-step controller target error changes from `0.00105560` rad (legacy) to `5.36e-9` rad (repaired). The physical orientation error after one simulation step is about `0.0355` rad for both, so target reconstruction should not be confused with instantaneous physical tracking.

The native controller clips each Euler axis to `[-0.1, 0.1]` rad per step. The larger target is therefore saturated; at 16 steps the repaired path is slightly worse, while by 64 steps both converge near zero and the repaired path is lower in this single deterministic run. This mixed horizon result does not establish general task success or broad performance superiority.

## Scope and evidence limits

This is one deterministic, native PickCube controller assay on one software stack and one GPU-rendering configuration. It does not test pick success, policy learning, multiple robots, hardware transfer, GPU physics, seed variance, or statistical significance. The T4 accelerates rendering; the dynamics simulation is not claimed to run on GPU. The result supports a narrowly scoped controller-space conversion regression only. It does not establish upstream adoption, maintainer acceptance, merge, or an L8/L9 research gate.

## Public rerun (v10)

Kernel version 10 is public and completed successfully: <https://www.kaggle.com/code/oblivicore/maniskill-native-delta-pose-assay>. The run emitted the same orientation measurements as v9 on the frozen test source commit. See [esults/v10/](results/v10/) for the raw JSON outputs. The repeated run confirms execution reproducibility for this one deterministic setup; it is not independent seed replication or statistical validation. v9 and v10 report Tesla T4 hardware and GPU rendering, while PhysX remains CPU-based.

## Relation to upstream PR #1495

The frozen assay commit is on the fork's esearch/native-delta-pose-assay branch. It includes a sign compensation for the installed controller's negative normalized rotation scaling. The current upstream PR head (cdd6db713ffe7edc3e0df3abfab51ea5320c1c0b, [#1495](https://github.com/mani-skill/ManiSkill/pull/1495)) instead emits positive XYZ Euler values and states that it should follow the separate controller sign fix. Consequently, this Kaggle run is **not exact-head validation of #1495** and must not be read as evidence that the current upstream PR alone passes the native production controller. The PR remains open and awaiting review.

# ManiSkill #429 — minimal official upstream PR draft (AFTER maintainer approval)

**Do not submit yet.** ManiSkill's CONTRIBUTING.md explicitly requires
maintainer approval in the issue before opening a PR. The user has already
posted the technical diagnosis but no maintainer has approved this specific
patch. First post the official-data evidence follow-up and ask for a thumbs-up.

**Once approved, open the official PR with this compare:**
https://github.com/mani-skill/ManiSkill/compare/main...lindicaphxag-tech:ManiSkill:fix/joint-delta-to-joint-pos-pr?expand=1

Suggested title:
`Fix pd_joint_delta_pos -> pd_joint_pos replay semantics and NumPy action decoding`

## Summary

Closes a reproducible conversion bug reported in #429. The original
`pd_joint_delta_pos -> pd_joint_pos` trajectory replay passes NumPy
trajectory rows to a tensor-only scaling helper, and may also encode a
physical joint target using the wrong target-controller action chart.

This two-file focused patch:
- decodes source normalized delta actions into physical joint increments,
  using source-controller bounds, without sending NumPy arrays through
  tensor-only `clip_and_scale_action`;
- computes `physical_target_qpos = source_current_qpos + physical_delta`;
- encodes that target into the **destination** `PDJointPosController`
  native action chart (normalized or physical), rather than passing
  physical qpos directly as a normalized action;
- keeps the change focused and adds deterministic conversion regression
  tests.

## Reproduction: actual official ManiSkill RL trajectories

The canonical publicly reproducible A/B run is:

https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37709660093

Input: official `PickCube-v1` RL demonstration archive downloaded with
ManiSkill's own `download_demo` utility. Its source file contains **997**
`pd_joint_delta_pos` episodes. The A/B used the *same first eight source
episodes*, copying identical input bytes into separate run directories,
and replayed on the CPU backend.

- **Unmodified main:** raises
  `TypeError: clip() received ... (numpy.ndarray, int, int)`
  on the first replay, before producing a usable task success count.
- **This patch:** replay finishes; **4/8 episodes saved (50%)**.

The source demonstrations were generated on **PhysX CUDA**, while
GitHub Actions replays them with **PhysX CPU**. The remaining four failures
must not be attributed to converter correctness without controlling this
backend difference. The comparison shows crash removal and actual
working CPU replay, **not** a baseline 0% vs patch 50% success-rate lift.

The production converter blob in the actual official-data validation run
matches the proposed PR branch exactly:
`15d127773e502ee58a3a6c3ac600deced681bf3d`.

Focused regression CI (also using identical production/test file blobs):
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37455293894

The A/B run has attached original/patch logs and machine-readable
`comparison.json`.

## Scope

This is a precise correctness fix for the supported source/target
joint-position action charts. It does not claim exact replay for all
controller families, simulation backends, or contact dynamics.

## AI assistance disclosure

AI assistance was used to audit the source/target controller semantics,
draft aspects of the patch and construct regression tests. The patch was
verified against upstream source and the public official-data replay.

Related issue: #429

# ManiSkill #429 upstream PR packet

Status: ready for user-side submission. The connected GitHub App returned
`403 Resource not accessible by integration` when attempting to create the
upstream PR, so no external PR is claimed.

## Head/base

- head: `lindicaphxag-tech:fix/joint-delta-to-joint-pos-semantics-clean`
- base: `mani-skill/ManiSkill:main`
- clean branch is currently 0 commits behind upstream main
- upstream diff: 3 files only

## Suggested title

Fix pd_joint_delta_pos to pd_joint_pos conversion semantics

## Suggested body

### Summary

Fixes the `pd_joint_delta_pos -> pd_joint_pos` trajectory conversion path
reported in #429.

The current conversion mixes controller-native and physical action semantics in
two places:

- recorded trajectory rows are NumPy arrays, but the source delta decode calls
  the torch-only `gym_utils.clip_and_scale_action`;
- after decoding a normalized delta into a physical target qpos, that physical
  qpos is passed directly to the target controller even when the target
  `PDJointPosController` expects a normalized native action, causing it to be
  scaled again.

This patch makes the conversion explicit:

    source native action
      -> physical delta qpos
      -> physical absolute target qpos
      -> target-controller native action

### Validation

Focused regression coverage includes:

- normalized delta -> physical delta decoding;
- physical absolute target -> normalized target-controller round trip;
- end-to-end `from_pd_joint_delta_pos` semantics;
- source clipping behavior;
- unnormalized target controllers.

Strict differential evidence:

- upstream base: the frozen reproducer fails 2/2 at
  `gym_utils.clip_and_scale_action -> torch.clip` because the recorded
  trajectory arm action is a NumPy array;
- patched branch: the same 2/2 reproducer cases pass.

Native evidence:

- independent headless PhysX `PDJointPosController` instances receive the same
  physical target after conversion;
- qpos/qvel remain equivalent over physics substeps;
- a target-delta sequence explicitly shows why controller-owned previous target
  state cannot be replaced by measured current qpos.

The upstream PR intentionally contains only the minimal conversion fix and
focused tests. Broader semantic-transport research code is kept out of the
upstream diff.

Fixes #429.

## Frozen evidence

- strict upstream base-fail / clean-fix-pass: Actions #37405088768
- native delta-current -> absolute equivalence: Actions #37404638720
- native target-delta hidden-state necessity: Actions #37404990097

## Reviewer-facing boundary

This PR does **not** claim to solve general control-mode conversion. It repairs
one concrete conversion path by respecting the existing source and target
controller action contracts and adds regression coverage for that contract.

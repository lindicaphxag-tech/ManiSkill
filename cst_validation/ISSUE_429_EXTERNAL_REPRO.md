# ManiSkill #429 — external reproducer and clean patch

Frozen on 2026-10-06.

## Upstream base

Repository: `mani-skill/ManiSkill`

Base commit:

    62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3

Issue: #429 — `pd_joint_delta_pos -> pd_joint_pos` trajectory conversion reports 0% success.

## Clean patch branch

Fork:

    lindicaphxag-tech/ManiSkill

Branch:

    fix/issue-429-joint-delta-pos-clean

The branch is intentionally separate from the CST/CCLAT research branch.

Net review surface against the frozen upstream base:

- `mani_skill/trajectory/utils/actions/conversion.py`
- `tests/test_action_conversion_joint_semantics.py`

No CST research modules, paper experiments, or research workflows are part of
the clean upstream diff.

## Concrete base failure

The upstream conversion path receives a NumPy action row from trajectory data
and calls the torch-only helper:

    gym_utils.clip_and_scale_action(ori_action_dict["arm"], low, high)

The strict differential run froze the same reproducer on the clean patch and
on upstream base. The base reaches `torch.clip` with a `numpy.ndarray` and
fails with `TypeError`.

Accepted differential run:

    GitHub Actions #37405088768

The workflow was written to fail unless the upstream-base traceback reached
that exact NumPy/torch boundary.

## Semantic fix

The clean patch makes the conversion explicit:

    source native normalized delta
      -> physical delta-q
      -> physical absolute target-q
      -> target-controller native action

This also avoids passing a physical qpos directly into a normalized absolute
PDJointPosController, where it would otherwise be interpreted as a normalized
native action and scaled again.

## Clean-branch validation

Temporary focused workflow:

    GitHub Actions #37407925965

Result:

    3 passed

The temporary workflow was then removed, leaving only the production patch and
tests in the branch diff.

The tests cover:

1. NumPy trajectory action -> physical delta-q decoding;
2. physical qpos -> normalized absolute-controller native action;
3. end-to-end delta-current -> absolute physical-target preservation.

## Native simulator evidence kept outside the upstream patch

Research-only independent headless PhysX assays are retained separately:

- Actions #37404638720:
  four delta-current -> absolute cases preserve controller target and qpos/qvel;
- Actions #37404990097:
  target-delta hidden-state necessity is observed under finite-stiffness
  tracking, while state-aware transport preserves target/qpos/qvel.

These runs support the mechanism but are not included in the minimal upstream
diff.

## Upstream submission boundary

The GitHub integration used for this research can push the fork but returned
HTTP 403 when attempting to create the upstream PR. Therefore no upstream PR
is claimed from this document.

A human submission should use the clean branch above and describe the change
as addressing #429, not as solving general cross-controller replay.

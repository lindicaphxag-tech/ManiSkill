# ManiSkill #429 — reduced upstream submission after controlled RL ablation

**Contribution rule:** ManiSkill requests prior maintainer discussion and
approval on the issue before submitting a PR. Do NOT open prematurely.

**Maintainer-review compare (after approval):**
https://github.com/mani-skill/ManiSkill/compare/main...lindicaphxag-tech:ManiSkill:fix/429-numpy-tensor-replay-minimal?expand=1

Suggested title: `fix(trajectory): accept NumPy pd_joint_delta_pos replay actions`

## Summary

Fix NumPy/PyTorch type and batch-shape handling in
`from_pd_joint_delta_pos`, allowing official RL HDF5 demonstrations
(`pd_joint_delta_pos`) to replay as `pd_joint_pos` on Panda.

The source HDF5 action row is NumPy (shape `(7,)`) while
`gym_utils.clip_and_scale_action` calls `torch.clip`. The source
controller `qpos` is a batched tensor `(1,7)`. The patch:
1. makes the action tensor explicit at the source controller's dtype/device;
2. converts the scaled physical delta to a **1-D** NumPy array;
3. reads the current source physical qpos as 1-D NumPy and sums physical
   vectors before passing into the existing target PDJointPos action path.

No new generic action-normalization abstraction. Panda's destination
`pd_joint_pos` controller has `normalize_action=False`, so the
original physical joint-position target semantics are already correct
when the type/shape bug is fixed.

## Three-arm official data evidence

Canonical workflow:
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37713849790

Official PickCube-v1 RL source HDF5 (997 episodes), SHA256
`b05851319021c290ed5e5055c03c776b434af5c9af98e13db2ab9159752b89c8`.
16 identically selected episodes; replay on PhysX CPU rather than source
PhysX CUDA.

| Approach | Outcome |
|---|---|
| Unmodified upstream | TypeError in first episode; not a valid success denominator |
| Type + shape fix only | 7/16 successful demos saved (43.75%) |
| Expanded source+destination semantic encoder | 7/16 successful demos saved (43.75%) |

Identical successful and unsuccessful episode identities between the latter
two arms. This is why the minimal fix is now preferred for upstream review.

The *same minimal implementation* has a focused CPU regression asserting
input `[0.5,-0.5]` from `qpos=[0.2,-0.3]` produces
`[0.25,-0.35]` physical joint position.

Minimal-branch focused + real official replay CI:
https://github.com/lindicaphxag-tech/ManiSkill/tree/validation/mani429-minimal-official-replay-20261008

Do not mark the **minimal exact-blob** workflow green until its run completes.
The previously completed three-arm ablation already establishes the
type/shape-only implementation's task result.

## Limitations

- `pd_joint_pos` Panda default consumes physical qpos, not normalized target
  actions. Therefore no additional output re-encoding improvement is claimed
  under this default mode.
- The issue author already mentioned a NumPy/Torch mismatch in 2024;
  the bug itself is not presented as newly discovered.
- Successful replay count is not baseline 0% -> new 43.75% because the
  original baseline crashes before task outcomes exist.
- Physical backend mismatch (source CUDA vs CPU replay) prevents attributing
  remaining 9/16 failures to this fix without matched backend experiments.

## AI assistance

AI assistance was used for code/CI inspection, testing and drafting.
The patch is deliberately limited to observed correctness failures.

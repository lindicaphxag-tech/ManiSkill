# ManiSkill Issue #429 — updated technical follow-up (copy into official issue)

**Official issue:** https://github.com/mani-skill/ManiSkill/issues/429

Do not claim the follow-up was posted via connector: upstream issue writing
returns HTTP 403 `Resource not accessible by integration`. If posted manually,
the official comment's timestamp and URL constitute external publication.

---

Following up on #429 with an official-data reproduction and a *smaller,
tested fix*.

The unmodified upstream `pd_joint_delta_pos -> pd_joint_pos` conversion
crashes on official PickCube-v1 RL trajectories because a NumPy HDF5 action
is passed into tensor-only `clip_and_scale_action`. The 2024 report had
already raised a NumPy/Torch issue; the new evidence is a controlled,
exact-input three-arm reproduction:

- Upstream `main`: TypeError on episode 1, so there is no valid baseline
  task-success rate.
- Correct NumPy/Torch **type + batch shape only**: 7/16 successful CPU replays.
- Broader controller-chart encoding: also 7/16, same failures.

Full CI and raw logs:
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37713849790

I checked Panda's default destination `pd_joint_pos` config:
`normalize_action=False`, so its action is already a physical qpos target.
This explains why the more complex output encoding did not help the default
Panda task. The appropriate upstream fix appears to be just the NumPy/tensor
and 1-D-vs-batch correction.

Minimal PR-ready diff (one commit, two files):
https://github.com/lindicaphxag-tech/ManiSkill/tree/fix/429-numpy-tensor-replay-minimal

The **exact submitted file contents** separately passed a focused regression
and official PickCube RL CPU replay (7/16 demos):
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37715715576

The original demonstration trajectories were generated with PhysX CUDA and
are replayed on CPU here, so this result does not imply that the remaining
9/16 failures are conversion bugs.

Would a PR restricted to this minimal NumPy/Torch replay correction be
welcome? I will disclose the AI assistance used in code analysis, patch
drafting and public tests, and keep the PR limited to the verified fix.

---

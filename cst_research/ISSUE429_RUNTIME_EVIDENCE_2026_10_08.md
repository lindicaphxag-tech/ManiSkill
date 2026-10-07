# ManiSkill #429 Runtime Evidence — 2026-10-08

## Protocol

A public GitHub Actions A/B harness downloads the official PickCube-v1
demonstrations, converts the same first 10 motion-planning trajectories to
`pd_joint_delta_pos`, then attempts to replay that exact generated source
dataset under `pd_joint_pos`.

The first-stage source conversion succeeded:

```
10/10 = 100.00%
```

so the source dataset used for the A/B is a successful
`pd_joint_delta_pos` dataset, not a synthetic fixture.

## Upstream-main observation

On upstream commit `62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3`,
the `pd_joint_delta_pos -> pd_joint_pos` conversion raises on the first
trajectory before a task-level success rate can be computed:

```
TypeError: clip() received an invalid combination of arguments
- got (numpy.ndarray, int, int)
```

Call path:

```
from_pd_joint_delta_pos
-> gym_utils.clip_and_scale_action(ori_action_dict["arm"], low, high)
-> torch.clip(action, -1, 1)
```

At this point `ori_action_dict["arm"]` is a NumPy array.

This is stronger and more current evidence than simply repeating the old issue
report of 0% success, but it is only the baseline half of the A/B.

## Fix-side gate

The active validation workflow now deliberately records the baseline runtime
error and continues to the PR-ready fix branch.  The workflow only passes if
the fixed branch:

1. exits normally;
2. produces a replay summary; and
3. recovers at least one successful PickCube trajectory.

Until that run completes, do **not** claim trajectory-level recovery.

Validation branch:
`validation/issue-429-trajectory-ab`.

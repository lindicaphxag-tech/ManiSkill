# Frozen protocol — ManiSkill multi-task CST reachability replication v0

Status: **pre-result protocol**.

Fixed task set:
- PickCube-v1
- StackCube-v1
- PegInsertionSide-v1
- PlugCharger-v1

For every task the audit downloads the official motion-planning
`trajectory.json` and `trajectory.h5` from
`haosulab/ManiSkill_Demonstrations` at Hub `main`.

Hard preconditions:
- `trajectory.json` must report `control_mode == pd_joint_pos`;
- every action row must have 8 coordinates;
- Panda articulation state must have 31 coordinates;
- state length must equal action length + 1;
- all values must be finite.

Semantics and thresholds are identical to
`OFFICIAL_PICKCUBE_REACHABILITY_PROTOCOL_V0.md`:
- source arm goal: `actions[:, :7]` (physical absolute qpos);
- measured arm qpos: Panda articulation state `[:, 13:20]`;
- target `pd_joint_delta_pos` / `pd_joint_target_delta_pos` bound:
  [-0.1, +0.1] rad per arm joint;
- numerical tolerance: 1e-9;
- no task-specific tuning.

Per-task metrics:
- trajectories, total actions;
- one-step exact action fraction for delta-current and delta-target;
- number and fraction of trajectories entirely one-step exact;
- H_min histogram and quantiles;
- per-joint p95/max displacement and bottleneck count.

Cross-task metrics:
- macro mean one-step exact fraction;
- micro aggregate one-step exact fraction;
- number of tasks with 100% action-level one-step exactness;
- total actions requiring H_min > 1;
- maximum H_min observed.

Falsification rule:
- If the current-vs-target semantic difference disappears or reverses on
  additional tasks, the claim contracts accordingly.
- No task may be removed after results are observed.

Claim boundary:
- E1 semantic-command reachability only;
- not a task-success, policy-learning, controller-trace, dynamics or safety
  result.
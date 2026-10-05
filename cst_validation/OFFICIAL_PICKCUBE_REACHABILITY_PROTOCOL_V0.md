# Frozen protocol — official ManiSkill action-semantic reachability map v0

Status: **pre-result protocol**.

Dataset:
- `haosulab/ManiSkill_Demonstrations`
- `demos/PickCube-v1/motionplanning/trajectory.h5`
- official `pd_joint_pos` motion-planning demonstrations.

Source semantics (verified from current ManiSkill Panda controller config):
- arm action dimensions: first 7 action coordinates;
- `pd_joint_pos` arm controller uses `normalize_action=False`;
- therefore `actions[t, :7]` is the physical absolute arm-joint goal.

Recorded state semantics (verified from `Articulation.get_state()`):
- Panda state is `[root pose(7), root lin vel(3), root ang vel(3), qpos(9), qvel(9)]`;
- arm measured qpos is `env_states/articulations/panda[t, 13:20]`;
- the two remaining qpos coordinates are the finger joints.

Target A — `pd_joint_delta_pos` (delta-current):
- physical one-step arm bounds are [-0.1, +0.1] rad per joint;
- target semantic displacement at step t is
      d_current[t] = q_goal[t] - q_measured[t]
- exact one-step E1 transport iff every component lies in [-0.1, +0.1],
  up to fixed numerical tolerance 1e-9;
- minimum ideal semantic horizon is
      H_min_current[t] = max_j ceil((abs(d_j)-1e-9) / 0.1),
  lower-bounded by 1.
- H>1 does **not** imply an open-loop exact realization because later commands
  require fresh measured q_current feedback.

Target B — `pd_joint_target_delta_pos` (delta-target):
- same per-step physical bounds [-0.1, +0.1];
- initial target reference is the recorded initial arm qpos;
- after an exact semantic command, the target reference becomes the source
  absolute goal, so for t>0
      d_target[t] = q_goal[t] - q_goal[t-1]
  and for t=0
      d_target[0] = q_goal[0] - q_measured[0].
- H_min_target is computed with the same frozen box formula.

Metrics fixed before reading outcomes:
- number of trajectories and total actions;
- one-step exact fraction for delta-current and delta-target;
- H_min histogram (1,2,3,4,5,6-10,>10);
- median, p90, p95, p99 and max H_min;
- per-joint bottleneck frequency (joint attaining max normalized displacement);
- per-joint p95 and max absolute semantic displacement;
- trajectory-level fraction with every action one-step exact;
- trajectory-level maximum H_min distribution;
- state/action schema validation and finite-value checks.

Claim boundary:
- E1 command semantics only;
- no controller-reference trace, realized trajectory, success-rate or safety claim;
- delta-current H_min>1 is a reachability lower bound, not an executable open-loop plan;
- no threshold will be changed after seeing results.
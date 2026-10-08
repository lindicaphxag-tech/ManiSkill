# Prospective independent-task replication: PushCube frozen PPO + controller memory

Published before running this PushCube task experiment. Previous tasks
and results are **PickCube**, not PushCube. Do not select seeds based on
PushCube results.

## Distinct task/policy and fixed cohort

- Official ManiSkill `PushCube-v1` (Panda; PhysX CPU); different
  pretrained PPO checkpoint from the same publicly published third-party
  ActionShift source:
  `kattri15/actionshift-baselines/ppo/push_cube_final_ckpt.pt`.
- Fixed checkpoint SHA256:
  `a4a02198b309e73cb877959079023d967d5f63ec78380de9703a10c9efafc0cf`.
- **32 preregistered task-initialization seeds: 40001..40032**;
  50-step horizon. No checkpoint tuning, gradient updates or seed
  filtering based on observed outcomes.

## Five real physics arms

1. Frozen source PPO, achieved-relative `pd_ee_delta_pose`.
2. Same frozen PPO, `pd_ee_target_delta_pose` with **runtime previous
   target memory** and bounded non-exact projection.
3. Same frozen PPO, target controller using *current achieved pose*
   instead of previous goal, **same bounded projection algorithm**.
4. Stateful **exact-only** converter, fail-closed when not representable.
5. Raw-action direct copy into target, no conversion.

All arms run on their own current observations. Because different
tasks may have different state observation widths, derive the source
PPO's exact input width from a source env and verify that destination
state observations only differ by the seven controller target-pose
values. Never silently use a hardcoded PickCube 42D index or trim the
final seven dimensions (task extras must remain intact). Abort on any
initial policy-observation or controller state mismatch.

## Outcomes (before seeing results)

- All 32 per-seed actual `success_once` and step count, from real
  ManiSkill task info.
- Primary: paired stateful projected versus stateless projected success,
  with discordant seeds.
- Secondary: stateful projected versus source, exact refusals,
  approximate step count and amplitude, raw-action direct-copy floor.
- A poor PushCube result is a **failed cross-task generalization** and
  must be reported. Do not silently reselect a trained checkpoint.
- If frozen source is incompetent on most of these 32 trials, mark
  cross-task conclusion limited by PPO competence.
- No hardware, no safety certificate, no universal new action-chart
  principle, and not an independent third-party execution.

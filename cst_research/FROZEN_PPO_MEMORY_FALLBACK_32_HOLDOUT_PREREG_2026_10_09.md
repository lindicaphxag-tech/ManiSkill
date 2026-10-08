> **Research-record correction (2026-10-09):** This is **NOT an independent new holdout cohort.** Seeds `20001–20032` and the same four-arm results were already reported in the project's 2026-10-08 prospective pilot: [original results](FROZEN_PPO_MEMORY_32SEED_PILOT_RESULT_2026_10_08.md), [original CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37746168558). The two October 9 runs are additional **reproducibility replications** of an already-observed cohort, not 64 new independent seeds, and the October 9 preregistration cannot be presented as the original preregistration. Do not pool three runs as 96 independent episode samples.

# Preregistered holdout: frozen learned policy with controller-goal memory and bounded fallback

Date: **2026-10-09**. This record is committed BEFORE initiating any
32-seed memory-fallback holdout run or viewing its outcomes.

## Frozen question and action

Does a runtime target-memory-aware executable controller adapter with
**explicit bounded, non-exact projection** retain substantially more
closed-loop task successes than (a) an exact-or-refuse contract and (b)
blind direct-copy, on *new* initial conditions?

Source: pretrained published third-party ActionShift PPO checkpoint
`kattri15/actionshift-baselines/ppo/pick_cube_final_ckpt.pt`;
SHA-256 `3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8`.
**No training, tuning or adaptation of policy weights.**

## Fixed evaluation

- Exactly **32 new independent initial seed IDs, integers 20001–20032**,
  excluding all prior developer and 10001–10032 seeds.
- Task: ManiSkill PickCube-v1 / Panda / PhysX CPU /
  `obs_mode=state`, at most **50 steps per trial**, with no model training.
- Every seed is evaluated on four physically separate simulation copies,
  independently stepping based on each controller's own observation:
  1. source `pd_ee_delta_pose`, frozen PPO;
  2. exact stateful `pd_ee_target_delta_pose` compiler, **refuse** on
     target-native action amplitude > 1 + 1e-5;
  3. target-memory-aware `pd_ee_target_delta_pose` compiler with
     **projected action** (componentwise bound [-1,1] for positional
     native action and Euclidean unit ball for rotational native action),
     separately records each non-exact approximation;
  4. naive unconverted `pd_ee_target_delta_pose` policy output.
- Target controller owns an extra seven pose-memory observation dimensions,
  thus observation projection MUST explicitly verify the `target_pose`
  seven-vector against live controller memory and strip only that field,
  preserving qpos, qvel and task context in original policy order.
- Initial projected 42D observations must agree to tolerance 5e-4
  against source or the trial is **invalid and not a success/failure**.
- Refusal counts as no task success, but remains explicitly its own outcome;
  error/crash is NOT silently counted as failure. Retain all full
  per-seed details with reasons and approximate action counts.

## Frozen primary analysis

Per arm, unconditional successes/32 and exact per-seed outcomes; paired
difference projected-exact and projected-naive; also
projected-source deficit and discordant pair counts.

Feasibility: count runs with any refusal, any approximated action, and
maximum required normalized target amplitude per seed.

Do not filter to source successes or approximate steps only. The primary
denominator stays all 32 when the complete valid run finishes; if
execution errors invalidate runs, report the accurate valid denominator.

## Hypotheses / risks

H1: projection may restore useful task behavior where exact target-action
conversion exceeds destination bounds.
H2: imprecise projection can itself degrade policy performance, and
there may be seeds on which exact/refuse does better. The trial is
**falsifiable** and no target superiority threshold is tuned afterward.

The 4-seed developer pilot (42,270,429,2026) achieved 4/4 for
projected, 2/4 exact/refuse, 1/4 naive:
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37717601656

Those four are NOT part of this preregistered new 32-seed holdout.

## Scientific scope

This is a *single pretrained PPO, single PickCube task and a particular
ManiSkill controller family* pilot holdout. Even a successful holdout
would NOT establish universal safe controller transport, hardware
readiness or first-in-literature generic action adaptation.
Richer contracts, multiple pretrained policies, joint/contact risk
limits and independent maintainer adoption remain future gates.

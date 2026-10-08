# Frozen PPO controller swap — preregistered 32-seed holdout

**Pre-registration timestamp:** 2026-10-08, before launching the 32-seed
holdout job. The 4-seed smoke [42,270,429,2026] has already been
observed and MUST NOT be included in the new holdout summary.

## Preselected holdout (fixed)

Exact, disjoint initial-state seeds:
`10001, 10002, ..., 10032` (32 integer seeds). No seed replacement,
subsetting, tuning or selective rerun to maximize outcomes.

All three arms receive the exact same seed for each episode:
1. Source frozen public PPO with `pd_ee_delta_pose` (expected competent).
2. Compiled frozen PPO with `pd_ee_pose` (same actor weights; source
   native action decoded into the target absolute Cartesian pose).
3. Naive frozen PPO with `pd_ee_pose` but unconverted 7D native action.

Each uses its **own** current `obs_mode=state` observation at every
step, identical public third-party weights, and no policy training
or fine-tuning. Initial observations are compared and any mismatch
over 5e-4 is marked **INVALID**, not silently scored as zero success.

Task: official ManiSkill PickCube-v1 / Panda / PhysX CPU, max 50
simulation steps/episode. Record `success_once`, actual step count,
errors and exact checkpoint hash for every arm/episode.

Public checkpoint:
`kattri15/actionshift-baselines/ppo/pick_cube_final_ckpt.pt`,
SHA-256:
`3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8`.
It is an independent published PPO baseline, NOT a model we trained.

## Frozen analysis

Primary:
- paired success count and fraction for each arm over **all 32**.
- `compiled - naive` paired success difference in percentage points.
- `compiled - source` paired success difference in percentage points.
- discordant pairs `n(compiled=1,naive=0)` and
  `n(compiled=0,naive=1)`.
- report all source failures; don't condition on source success
  without also presenting unconditional results.

Secondary:
- distributions of episode completion steps, including 50-step
  censoring for unsuccessful episodes (do not treat as successful
  completion times).
- exact per-seed outcomes, no duplicate episode deletion.

No inferential superiority claim from the four earlier development
seeds. The new 32-seed run is a **pilot holdout**; for scientific
publication require a separate, preregistered confirmatory split and
more diverse task/controller families, plus stateful memory interventions.

## Scientific claim boundary

This tests a **known action-chart translation** between ManiSkill
Panda EE controllers. It does NOT establish that automatic controller
state extraction or robosuite OSC target-memory transport works on a
frozen trained policy. That latter mechanism has its own scripted
causal physics evidence and still needs learned-policy integration.

A success in the 32-seed controller swap would validate execution
robustness and improve evidential completeness, **not** establish
novelty of a generic delta-to-absolute adapter.

Parent initial 4-seed run (NOT holdout):
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37716549038

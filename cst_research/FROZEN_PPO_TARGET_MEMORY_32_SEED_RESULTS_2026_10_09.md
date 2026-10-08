# Frozen-policy goal-memory compilation with bounded feasibility: 32-seed pilot

**Pre-registered before experiment:** [protocol](FROZEN_PPO_TARGET_MEMORY_32_SEED_PROSPECTIVE_2026_10_09.md)
(correct filename: [TARGET_MEMORY_32_SEED_PROSPECTIVE_2026_10_09.md](TARGET_MEMORY_32_SEED_PROSPECTIVE_2026_10_09.md))

**Author-run public CI:** https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37814776505

**Exact code:** https://github.com/lindicaphxag-tech/ManiSkill/blob/validation/frozen-ppo-memory-holdout-32-20261009/research/frozen_ppo_target_memory.py

Date: 2026-10-09. The experiment uses new prespecified seeds
`20001`–`20032`, disjoint from the development seeds `42/270/429/2026`
and separate from the delta-to-absolute study `10001`–`10032`.
32 out of 32 launched episode groups produced outcomes; initial
source-vs-target observations after explicit 49D -> 42D source-ABI
projection matched **exactly** (`initial_obs_diff=0.0`) on all groups.

## Real physical simulation, no policy training

External, pre-trained PPO belongs to the authors of ActionShift
(`kattri15/actionshift-baselines/ppo/pick_cube_final_ckpt.pt`; SHA-256
`3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8`).
It is NOT a newly trained model by this project.
Each independent Panda PickCube-v1 PhysX CPU environment receives the
unchanged policy on its **own** online observations.

Target `pd_ee_target_delta_pose` tracks the last desired target
controller pose in its runtime state; original PPO's
`pd_ee_delta_pose` instead composes increments from the *currently
achieved* pose. The goal memory adds 7 dimensions to the target state's
observation, making it 49D vs the original 42D PPO input; the adapter
validates and strips only the 7D controller-owned field for policy
inference and separately reads that field for action compilation.

## Unconditional results (every prespecified seed)

| Mode | Task success | Interpretation |
|---|---:|---|
| Original source PPO, achieved-relative deltas | **31 / 32** | Source-performance baseline; seed 20016 failed |
| Exact stateful translation, REFUSE unrepresentable one-step action | **5 / 32** | 27 actual fail-closed stop/refusals; no false exactness |
| Stateful translation + bounded *non-exact* native-action projection | **32 / 32** | 30 non-exact projected actions across 27 episodes |
| Raw PPO actions on target-history mode | **3 / 32** | Semantically incompatible direct-copy baseline |

The exact-stateful successful seeds: **20003, 20017, 20022, 20025,
20026**. The naive successes: **20006, 20023, 20031**. The stateful
bounded solution succeeds in all 32 during this one job, including seed
20016 which the source failed; that is a **single-run observation**,
NOT evidence it generally outperforms the source.

Maximum demanded normalized source-to-target action amplitude before
projection: **1.6308782249689098** (seed 20002, step 4).
The reported 30 non-exact actions were labeled
`APPROXIMATE_BOUNDED_PROJECTION`, not certified
exact desired-goal reproduction. Under the bounded mode, each
position native component is projected to [-1,1], and the rotation
vector to the unit Euclidean ball, the representability constraint of
ManiSkill's target controller native interface in this configuration.
This is an ordinary Euclidean projection, not an optimal
long-horizon controller, global task planner or geodesic SO(3)
projection certificate.

## Mechanism and limitations

The action conversion's runtime dependency and feasibility boundary are
demonstrated with a *real frozen learned policy*, not only scripted
actions. Exact one-step interface conversion fails in 27/32
cases because of per-step action limits; bounded approximation and
continued policy feedback recovered 32/32 executions in one
prespecified pilot. The intervention changes requested actions and
does not maintain exact trajectory identity.

What it **does not** establish:
- task success on other tasks/robots/control families;
- independent third-party reproduction;
- formally proven robotics safety or universal guarantees;
- learned controller contracts from unknown black-box actions;
- novelty of generic frozen-policy adaptation or simple saturation,
  which are existing ideas;
- statistical superiority to the source based on one 32-seed run.

Separate reproducibility audit already exposed incompatible single-seed
outcomes for a different controller swap (seed 10014, one job failed,
another succeeded). Accordingly, for a future paper, reproduce this
32-seed target-memory result on **independent CI runners with complete
initial observation SHA and pinned dependency versions**, plus a
separate preregistered task/policy holdout and longer contact-rich
horizons.

## Reviewer falsification paths

1. Verify exact published SHA and all 32 original log lines in the CI.
2. Replay the exact branch pinned to the workflow `head_sha`.
3. Replace goal-memory reads with achieved-only pose: test whether the
   same bounds action can be recovered (the naive arm is a no-adapter
   baseline, not achieved-only memory inversion; a tighter second
   baseline is still required).
4. Compare simple clipping with the state-aware projected controller,
   and a reachable-oracle target controller at matched step budgets.
5. Validate scene-independent environment seed reproducibility and
   report divergent samples, not just success aggregates.

**External adoption, official upstream acceptance, independent
replication and a top-tier-paper acceptance remain unverified.**

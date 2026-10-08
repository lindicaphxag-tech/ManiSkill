# Preregistered frozen PPO target-memory feasibility holdout (2026-10-08)

## Scope and data split
The four earlier development seeds [42,270,429,2026] showed:
source 4/4, exact/refuse 2/4, bounded non-exact memory-aware projection
4/4, direct copy 1/4. This is **development evidence only**.

Before launching this holdout, fix these 32 **new** environment seeds:
`18001,...,18032` inclusive. The four-arm code/threshold is inherited
unchanged from validation/frozen-ppo-memory-feasibility-fallback-20261008,
except for the seed tuple and workflow branch trigger.

- External pretrained and frozen public PPO:
  `kattri15/actionshift-baselines/ppo/pick_cube_final_ckpt.pt`
  SHA256 `3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8`.
- Task: ManiSkill PickCube/Panda, real PhysX CPU, max 50 steps per arm.
- Same 32 initial seeds, initial 42D *projected policy observation*
  equality explicitly checked. Target controller adds 7D target memory
  to its raw proprioception; source-trained PPO only receives canonical
  42D observation, and the 7D runtime target memory is used by the adapter.
- No training or policy fine-tuning, own-world policy inference each step.

## Four predeclared arms
1. Source: `pd_ee_delta_pose` native PPO.
2. Exact memory-aware: `pd_ee_target_delta_pose`; refuse if required
   target-relative translation or rotation is outside target's native limits.
3. Bounded memory-aware **approximation**: same target, but on infeasible
   source physical targets project position native delta to [-1,1] box
   and rotation native delta to the unit norm ball. MUST label every
   approximation `NOT_EXACT`; no assertion of pose equivalence.
4. Naive: same target, directly copy the PPO delta actions, no memory
   inversion.

## Frozen outcome metrics (do not tune)
- Unconditional per-arm task `success_once` / 32, exact and nonexact
  cases BOTH included in the denominator.
- Pairwise source/strict/projected/naive success table; at each paired
  seed, retain all four results even on failures.
- Number of episodes with strict refusal and its step/amplitude;
  count projection steps and per-episode maximum required native amplitude.
- All actual episode steps and error states; if any arm's initial scene
  differs by >5e-4, report INVALID, not unsuccessful task execution.
- Effect is interpreted as exploration within a single task + policy,
  NOT a guarantee of safety or exact behavior preservation.

## Novelty / external validity boundary
This tests an observation ABI projection plus stateful controller-goal
memory plus representability-aware choice (exact/refuse/projected).
The components overlap prior control saturation and action adaptation
literature. Scientific novelty requires stronger prior-art review,
longer contact-rich tests, distinct task/controller/robot, and
independent adoption. Do not claim L8/L9 or independent support on the
basis of 32 author-run simulations.

Original development code:
https://github.com/lindicaphxag-tech/ManiSkill/tree/validation/frozen-ppo-memory-feasibility-fallback-20261008

Four-seed development result:
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37717601656

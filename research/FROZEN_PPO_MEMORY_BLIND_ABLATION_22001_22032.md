# Pre-registered 32-seed state-memory ablation — frozen PPO PickCube

This protocol was committed **before the ablation implementation and before running its results**. New source seed IDs `22001..22032` are disjoint from the already observed `20001..20032` development and `21001..21032` successful prospective test. No seed cherry-picking.

## Motivation and specific identification question

The previously observed PickCube target-controller transfer used **two coupled ideas**: (i) invert the *actual previous controller target memory*, and (ii) bound the resulting target-native action with a box translation plus Euclidean-ball rotation projection. Its naive direct-copy control lacks both. Therefore the previous large 32/32-versus-0/32 effect alone does NOT establish that reading live previous-target state matters, independently of projection.

**Isolated ablation**: give a `memory_blind` target controller exactly the same frozen pretrained PPO, projected 42D observation contract, *source action normalization, root frame*, inverse/normalization code and bounded projection as `projected`. Make ONE semantic change: during inverse translation compute with `old_pose_override=target_arm.ee_pose_at_base` (an erroneous assumption that prior controller target equals current achieved pose), instead of using `target_arm._target_pose`. The real `pd_ee_target_delta_pose` simulator must still execute the action relative to its *actual* previous target memory; do not edit the real controller state. This makes the ablation plausible yet physically wrong, allowing direct isolation of stateful memory use.

## Frozen mechanics and exact task

- Source code from previously validated branch at `2a1c2e739c234098e2d08b0e5633026c05aaf721`. Source file `research/frozen_ppo_target_memory.py` blob `c1b1b2dcd39e549a91f99540ba9cd05bc7bae51e`.
- Fixed external third-party PPO `kattri15/actionshift-baselines/ppo/pick_cube_final_ckpt.pt`; SHA-256 `3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8`. **No training / updates**.
- Real ManiSkill `PickCube-v1`, `state`, `physx_cpu`, `num_envs=1`, each arm receives same predeclared seed, `reconfiguration_freq=1`, 50-step horizon and official `info['success']`.
- Arms: native `source`; strict exact-only `memory`; full memory-aware bounded `projected`; intentionally broken "memory_blind" bounded target; raw source action `naive`. All target arms must verify identical source-projected initial task observation.
- `memory_blind` controller is a *controlled ablation*, not a proposed deployable fix. It has access to the actual achieved pose, but **not** to previous controller goal memory in its inverse equation. There may still be target-pose entries in the environment observation; the policy always receives only projected 42D source-compatible states.

## Pre-declared evidence and stop/go tests

1. Every seed `22001, 22002, …, 22032`, exactly once. Any missing or unexpected seed => reject the aggregate. A successful task means official `info['success']` achieved within 50 physical simulation steps.
2. Competent source: **>= 24 / 32**; full stateful method ≥ **24 / 32**; else abort improvement claims.
3. Primary mechanistic difference: full `projected` minus `memory_blind` ≥ **12 / 32 net successes**. Paired discordants `full-only` and `blind-only` must be reported. This is a prospective threshold, not a post-hoc significance claim.
4. Report source, strict, projected, blind and naive counts, any strict refusals, number of projection actions **separately for projected and blind**, their required native amplitudes and initial-state identity. Do not reclassify `APPROXIMATE_BOUNDED_PROJECTION` as exact.
5. All arms use the *same checkpoint* and unchanged controller code; the adapter change should be limited to the ablation-flag and the new arm. The complete previously accepted `projected` code path must be functionally unchanged. If existing result differs from previously observed 20001–20032, retain and report the difference.
6. Store each per-seed result, commit/weights SHA, source blob and action bound model. **No real robot safety** conclusion from task success.

This is developer-operated CPU PhysX, not unrelated third-party replication, unknown morphology robustness, large-scale VLA training, or a proof that bounded approximation is safe. The method's exact and approximate branches retain different authority/equivalence meaning.

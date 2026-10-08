# Frozen PPO stateful controller transport: PullCube and StackCube prospectively fixed pilots

Registered before either 32-seed experiment runs. Separate 32-seed pilots,
report unconditionally regardless of source-policy competence or outcomes.

## Fixed comparisons and source provenance

Same already-implemented algorithm used for PickCube and PushCube.
**No algorithm tuning, clipping threshold changes, policy retraining, or
after-the-fact seed/horizon changes**. Each task uses its separate public,
frozen ActionShift PPO weights, and the *exact same* four controller arms:

1. original source achieved `pd_ee_delta_pose`;
2. destination target-relative `pd_ee_target_delta_pose` with live goal
   memory and exact-or-refuse semantics;
3. same destination with live goal memory and bounded nonexact action
   projection (clip translation box, scale normalized rotation to unit ball);
4. same destination receiving unconverted source-native actions, retaining
   proper 7-D controller observation projection for policy input.

The policy actor runs on each environment's own observations, always
unchanged. Controller state is used by the action compiler, not mistaken
for policy training observations.

### PullCube-v1

- Checkpoint `ppo/pull_cube_final_ckpt.pt`, verified SHA256
  `74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7`.
- 32 exact prespecified seeds `40001,40002,...,40032`.

### StackCube-v1

- Checkpoint `ppo/stack_cube_final_ckpt.pt`, verified SHA256
  `e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c`.
- 32 exact prespecified seeds `50001,50002,...,50032`.

## Common protocol and stop conditions

ManiSkill v3.0.1, Panda, real SAPIEN/PhysX CPU, `obs_mode=state`,
max **50 steps** per episode, 4 arms per seed. That 50-step budget may
be inadequate for the harder StackCube task. Do **not** extend it after
seeing the failures; if original source succeeds rarely, report a
source-competence limitation rather than claiming policy transfer failure.

For every task include all 32 per-seed outcomes, source competence, exact
refusal count and required amplitude, bounded projection action count,
concrete target/controller observation ABI lengths, any invalid initial
state comparisons, and exceptions (never score exceptions as task 0).
Require initial policy-visible state to match within 5e-4 after a verified
7D controller-goal slice is removed from target observations.

The trained policies and generic delta/absolute conversions are prior
art. This is an experimental *controller memory + observation contract +
native feasible action set* portability test, not a safety theorem or
novel neural architecture. Re-run on independent machines / confirm
full physical initial-state hashes before asserting stable per-seed
repeatability, especially in light of earlier seed10014 batch mismatch.

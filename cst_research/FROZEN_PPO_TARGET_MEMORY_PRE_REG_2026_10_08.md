# Frozen PPO target-memory controller transfer — exploratory preregistration

Date 2026-10-08; established BEFORE first `pd_ee_target_delta_pose`
learned-policy experiment. Not the 32-seed holdout.

## Hypothesis and relevant novelty

A policy trained with `pd_ee_delta_pose` assumes each action increment
starts from **achieved current EE pose**. The ManiSkill
`pd_ee_target_delta_pose` controller instead composes incremental actions
from its controller-owned **previous target pose** (`_target_pose`).

For the same frozen, competent public PPO checkpoint, raw unconverted
native actions should not be treated as ABI-equivalent. A runtime
compiler can, in principle, reconstruct the desired achieved-relative
goal then express it as a delta **relative to the target's previous desired
pose**, if and only if the necessary delta remains representable within
the destination native control bounds.

## Fixed exploratory experiment

- Same checkpoint as earlier 4/4 source competence:
  `kattri15/actionshift-baselines/ppo/pick_cube_final_ckpt.pt`,
  SHA256 `3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8`.
- Four *development* seeds 42,270,429,2026 (do not call them holdout).
- Three Panda/PickCube PhysX CPU environments, identical initial states
  checked before rollout, 50 steps max:
  1. Source PPO `pd_ee_delta_pose` (achieved-relative).
  2. Same frozen PPO under `pd_ee_target_delta_pose`, with
     runtime target-memory `_target_pose` read each step to compile
     action in *target-relative* coordinates.
  3. Same frozen PPO under `pd_ee_target_delta_pose`, directly applying
     policy-native action without memory-aware conversion.
- Each environment runs policy inference on its **own** observations.
- The compiler must refuse actions that cannot be expressed in the
  target native bounds instead of silently clipping while claiming exact.
- Every episode records success, refusal, exception, length, and the
  max required normalized action amplitude.
- Original source has already shown 4/4 CPU task competence; no
  new training/finetuning allowed.

## Honest failure modes

- `_target_pose` absent or incompatible / orientation representation
  mismatch -> invalid execution or explicit refusal.
- Desired target out of target-controller action range -> **refusal**
  not counted as success, report exact refused episode count.
- Divergent initial observations -> **invalid comparison**, not 0%.
- Success parity on 4 episodes only an engineering smoke, not a
  statistically meaningful task success estimate or conference novelty.
- A frozen PPO under changed controller is not the same as a universal
  safe-robot controller migration; ActionShift and other prior works
  already address generic action-interface adaptation.

The 32-seed delta->absolute policy transfer holdout was separately
preregistered and is **not** used to tune this state-memory experiment.

# PushCube frozen PPO: independent-task controller memory ablation

**Public successful CI:** https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37752524225

**Frozen before run:**
[FROZEN_PUSH_CUBE_MEMORY_CROSS_TASK_PREREG_2026_10_08.md](FROZEN_PUSH_CUBE_MEMORY_CROSS_TASK_PREREG_2026_10_08.md)

**Code for exact CI run:**
https://github.com/lindicaphxag-tech/ManiSkill/blob/validation/frozen-ppo-pushcube-memory-cross-task-20261008/research/frozen_ppo_target_memory.py

## Independent task and provenance

This is a **new manipulation task** PushCube-v1, not another PickCube
initialization split. It uses a **different**, externally trained
ActionShift PPO frozen checkpoint: 
`kattri15/actionshift-baselines/ppo/push_cube_final_ckpt.pt`,
SHA256 `a4a02198b309e73cb877959079023d967d5f63ec78380de9703a10c9efafc0cf`.

PushCube source observation ABI = **35D** (reported by CI), target
= **42D** with a distinct seven-value target-pose controller memory.
The compiled PPO input is checked to preserve the true 35D layout
including task-specific features. All projected target initial
observations matched source initial observations within the
fixed threshold; all 32 designated seeds `40001..40032` completed.

Official ManiSkill Panda/PushCube-v1, PhysX CPU, max 50 steps per
episode. All five arms execute their *own current* frozen policy
observations and take real physics actions. No gradients or retraining.

## Unconditional 32-seed results

| Arm | Successes |
|---|---:|
| Original PPO source (`pd_ee_delta_pose`) | **30/32** |
| Stateful previous-goal memory + bounded projection | **30/32** |
| Stateless achieved-only instead of previous goal + same projection | **20/32** |
| Stateful exact-only / refuse | **28/32** |
| Raw PPO native action copy | **20/32** |

For the primary paired stateful vs stateless comparison:
- **11** seeds: memory-aware only succeeds;
- **1** seed: achieved-only succeeds, memory-aware fails;
- **19** seeds: both succeed;
- **1** seed: neither succeeds.

Important: **do not** suppress the one stateless-only success or two
memory-aware failures. Both are part of the preregistered cohort.

The stateful exact-only compiler refused **two** episodes on a
nonrepresentable target-native action. Bounded projection took
**two** non-exact action steps in all 32 episodes; stateless projected
method recorded **zero**. Thus the effect of controller-history
semantics appears even in a task where severe action
representability deficits are relatively uncommon.

## Joint interpretation across tasks (not pooled as same population)

A separate PickCube disjoint 32-seed ablation reported
stateful projected 32/32 vs achieved-only stateless 2/32.
This PushCube replicate gives a *smaller, nonzero* advantage
30/32 vs 20/32 using a **different trained checkpoint** and
task while retaining Panda's controller family.

This supports that live target history is an execution-relevant
component of the learned-policy→controller interface rather
than merely a per-task code accident. It **does not** prove
universality, cross-robot transfer, safety, or a new generic
mathematical notion of stateful controllers.

The source PushCube PPO itself succeeds 30/32. Outcome differences
are from exploratory author-run paired CPU simulations, **not**
independent community replication or a blinded multi-group trial.
Action projection is elementary, not claimed as a novel solver.

## Follow-up

- Replicate on a *different robot/controller family*, not merely
  another Panda task with same semantics.
- Pin and share exact dependencies and container image; test
  reproducibility under fresh-run processes with state fingerprint.
- Include a principled residual/feasibility certificate for
  approximate stateful actions and explicit refusal conditions.
- Obtain upstream maintainer code review and external independent
  reproduction; no upstream acceptance is implied here.

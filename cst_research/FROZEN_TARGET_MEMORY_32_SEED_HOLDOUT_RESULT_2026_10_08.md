# True frozen PPO — stateful target-controller feasible-set holdout

Canonical public CI (succeeded; 32 per-seed records):
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37751001239

Protocol published **before run**:
[FROZEN_TARGET_MEMORY_32_SEED_HOLDOUT_PRE_REG_2026_10_08.md](FROZEN_TARGET_MEMORY_32_SEED_HOLDOUT_PRE_REG_2026_10_08.md)

Public exact test code:
https://github.com/lindicaphxag-tech/ManiSkill/blob/validation/frozen-ppo-target-memory-32-holdout-20261008/research/frozen_ppo_target_memory.py

## Controlled setting

Official ManiSkill Panda/PickCube-v1 task, `pd_ee_delta_pose` source
vs `pd_ee_target_delta_pose` destination, CPU PhysX. Third-party public
ActionShift-trained PPO, **weights unchanged**, SHA256
`3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8`.

32 **new** pre-selected seeds `20001..20032`, four independently
stepped environments per seed. Native PPO input observation contracts:
source 42D; target 49D from added 7D target-pose memory. The target's
extra controller state was verified then projected out **only from
PPO input**; the execution compiler could still read it. Every
arm's initial projected policy observation matched exactly
(`initial_obs_diff=0`) within each paired seed.

Four arms:
- Original PPO in achieved-relative `pd_ee_delta_pose` (source).
- Live previous-target memory with **exact action requirement**, abort
  on out-of-bounds controller native command.
- Live previous-target memory with **non-exact bounded projection**
  (translation box, SO(3) rotation native-action Euclidean ball),
  explicitly logging each inexact action.
- Directly replay the raw PPO command into the target action chart
  (**not** semantic translation).

## Unconditional results

| Arm | Success / 32 | Fail or refuse |
|---|---:|---:|
| Source frozen PPO | 31/32 | 1 |
| Stateful **bounded projection** | **32/32** | 0 |
| Stateful **exact-only / refuse** | 5/32 | 27 refused |
| Direct native-action copy | 3/32 | 29 |

Exact-only refusals: **27/32** seeds. Bounded projection used
**30** explicitly non-exact action corrections in total across
the 32 runs. No detected dropped seeds, no post-hoc task success
denominator changes.

Source fails once at seed **20016**, where the stateful bounded
projection succeeded in step 36 after four non-exact command
projections. This is *an observed difference*, not evidence that
projection is a generally superior trained policy.

The 32-seed trial is an **exploratory holdout on one task and
one pretrained third-party policy**. The successful bounded
projection method was devised after examining four earlier
development seeds 42/270/429/2026, but *before* the disjoint
32-seed cohort was observed.

## What is new evidence, and what is not

- The **controller target memory** changes the meaning of otherwise
  valid native deltas. Exact action conversion alone may become
  infeasible after previous-target accumulation.
- Feasibility must be considered as part of the executable interface:
  **exactly encodable**, **bounded non-exact fallback**, **refusal**.
- Bounded Euclidean projection and target pose bookkeeping are
  straightforward known optimization/control mechanisms; the author
  does **not** claim they are original first-in-literature algorithms.
- Task success **does not** certify that non-exact commands preserve
  the intended source physical trajectory, nor robot hardware safety.
  Confidence intervals and multi-task policy generalization are
  not yet established.

## Must-have falsification before a flagship contribution

An **otherwise identical action transformation that does NOT read
previous-target controller memory**, using achieved EE pose instead
but preserving exact same bounds/projection and observation ABI.
The separate preregistration is
[FROZEN_STATE_MEMORY_ONLY_ABLATION_2026_10_08.md](FROZEN_STATE_MEMORY_ONLY_ABLATION_2026_10_08.md).
Without it, the 32/32 result cannot attribute the benefit specifically
to controller-owned memory rather than ordinary bounded action
adaptation.

Independent third-party replication and upstream maintainer adoption
are likewise still unverified.

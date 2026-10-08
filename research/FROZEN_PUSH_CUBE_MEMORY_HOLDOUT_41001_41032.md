# Prospective non-overlapping PushCube closed-loop transfer holdout

**This document is committed before modifying runner seeds and before
executing the new 41001–41032 result.**

## Frozen source / known development results

- Derivative of public real PhysX PushCube experiment
  [37752524225](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37752524225),
  source commit `2225bfa1f2b41adf293e308b1e1158ecb1c6c6c9`.
- Exact executable file:
  `research/frozen_ppo_target_memory.py` at that source commit.
- Third-party *frozen* policy:
  `kattri15/actionshift-baselines/ppo/push_cube_final_ckpt.pt`,
  SHA-256 `a4a02198b309e73cb877959079023d967d5f63ec78380de9703a10c9efafc0cf`.
  No fitting, updates or adversarial reselection of trained policy.
- Source = `pd_ee_delta_pose`; target = `pd_ee_target_delta_pose`;
  all real simulator environments use `PushCube-v1`,
  `state`, `physx_cpu`, `reconfiguration_freq=1`,
  50-step max horizon. All comparison arms start from equal
  checked physical-task observations and then run independent dynamics.
- Control variants: source original; target memory-aware exact-only
  compiler with out-of-bounds refusal; target memory-aware compiler
  with **inexact bounded projection**; target direct-copy naive and
  (where present) target-memory-free stateless baseline.
- **KNOWN already** development seeds 40001–40032 yielded
  source **30/32**, strict exact-only **28/32**,
  bounded projection **30/32**, naive **20/32**,
  stateless **20/32**. Strict refused in 2 episodes and projected
  used 2 non-exact steps. These results are *not* new validation.

## Held-out seeds and acceptance locked BEFORE test

1. Evaluate precisely the 32 integer seeds **41001–41032**;
   no replacement for cases that fail, no missing-case exclusion.
   This cohort has zero overlap with the 40001–40032 development seeds
   or the PickCube 20001–20032 and prospective 21001–21032 seeds.
2. Modify only `SEEDS=tuple(range(40001,40033))` to
   `SEEDS=tuple(range(41001,41033))` in source Python,
   plus workflow event branch name. No changes to adapter,
   projector, physics/backend, checkpoint or initial-state guard.
3. Competent original source: must succeed at least **24/32**.
4. Useful holdout transfer: projected target must outperform
   target naive by at least **8/32 net paired successes**. Publish
   source, exact-only, projected, naive, stateless, and all refusals.
5. Every approximate projection must be labeled NON-EXACT,
   never credited as an exact action contract certificate or
   a physical safety guarantee. Do not use the green CI conclusion
   in place of genuine per-seed task outcomes.
6. Failed threshold, null result or worse results stay public;
   no amendment after seeing heldout measurements.

## Generalization/novelty boundaries

This and separately preregistered PickCube holdout would establish
repeatability of a **single algorithm idea on two real simulator
tasks and two released third-party checkpoints** if they succeed.
It would not establish independent upstream adoption, VLA recovery,
new robot embodiments, cross-morphology physical generalization,
safe real-world actuation, or new mathematical invention of
inverse action transforms and box/ball projection.

Methods and prior art: ManiSkill `use_target` changes controller
reference pose semantics, and absolute/delta action-space
design and learning are existing research topics. The proposed
newer contribution needs substantive safe identification/synthesis
under unknown control mapping plus cross-task policy recovery,
not merely porting the published controller equations.

# Frozen-policy controller-owned goal-memory transport: 32-case prospective pilot

**Status: completed, author-run, one task / one public pretrained PPO.**

**Published prespecified protocol (before outcomes):**
[FROZEN_PPO_DESIRED_32SEED_PROTOCOL_20261009.md](FROZEN_PPO_DESIRED_32SEED_PROTOCOL_20261009.md)

**Canonical public run including all 32 machine logs:**
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37812225529

**Executable real-simulator source:**
https://github.com/lindicaphxag-tech/ManiSkill/blob/validation/frozen-ppo-desired-holdout-20261009/research/frozen_ppo_target_memory.py

## Method and exact scope

A third-party **already-trained frozen** ManiSkill PPO (ActionShift,
SHA256 `3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3ef8497a8`)
is evaluated in real PickCube-v1 Panda PhysX CPU simulation. It is never
retrained. 32 distinct prespecified nominal integer reset seeds
`20001..20032`, max 50 steps, compared in the same CI.

Source uses `pd_ee_delta_pose` (current achieved-pose-relative commands).
Target uses `pd_ee_target_delta_pose` (controller previous desired-target
relative). Target observations contain 7 extra controller-memory features;
the trained PPO consumes a **verified 42-D observation projection** while
the live 7-D target memory remains available to the action compiler.

Four arms are tested for every seed:
1. Source unmodified frozen PPO.
2. Stateful **strict/refuse**: compile desired pose to target-relative
   delta; reject if required normalized position/rotation exceeds native
   bounds.
3. Stateful **bounded approximate**: when strict mapping is unrepresentable,
   project normalized Cartesian position into its box and normalized
   Euler-vector into its unit L2 ball. Logs every such action as
   **NOT_EXACT**; no assertion of universal equivalence.
4. Naive target controller with direct native action copy, no memory
   compensation.

Within-run initial projected observation differences are **0.0** across
all three target arms in all 32 cases; all seeds have results and none
are excluded.

## Full unconditional results

| Arm | Successful / 32 | Percentage |
|---|---:|---:|
| Source frozen policy | **31 / 32** | 96.875% |
| Stateful exact-or-refuse | **5 / 32** | 15.625% |
| Stateful bounded approximation | **32 / 32** | 100% |
| Naive raw native action | **3 / 32** | 9.375% |

- **27/32** strict/refuse episodes halted when a desired one-step goal
  exceeded the target controller's native command limits.
- **27/32** bounded-approximation episodes needed some projection.
- In total **30 / all executed policy steps** used a non-exact projected
  command; every projection is retained in its episode's raw record with
  the triggering step and required native amplitude.
- Largest native amplitude observed in the run: approximately
  **1.631** (seed 20002); target native limit is 1.0.
- Distinct projected successes not achieved by naive: **29**; naive-only
  successes: **0**.
- Source-only successes vs projected: **0**; projected-only successes:
  **1** (seed 20016). That one seed has source timeout at step 50
  while projected completed by step 36 after **four** approximate actions,
  so it is not evidence of generally superior policy performance.

## Caveats critical to research integrity

- This result is real **CPU simulator feedback with a frozen neural
  policy**, not training, not hardware, not independent external replication.
- Projection makes the *next goal different* from the exact requested
  source target. The data show task recoveries, **not exact simulator
  bisimulation, guaranteed execution equality or safety**.
- Clipping/projection is a standard baseline operation; novel
  contribution is not the primitive alone. Current evidence tests a
  restricted executable coupling of observation ABI, controller-owned
  previous goal memory, native action feasibility and explicit refusal.
- Prior ActionShift and control/adaptation literature must be credited.
- A different 32-seed delta->absolute pilot was once 31/32; nominal
  seed 10014 did NOT reproduce the failure on independent reruns.
  Thus one integer reset seed is NOT a verified full scene identity;
  even here all comparisons are verified **within** each seed/CI run,
  and cross-run initial-state/environment reproducibility remains
  an open issue. See
  [seed-10014 reproducibility report](FROZEN_PPO_SEED10014_REPRODUCIBILITY_20261009.md).
- Seed selection was recorded before viewing outcomes but the runtime
  and hyperparameters were developed on the four earlier seeds;
  call this a prospective **pilot**, not an untouched fully independent
  benchmark or statistical guarantee.

## Next representative-work milestone

Use a **complete replayable simulator snapshot** and controller-state
certificate, not an integer seed alone. Freeze the final method and
compare on a different policy, task and robot/controller family; include
feasible/infeasible target goal geometric residuals; obtain independent
CI reproduction or upstream maintainer review. Only then evaluate a
research-conference or high-value open-source flagship claim.

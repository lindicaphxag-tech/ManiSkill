# Registered prospective 32-seed pilot: state-memory transport under native action limits

**Protocol deposited BEFORE 32-seed pilot CI is launched.** Four developmental
seeds 42,270,429,2026 have already been observed and are excluded from
the new pilot denominator. Separate action-chart swap pilot used
10001–10032 and does not enter this analysis.

## Fixed evaluation

- Seeds **20001 through 20032 inclusive**, in ascending order. 32 episodes.
- Task PickCube-v1/Panda, `obs_mode=state`, PhysX CPU, max 50 steps.
- Exactly identical published frozen ActionShift PPO checkpoint SHA-256
  `3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8`.
  No policy training, fine-tuning or adaptive updates.
- Three target-memory controller arms and original source, each with its
  own current environment observations but the **same frozen policy**:
    1. `source` achieved-relative `pd_ee_delta_pose` PPO, 42-D obs;
    2. `memory` target-relative `pd_ee_target_delta_pose` with live
       previous goal, exact action conversion or fail-closed refusal;
    3. `projected` same runtime goal memory, with bounded one-step
       native-action projection when the desired incremental target is not
       representable; this is **not exact semantic equivalence**;
    4. `naive` raw PPO action into `pd_ee_target_delta_pose`.
- Targets expose controller goal state appended to proprioception
  (49-D). Project the observation ABI to the source PPO's 42-D input
  by specifically verifying and removing the 7-D controller-memory
  field while keeping full task extra observation fields.
- Paired initial projected policy observations must agree within 5e-4
  or experiment is invalid.

## Precommitted outcomes

Report all 32 per-seed results and four unconditional success counts,
the number of exact refusals, number of projection intervention steps,
peak normalized action amplitude, and all failed/range-exceeded seeds.
If a task cannot execute because of API/physics exceptions, report an
integration error separately; do not score it as a legitimate task
failure or silently omit it. The native projection clips each Cartesian
component to [-1,1] and scales rotational normalized vector onto the
unit ball if necessary; this baseline is **simple bounded projection**,
not a new optimization algorithm.

Do not report an apparent win over exact refusal as evidence of
improved "exact transport" — these procedures have different contracts.
Compare task completion of projected vs raw-copy with full episode data.

## Known prior 4-seed results (not holdout)

- source 4/4
- exact+refuse 2/4, two out-of-range refusals with amplitudes ~1.42/1.62
- projected 4/4, two approximate steps
- raw-copy 1/4

Prior implementation/CI:
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37717601656

## Reproducibility and novelty caution

A separate seed10014 audit found inconsistent outcomes between the
original *32-seed sequential batch* and standalone execution of a
nominally identical seed. Therefore this 32-seed pilot is a **single
batch estimate, not a guarantee of deterministic per-seed replay**.
Record full build/runtime identity; request independent repetitions.
Even a perfect result does not by itself establish novelty over
established action-space conversion and bounded projection work.

Demonstrating a new scientific mechanism requires proving that
controller-owned memory is causally necessary under matched state,
showing the correct physical goal is preserved when feasible, and
testing rejection behavior on unseen unsupported controllers.

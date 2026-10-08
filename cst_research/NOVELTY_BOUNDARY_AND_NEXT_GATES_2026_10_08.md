# CST: what is and is not scientifically new — 2026-10-08

This is a **conservative novelty and external-recognition audit**, not a
peer-review decision or a guarantee of acceptance.

## Work that narrows novelty claims

- ManiSkill #429 already reports the **NumPy vs torch clipping bug** in its
  original 2024 issue description. We must **not** claim discovery of that
  bug; the fresh contribution is an executable upstream patch and
  controlled official-data reproductions, especially correct re-encoding in
  the target controller action chart:
  https://github.com/mani-skill/ManiSkill/issues/429

- [ActionShift](https://github.com/Archerkattri/actionshift) studies hidden
  action-interface grammar (permutation, sign, scale, delta/absolute,
  reference frame, delay, gripper convention) and adapts frozen PPO /
  diffusion policies with probing, belief, learning and timing effects.
  The idea of **frozen robot policy + action adapter**, interface grammar,
  contract inference and evaluation is therefore **not** ours to claim
  broadly.

- [Tune to Learn](https://arxiv.org/abs/2604.02523) concerns how robot
  controller gains shape learnability; gain variation/selection by itself
  is not our research novelty.

- [ReStruct](https://arxiv.org/abs/2606.26588) adapts behavior of a
  frozen policy by modifying task structure and residual-control priors.
  Generic inference-time steering with frozen weights is not unique.

- The mathematical notions of simulation relations, bisimulation,
  robust tracking bounds, action-coordinate changes and inverse
  kinematics are established background. Do not claim their invention.

## Precise research hypothesis still worth testing

**Runtime-state-complete compilation of controller interfaces**:
Given an unchanged policy and two *real implementations* of low-level
controllers, recover the native action chart AND minimum controller-owned
state that is needed to execute the same goal/torque/physical trajectory.
Generate a runnable adapter and refusal diagnostics based on executable
contracts and actual runtime state, not on a black-box score alone.

The key issue is state/history:
- `OSC_POSE` delta with `achieved` update can be mapped from current
  measured pose; joint controller zero-space `initial_joint` still needs
  migration for matching torques.
- `OSC_POSE` delta with `desired` update needs the *previous desired goal*;
  it may be unidentifiable from independently restored physical states.
  However, a **live step hook** can read that goal memory and compile an
  absolute target without retraining the source policy.
- Compiler acceptance must be local and conditional: same MJCF, selected
  controller family, matched gains/reference frames, supported memory,
  restricted action range, a declared finite horizon.
- A rejected conversion must not mutate the destination controller; if a
  partial write happens, rollback is verified, otherwise quarantine.

This is a strong *implementation-level research hypothesis*. Existing
literature and comprehensive prior-art search are needed before claiming
conference-level novelty.

## Actually passed evidence

1. Official ManiSkill PickCube RL replay with patch: **4/8 successful
   on CPU**, while unmodified baseline crashes on NumPy/Torch mismatch.
   This does not measure a success-rate improvement over a valid baseline:
   https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37709660093
2. Real Panda/Lift+Stack **six** matched-MJCF, 8-step rollout trials;
   full-scene qpos maximum discrepancy approx `2.03e-7`.
   https://github.com/lindicaphxag-tech/robomimic/actions/runs/37713698317
3. Transactional `initial_joint` handshake with explicit
   post-write-check, rollback and quarantined failure; **94 unit tests
   passed** in the corresponding research suite:
   https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37713542550
4. Online desired-goal step-hook compiler:
   **99 unit tests passed** on the current CST research branch;
   real Panda desired-mode integration is still under independent CI
   validation at the time of drafting:
   https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37714080201

## Pinned scientific decision gates

**Go to major top-tier flagship study ONLY IF all hold:**
1. Use at least one public, real **frozen trained PPO or BC checkpoint**;
   no fine-tuning after controller swap.
2. Run multi-task paired trials with at least two distinct controller
   implementations and holdout scenes; do not collapse multiple action
   seeds from one scene into "independent environment seeds".
3. Ablate direct native-action copy vs type-only correction vs
   action-chart adapter vs state+action adapter. Each must actually run,
   or classify as execution failure rather than reporting 0% success.
4. Quantify runtime refusal and harmful accepts on unsupported modes
   (`desired` without live state, variable impedance, interpolation,
   saturated actions, incompatible MJCF/gains).
5. Freeze a reproducible artifact with exact code/environment/data hash
   before observing final holdout outcomes.
6. Obtain third-party code review, merge or independent reproduction
   of a **matching** mechanism rather than only generic upstream fixes.
7. Demonstrate a benefit that cannot be explained by simple API shape
   correction, new controller gains, scene reset or a baseline bug.

**Not achieved:** maintainer adoption of the CST research mechanism,
independent replication, hardware validation, universal proof, L8/L9
status or paper acceptance.

## External response triggers

- ManiSkill #429: prepared minimal 2-file patch. The project requires
  maintainer thumbs-up on the issue **before** PR.
- robomimic #270: maintainer invited absolute->delta converter PR,
  but upstream official PR is **not open**.
- LeRobot #3312: maintainer invited ACT relative-action support PR,
  but upstream official PR is **not open**.

The installation-connected GitHub app can push to the author's forks
and personal repo but upstream PR/comment attempts returned HTTP 403.
Manual user publication is therefore a genuinely necessary gating step.

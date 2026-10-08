# 2026-10-08 novelty audit: the real claim is state-complete executable migration

This note is a conservative research-priority audit, not a claim of precedence.

## Closely related work that narrows the available novelty

1. **SPACE: Enabling Learning from Cross-Robot Data Toward Generalist
   Policies** (Lee et al., arXiv:2606.24049, June 2026).
   State Prediction and Adaptive Command Execution uses a Cartesian
   state-delta policy and action adapter to handle different embodiments,
   control frequencies, gains, and online dynamics changes.
   https://arxiv.org/abs/2606.24049

2. **TAM: Torque Adaptation Module for Robust Motion Transfer in
   Manipulation** (CoRL 2026 Spotlight).
   Learns residual torque corrections between the low-level controller and
   plant. Policy-agnostic across joint targets, EE targets and torques.
   https://dongwon-son.github.io/tam-project-page/

3. **Meta-Control: Automatic Model-based Control Synthesis for
   Heterogeneous Robot Skills** (CoRL 2024 proceedings, published PMLR 2025).
   Automatically synthesizes task-specialized model-based controllers.
   https://proceedings.mlr.press/v270/wei25a.html

These works occupy substantial portions of generic "action adapter",
"controller transfer", "dynamics adaptation", and "automatic controller
synthesis" novelty. Do not claim these ideas as inventions here.

## New empirical impetus: controller target equivalence is not enough

Public real robosuite 1.5.2 / MuJoCo 3.3.0 Panda/Lift evidence:

- 10 steps with real OSC goal generation: native round-trip maximum
  approximately 1.57e-15; goal-position maximum 0; goal SO(3) maximum
  approximately 1.05e-8 rad.
- A naive two-environment full-state paired rollout showed near-equal
  controller goals (approximately 5e-9) but different qpos after 8 steps.
- Source and target OSC had different `initial_joint` posture references,
  even when the MuJoCo flattened state was copied exactly.
- The actual robosuite OSC code adds nullspace torque around
  `initial_joint`. Therefore that memory is executable control state.
- A state-handshake run showed near-matching first-step actuator controls,
  but full-scene object dynamics remained different; the cause is not yet
  isolated across identical simulation models and complete solver state.

Treat different random initializations and model/data instances as confounds.
Do not claim causal effect size across separate randomized runs.

## Narrow flagship research claim to validate

**State-Complete Controller-Interface Migration for Frozen Robot Policies**

A deployment compiler extracts two executable controller contracts, including
both native action chart and controller-owned memory. It either:

1. synthesizes a state+action adapter preserving explicitly declared goal,
   torque or rollout observables over a certified scope; or
2. returns a concrete non-representability, state-incompatibility or saturation
   witness and refuses exactness.

The interesting result is NOT that "controllers have hidden state", NOR
that "a simulation relation exists" (classical). It is whether a
mechanically extracted, actionable contract can distinguish safe migrations
from unsafe ones in real robot-learning stacks and produce a deployable
adapter **without changing the frozen policy weights**.

## Claim gates (ordered)

- [x] Real target-goal round trip on official robosuite OSC.
- [x] Public minimal upstream-compatible robomimic patch for issue #270.
- [ ] Within-one-scene, same-physics causal ablation of OSC controller
      `initial_joint` showing torque divergence and recovery.
- [ ] Physically matched full-state paired rollout, or explicit documented
      reason exact rollout is impossible under the tested controller/solver.
- [ ] Real robomimic HDF5 absolute->delta->absolute conversion and replay.
- [ ] Real ManiSkill #429 base-fail/fix-pass trajectory success study.
- [ ] At least one external upstream maintainer review or merge.
- [ ] Second independent reproduction by a non-author.

Do not label the work accepted by any top conference, endorsed by any
university, or L8/L9-achieved before evidence exists.

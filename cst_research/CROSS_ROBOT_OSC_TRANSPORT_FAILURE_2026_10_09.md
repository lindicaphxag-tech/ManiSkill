# Cross-robot OSC migration: retained negative results

First public exploratory run (intentionally **failed** strict numerical
assertions): https://github.com/lindicaphxag-tech/robomimic/actions/runs/37811000344

Source test code:
https://github.com/lindicaphxag-tech/robomimic/blob/validation/cst-ur5e-iiwa-osc-20261009/tests/test_cst_real_osc_multi_robot.py

The already validated Panda Lift/Stack scripts were deliberately extended to
two physically different robot models, **UR5e** and **IIWA**, both using real
robosuite 1.5.2 / MuJoCo 3.3.0 and 8-step `OSC_POSE`
delta -> absolute controller transformation. Per source/target pair the
MJCF and initial MuJoCo state were aligned, a source-defined bounded native
action sequence was reused, and the target nullspace posture and goal
reference were synchronized by the existing executable handshake.

**Goal:** falsify any overly broad belief that the narrow Panda OSC
state/action compiler guarantees cross-robot physical state equivalence.

## Observed errors in the FIRST CI (not tuned post hoc)

| Robot | action seed | max full scene qpos difference | max arm joint qpos difference | max goal matrix difference |
|---|---:|---:|---:|---:|
| UR5e | 42 | **1.039746e-3** | 7.069e-8 | 1.372e-8 |
| UR5e | 270 | 1.439e-8 | 4.573e-9 | 7.167e-9 |
| IIWA | 42 | 2.520e-4 | **2.520e-4** | **1.665e-4** |
| IIWA | 270 | 2.215e-4 | **2.215e-4** | **1.623e-4** |

Original frozen test acceptance limits, before observing values:
- goal matrix error < 1e-6;
- arm joint-state error < 2e-5;
- complete scene qpos difference < 2e-5.

**Three of four cross-robot cases fail the strict full-scene limit.**
Two IIWA cases also fail arm / goal limits. One UR5e case (seed 42)
has tiny arm and goal discrepancies but much larger **other full-scene
coordinates**. These have mixed units and must not be labeled a
single end-effector meter displacement.

The CI was *red* and remains part of the evidence. Do not relax
thresholds after measurement simply to report 4/4 successes.

## Mechanistic interpretation — hypotheses only

- UR5e seed 42: arm/goal match while the scene does not. A possible
  interpretation is divergence in contact or free-object motion, but
  the qpos index responsible is not yet isolated. That is a hypothesis,
  not an established finding.
- IIWA: non-negligible arm and controller-goal mismatch appears within
  eight physics steps. This could reflect kinematics/controller integration,
  unmodeled mutable controller state, precision, or source/target goal
  reference semantics. The initial same-MJCF handshake by itself did not
  provide a universal execution-equivalence certificate.

A separate diagnostic CI preserves **per-step qpos/arm/goal residuals**
and worst-coordinate indexes:
https://github.com/lindicaphxag-tech/robomimic/tree/validation/cst-ur5e-iiwa-diagnostics-20261009

## The scientific advance gate

A useful new compiler mechanism would distinguish:
1. **locally validated** action/goal memory transformations;
2. **runtime/integration uncertain** mappings that require a physical
   calibration or instrumented probe before execution;
3. **incompatible** mappings that are refused with observable witnesses.

Do not call an action chart transform or small controller-state handshake
alone a robot-wide formal bisimulation or safety certificate.
The corresponding Panda/PickCube frozen PPO evidence remains valid for its
own precisely documented scope; it is not automatically transferable to
new robots.

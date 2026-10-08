# Real Robosuite OSC Controller-State Handshake — Public Reproduction

## Problem

A controller migration can preserve the goal target while producing different
torque commands because MuJoCo state snapshots do not carry all
controller-owned memory (particularly the OSC nullspace posture target
`initial_joint`).

This case illustrates why a frozen-policy deployment adapter may need a
**controller-state mapping M** in addition to an action mapping T.

## Environment

- robosuite 1.5.2 / MuJoCo 3.3.0 / Panda + Lift / CPU;
- source: `OSC_POSE` with `input_type=delta`;
- target: `OSC_POSE` with `input_type=absolute`;
- fixed impedance, achieved-goal update;
- run: https://github.com/lindicaphxag-tech/robomimic/actions/runs/37705773529
- code: https://github.com/lindicaphxag-tech/robomimic/blob/validation/delta-actions-real-osc-20261008/tests/test_robosuite_paired_closed_loop.py

## Observations

### Goal vs physics equivalence

Actual controller goal generation was compared against the compiled inverse
action using real Panda/Lift simulation.

Independent 10-step goal test:
- maximum native action round-trip discrepancy: `1.568e-15`;
- maximum goal-position discrepancy: `0`;
- maximum goal orientation discrepancy: `1.053e-8` radians.

After transferring `initial_joint`, on a separate 8-step paired rollout:
- maximum controller goal discrepancy: `5.149e-9`;
- maximum **arm joint qpos** discrepancy: `1.520e-9` radians;
- maximum **full-scene qpos** discrepancy: `1.688e-3` (mixed physical units; includes free object).

The full scene is **not** certified equivalent. The object discrepancy may
stem from independently initialized scene/model/solver states and contacts;
it has not been causally isolated. The arm and object results must not be
conflated.

### Within-scene controller-memory intervention

Source and target receive the same copied MuJoCo state and semantically
equivalent OSC goals. The experiment changes only the target controller's
nullspace `initial_joint`.

- Introduced nonzero posture-reference mismatch:
  maximum source/target torque difference `1.575201` (torque units).
- Source posture-reference transferred to target:
  maximum difference `9.152501e-7` (torque units).
- Ratio: roughly `1.72e6`, but this is a single *deliberately injected*
  controller-state mismatch, not a measured task-performance improvement.

This demonstrates a **mechanistic counterexample** to the notion that
matching `goal_pos/goal_ori` alone guarantees low-level torque equivalence.

The experiment does NOT prove that all hidden controller states can be
transferred nor certify arbitrary closed-loop trajectories.

## Source-code mechanism

robosuite OSC `run_controller` includes a nullspace torque term:

```python
self.torques += nullspace_torques(
    self.mass_matrix, nullspace_matrix,
    self.initial_joint, self.joint_pos, self.joint_vel
)
```

The executable goal/action contract therefore requires more than the
exposed native action chart.

## Remaining scientific controls

1. Multiple state-only controlled interventions in the *same physical
   snapshot* (current validation run in progress).
2. Ensure two scenes use identical model parameters, solver state and
   contacts before interpreting free-object qpos differences.
3. Real robomimic HDF5 dataset conversion + replay success/error.
4. Independent controller family beyond Panda OSC.
5. External maintainer review/merge and third-party reproduction.

## External-recognition discipline

Robomimic upstream issue:
https://github.com/ARISE-Initiative/robomimic/issues/270

Upstream-ready feature PR branch:
https://github.com/lindicaphxag-tech/robomimic/tree/fix/add-delta-actions-converter-pr

The causal experiment is kept in a validation branch; it is **not** bloating
the small upstream patch. External maintained adoption remains **zero**.


## Multi-intervention reproducibility (32 controlled offsets)

Frozen-scene experiment run:
https://github.com/lindicaphxag-tech/robomimic/actions/runs/37706017196

The source physical state and source/target OSC goals were fixed. We
replaced the target `initial_joint` with 32 deterministically sampled
synthetic offsets (Gaussian standard deviation 0.03 rad per joint), then
computed the target low-level torque without stepping the simulator.

Absolute maximum source/target torque difference across each perturbation:
- n = 32
- p10 = `0.2739986`
- median = `0.7785467`
- p90 = `1.872390`
- exact transferred reference: `8.518459e-7`

The same workflow passed **3/3 tests**. Separate paired controller goals
still matched at `5.148609e-9`; arm-joint qpos matched within
`1.518279e-9` rad over 8 steps, while full-scene qpos mismatch
remained `1.221201e-4`. The latter is not treated as controller-migration
success/failure until simulation-model confounds are isolated by a
same-controller negative control.

These are **intervention sensitivity measurements**, not an estimated
policy success-rate delta, not a statistical confidence interval over
independent scenes, and not external adoption.


## Synthetic HDF5 integration + same-controller negative control

CI: https://github.com/lindicaphxag-tech/robomimic/actions/runs/37706383227

Full CPU suite: **5 passed in 25.32s** (fixed robosuite 1.5.2 /
MuJoCo 3.3.0).

A synthetic 8-step HDF5 episode was generated with the **real Panda OSC**
controller. The test then executed robomimic's actual
`RobomimicDeltaActionConverter.convert_demo` and
`convert_actions` implementations against real simulator snapshots.
Only the heavy initialization-time training/metadata modules were replaced by
narrow test doubles.

Result: `ROBOMIMIC_HDF5_REAL_OSC_PASS steps=8
native_error_max=1.639314e-15 saturation_count=0`.

This is an actual HDF5 parser + converter-method integration test, **not**
validation of the entire robomimic CLI, multiprocessing writer, external
public dataset, or learned policy success rate.

The negative control uses two **identical** delta-OSC controller types in
separate Panda/Lift simulator instances. It found:

- independently initialized `geom_size` difference `0.001805384`;
- maximum full-scene qpos difference `0.002626427`;
- maximum arm-joint qpos difference `9.537e-8`;
- maximum actuator control difference `1.458e-5`.

Thus full-scene differences between independent simulated environments
are **confounded by model geometry**. They cannot automatically be
attributed to a controller-interface migration.


## Identical-MJCF source-to-target CLOSED-LOOP migration

Canonical public run:
https://github.com/lindicaphxag-tech/robomimic/actions/runs/37706956215

**8/8 CPU simulation tests passed** (robosuite 1.5.2, MuJoCo 3.3.0).

Experimental controls:
- real Panda/Lift physics, source delta OSC and target absolute OSC;
- exactly the same MJCF XML reloaded in target;
- identical initial flattened physics state and copied warm-start state;
- target OSC nullspace posture `initial_joint` set to source;
- source policy-native OSC deltas analytically compiled to target absolute
  pose actions at every one of the 8 closed-loop steps.

Source-vs-target maximum error over these 8 steps:
- full-scene qpos: **1.836504e-7**;
- arm joint qpos: **1.836504e-7** radians;
- controller goals: **5.148608e-9**.

For comparison in the **same public workflow**, an identical delta-OSC
controller pair using the same MJCF/physics alignment had a full-scene
qpos error of **1.078719e-7**.

When the controller types differed AND the MJCF geometry was not aligned,
full-scene qpos mismatch was **7.228455e-4** despite arm joints being
near-equivalent. This is why model identity is part of the replay protocol.

Also in this run:
- 32 synthetic OSC controller-memory perturbations:
  p10 `0.3009982`, median `0.8095894`, p90 `1.912405`
  maximum torque error, while matched state error `8.929123e-7`.
- 8-step synthetic HDF5 dataset through actual robomimic `convert_demo`:
  native action max error `1.665335e-15`, zero saturation.

**Scientific claim boundary:** this is finite-horizon, single-scene,
CPU-simulated controller-interface migration for a prescribed sequence of
bounded OSC commands. It is NOT a trained frozen VLA policy result, proof of
general nonlinear-region bisimulation, or validated contact-rich task
success-rate parity. Full-state error close to same-controller numerical
baseline is strong empirical evidence, not a universal certificate.

The important mechanism combines an action-chart inversion with controller-
owned state mapping and exact physics-model replay. An action vector
conversion by itself does not establish these guarantees.

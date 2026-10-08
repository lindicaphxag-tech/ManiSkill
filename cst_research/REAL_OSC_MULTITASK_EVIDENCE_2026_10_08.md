# Real OSC controller migration on Lift and Stack: matched-model evaluation

**Canonical GitHub Actions run:**
https://github.com/lindicaphxag-tech/robomimic/actions/runs/37713698317

**Full code:**
https://github.com/lindicaphxag-tech/robomimic/blob/validation/delta-actions-real-osc-20261008/tests/test_cst_real_osc_multitask.py

## What changed from the initial single-task study

The same narrow executable compiler
(`cst_research/executable_osc_migration.py`) is now invoked on real Panda OSC
controller objects in **two different robosuite task environments: Lift and
Stack**. We are testing the same fixed-impedance `OSC_POSE` controller
family, NOT a new controller algorithm/family.

Six independent test instances pair task types with deterministic
**action-generation random seeds** (42, 270, 429). The task's randomized
environment model itself is not seeded by this test; source and target within
each pair are made identical by reloading the *same* MJCF XML and physical
state. Therefore treat the six results as 6 experimental executions, not
3 controlled environment-randomization seeds for either task.

Protocol for each pair:
1. Create source delta-OSC Panda and target absolute-OSC Panda.
2. Reset both; reload source's fully generated MJCF into target.
3. Copy flattened MuJoCo state and solver acceleration warm-start.
4. Refresh both controller reference frames and run the executable
   **state-posture handshake**, requiring an APPLIED result.
5. For eight successive *real physics steps*, sample a bounded native
   action from the frozen NumPy RNG action sequence. Decode to a physical
   OSC increment, compose with the source achieved pose, and pass the
   absolute goal into the target OSC controller.
6. Compare complete scene `qpos`, arm joint `qpos`, and target goal matrix
   at every step. No per-step physical state reset is permitted.
7. Assert maximum goal matrix difference < 1e-6 and arm and full-scene
   state differences < 2e-5.

## Results

Every one of the six new paired task/seed tests **passed**. The full
CI suite including earlier baseline/negative-control tests was
**15 passed in 56.95 seconds**.

| Task | Action seed | Max full-scene qpos difference | Max controller goal matrix difference |
|---|---:|---:|---:|
| Lift | 42 | 2.03023e-7 | 1.38560e-8 |
| Stack | 42 | 2.01951e-7 | 1.40304e-8 |
| Lift | 270 | 1.79496e-7 | 6.78874e-9 |
| Stack | 270 | 1.75507e-7 | 6.77973e-9 |
| Lift | 429 | 2.02071e-7 | 1.08569e-8 |
| Stack | 429 | 1.84899e-7 | 1.08703e-8 |

Across these six trials: maximum full-scene `qpos` discrepancy approximately
**2.03e-7**. All matching source/target joint `qpos` and OSC goal assertions
passed.

## Scientific claim limits

The action source is a **deterministic scripted action stream**, not a
trained frozen neural policy checkpoint. The model checker is deliberately
narrow (Panda + OSC_POSE, fixed impedance, achieved-pose state, reference
frame matched and common MJCF). This 8-step result is an empirical local
transport test; it is not a universal formal equivalence proof or real-robot
safety claim.

These tests support a specific, falsifiable *engineering mechanism*:
native-action transformations plus a controller-owned nullspace-state mapping
can preserve low-level execution across different action parameterizations,
when full simulator-model identity and the necessary state are enforced.

They do not prove that arbitrary hidden controller memory can be recovered
automatically from a black-box controller, nor any task-success probability
improvement or global bisimulation.

## Next discriminating experiments

- Replace scripted actions with a **real frozen trained policy** checkpoint;
  require same-policy (no retraining) paired task success measurements.
- Verify a second controller family or robot, with explicit incompatible
  configurations and checkable refusal witnesses.
- Run longer 50/100-step contact-rich rollouts and independently selected
  environment geometry and solver conditions; document divergence.
- Ask an independent practitioner to rerun from pinned source/dependencies.
- Obtain external maintainer feedback/adoption through separate minimal
  upstream PRs (#429 ManiSkill, #270 robomimic, #3312 LeRobot).

# CST live desired-OSC: closed-loop three-arm causal counterfactual

**Canonical public run (20 tests passed):**
https://github.com/lindicaphxag-tech/robomimic/actions/runs/37715504522

**Actual independent-execution code:**
https://github.com/lindicaphxag-tech/robomimic/blob/validation/delta-actions-real-osc-20261008/tests/test_cst_desired_physical_causal_ablation.py

## Scientific question

Does the `OSC_POSE` delta controller's **previous desired goal** contain
execution-relevant memory that cannot be replaced with its current achieved
pose when compiling equivalent absolute OSC targets?

## Experimental intervention

For each of three deterministic **action stream seeds** (42,270,429),
create three independent real Panda/Lift robosuite 1.5.2/MuJoCo 3.3.0
CPU simulated controllers:

1. **Source** — `OSC_POSE` `delta` with `goal_update_mode=desired`.
2. **Correct adapter** — `OSC_POSE` `absolute`, driven by next target
   compiled from the source's *live previous desired goal*.
3. **Naive achieved-only adapter** — same `OSC_POSE absolute` destination,
   but relative deltas are added to the naive target's current measured
   end-effector pose (no history transfer).

All three environments: exact same generated MJCF (including geometry),
copied flattened MuJoCo state and solver acceleration warm start; same
OSC gains, controller-owned nullspace posture reference, initial live desired
pose aligned to actual achieved world-frame pose; same deterministic
bounded 16-step source-native action sequence. Physics runs naturally
between steps; **no per-step simulator-state reset**.

This is an actual executed **counterfactual physical rollout**, not a
post-hoc static goal-vector comparison.

## Raw results (full-scene max |qpos_source - qpos_target|)

| Action RNG seed | Correct live-memory adapter | Naive achieved-only adapter |
|---|---:|---:|
| 42 | 4.605237e-7 | 0.550858 |
| 270 | 2.983248e-7 | 0.476500 |
| 429 | 2.360026e-7 | 1.023570 |

- Across three cases the correct adapter's maximal *goal position* error
  was **0.0** in the script output.
- Naive controller goal-position deviations ranged **0.0319–0.0415 m**.
- The entire relevant real-simulator suite reported **20 passed
  in 79.71 seconds**.
- Raw per-step trajectory deviations for both adaptations are printed
  in the CI log. The naive deviation accumulates over 16 steps.

## What this proves / does not prove

It gives evidence that *for the specific tested OSC update semantics*,
losing previous desired-target memory changes actual controller execution
even when source native action streams, controller gains, MJCF and physics
initialization are matched. Transferring executable goal memory plus action
conversion preserves this small-horizon trajectory to numerical error.

This **does not** establish a probability gain in *task success* and is
not a frozen learned policy evaluation, hardware deployment, cross-controller
family theorem, or guaranteed bisimulation. The full scene `qpos` includes
both joint and free-object coordinates (mixed physical units), so 0.55 is
not interpreted as a robot end-effector translation of 0.55 m.

Controller modes with variable impedance, interpolation, saturation or
unknown runtime target history must be refused unless separately verified.

## Novelty distinction

This work is narrower than generic action-adapter concepts. The
deployment-relevant contribution is **stateful executable transport** of
controller-owned `goal_pos/goal_ori` memory in addition to native action
coordinates, with refusal behavior when that memory is unavailable.
Claims of novelty must still be compared against prior controller
migration, stateful refinement and action-interface adaptation literature.

## Next scientific discriminator

Execute a **pretrained frozen task policy checkpoint** under the three
modes above and evaluate paired task success, with scene/initialization
seeds held out before interpreting a success-rate gain. This artifact
currently uses deterministic scripted native action streams.

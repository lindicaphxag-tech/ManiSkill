# Frozen PPO target-memory feasibility: prospective PickCube 32-seed pilot

**Canonical public run:**
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37746168558

**Pre-registered sample/rules before first measurement:**
[FROZEN_PPO_MEMORY_32SEED_PILOT_PRE_REG_2026_10_08.md](FROZEN_PPO_MEMORY_32SEED_PILOT_PRE_REG_2026_10_08.md)

**Implementation/checkpoint:** https://github.com/lindicaphxag-tech/ManiSkill/tree/validation/frozen-ppo-memory-32-holdout-20261008.
MIT pretrained PPO weights from `kattri15/actionshift-baselines/ppo/pick_cube_final_ckpt.pt`
at SHA256 `3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8`,
**frozen**, no policy retraining/fine-tuning.

## Actual unconditional results over preselected 20001–20032

| Manipulation | Success episodes | Meaning |
|---|---:|---|
| Source `pd_ee_delta_pose` | **31/32** | Original trained action contract |
| State-memory-aware exact translation + reject on infeasible actions | **5/32** | Strict contract: refuses commands outside native reachability |
| State-memory-aware bounded non-exact projection | **32/32** | Controller memory read, 7D policy-observation projection, actuation projected into native bounds |
| Raw action copied into target-memory controller | **3/32** | Known-incompatible action-interface shortcut |

- Strict exact mode **refused 27 episodes** when the next desired target
  required an action outside target bounds. This is honest safe nonexecution,
  not proof that the source task failed.
- Bounded projection executed **30 approximate action steps** across the
  32 episodes (seed **20016** required **four**, while 26 others required
  one each).
- Source PPO failed seed **20016**; projected target finished it in this
  *one* batch. Do not claim the projection universally improves on the
  source policy: the difference is one episode and no cross-run physics
  repeatability for these exact samples is proven.
- Paired projected-vs-raw-copy success: **29 projected-only, 0 raw-only**.
  Projected-vs-source: **1 projected-only, 0 source-only**.
  Projected-vs-strict: **27 projected-only, 0 strict-only**.
- Source initial policy observations matched the 42-D policy ABI.
  Destination exposed 49-D proprioception containing the controller
  target-pose memory; the evaluator explicitly checks this 7-D field and
  removes it **only from the PPO observation**. The execution compiler
  still reads and uses the live target pose each step.
- All raw episode outcomes and refusal amplitudes are in the linked
  CI logs and `frozen_ppo_target_memory.json` artifact.

## Interpretation

These results support an **implementation-level causal hypothesis**:
a previously trained *fixed* neural policy can be transported to a
stateful target-relative controller by **keeping controller-owned goal
memory distinct from policy observation**, and when the commanded
one-step target is not representable, bounded nonexact projection may
preserve useful task execution on this distribution.

The projection in this pilot is **simple box/rotation-ball clipping**,
not claimed as an original optimization algorithm, formal certificate
of safety, or universal exact equivalence. The strict mode targets a
different exactness contract; its 27 refusals are not a quantitative
task-success loss that can be directly interpreted as a task failure.
ActionShift and other works address generic frozen-policy action-space
adaptation, so novelty must be scoped to executable runtime controller
memory and jointly compatible observation/action contracts.

## Limits and next scientific gates

- One PushCube task? **No**. This report is only **PickCube-v1**.
  A *separate* PushCube-v1 different frozen PPO checkpoint and separate
  seeds 30001–30032 were prospectively preregistered and are being tested.
- Entire 32-seed pilot is a **single stochastic simulation batch**.
  Another PickCube delta→absolute study changed its seed10014 outcome
  between independent runs, despite same nominal task seed and apparently
  matching runtime package versions. Never imply global deterministic
  per-seed replay without full physical-state fingerprints and duplicate
  CI runs.
- No different robot, real hardware, independent maintainer reproduction
  or accepted flagship method upstream yet.
- Extend to PushCube and further different tasks, implement and test
  physical goal error witness and policy robustness under multiple
  stochastic executions per matched initial state, and request an
  external reproducer to audit all code/weights.

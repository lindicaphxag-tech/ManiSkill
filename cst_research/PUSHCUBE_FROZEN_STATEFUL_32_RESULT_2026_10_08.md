# PushCube-v1: second frozen policy, stateful target-memory controller transfer

**Public successful end-to-end CI:** https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37746854295

**Predeclared experiment plan:**
[PUSHCUBE_FROZEN_STATEFUL_32_PRE_REG_2026_10_08.md](PUSHCUBE_FROZEN_STATEFUL_32_PRE_REG_2026_10_08.md)

**Public exact code:**
https://github.com/lindicaphxag-tech/ManiSkill/tree/validation/frozen-ppo-pushcube-memory-32-20261008

## Model and experimental context

- Task: official ManiSkill PushCube-v1/Panda/PhysX CPU.
- **Different pretrained PPO policy** from the PickCube-v1 results,
  from ActionShift/Attri (MIT), file
  `ppo/push_cube_final_ckpt.pt` at SHA256
  `a4a02198b309e73cb877959079023d967d5f63ec78380de9703a10c9efafc0cf`.
  This project did not train or fine-tune it.
- 32 preregistered seeds **30001–30032**, fixed 50-step budget, all
  attempted and reported. Four separate actual simulator environments
  running the same frozen policy on their *own* observations per seed.
- Source PPO expects **35D** policy observation; target controller
  appends 7D previous-goal state to produce **42D**. The general
  ABI projection verifies the 7D memory at its actual offset and
  removes only that memory from policy inference input. The adapter
  still reads the controller-owned target memory during execution.
- Identical source/target projected initial observation at every seed
  (valid experiment; no per-seed invalid comparisons in logs).

## Results, unconditional

| Arm | Successes out of 32 |
|---|---:|
| Original PPO / achieved-relative delta controller | **29/32** |
| Runtime goal-memory exact compilation or boundedness refusal | **28/32** |
| Runtime goal-memory-aware bounded nonexact projection | **29/32** |
| Unconverted source-native action to target-relative controller | **23/32** |

- Strict exact mode found **one nonrepresentable instruction** and
  refused it (seed **30024**).
- Approximate mode intervened in **one step** on seed 30024;
  it completed that episode.
- The 3 source failures were seeds **30003, 30005 and 30010**.
  The bounded approximate arm failed the same three; do not claim
  robustness beyond the original policy on this sample.
- Other naive failures occurred in seeds
  30007,30010,30014,30015,30022,30024,30026,30030,30032.
  Raw direct-copy still succeeded 23/32: task demands and controller
  history effects differ from PickCube, so the apparent benefit is
  **strongly task dependent**.
- Do not score refused episodes as unexpected control execution:
  strict acceptance contract differs from bounded approximation.

## What this demonstrates and limits

This second-task result validates that the *software mechanism*
(controller memory extraction, policy-observation ABI adaptation,
native-action feasibility check, bounded target projection) runs
end-to-end for a **different task-specific trained frozen policy and
different observation width**, not merely a hard-coded 42D PickCube
special case.

It does not validate a different robot/controller implementation family.
A 29/32 result on 32 CPU episodes from one trial is not statistical
guarantee nor proof of L8/L9 originality. Projection itself is simple
action clipping, not an original optimizer. More tasks, robust physics
fingerprints, paired seeded repetitions and independent maintainer
replication must follow. Attribute pretrained weights and known
action adaptation prior work to ActionShift.

Additional third/fourth-task experiments were separately preregistered
before observing them at:
[PULL_STACK_FROZEN_STATEFUL_PILOTS_PRE_REG_2026_10_08.md](PULL_STACK_FROZEN_STATEFUL_PILOTS_PRE_REG_2026_10_08.md).

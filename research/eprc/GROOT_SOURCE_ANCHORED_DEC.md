# Source-anchored GR00T DEC assay

This assay anchors the Differential Execution Contract to the current GR00T N1.7
relative-action path rather than to a hand-invented API.

## Frozen source

- repository: `NVIDIA/Isaac-GR00T`
- commit: `51d4c89f72fda44cbf77285c6a8114b52676b8a1`
- files:
  - `gr00t/data/state_action/state_action_processor.py`
  - `gr00t/data/state_action/pose.py`
  - `gr00t/data/state_action/action_chunking.py`

## Source semantics

GR00T issue #490 asks why training can use relative actions while inference still
returns absolute joint positions. The source path confirms that this is intended:

1. `apply_action()` converts configured absolute actions to a representation
   relative to the last state timestep;
2. the model learns/produces actions in that processed representation;
3. `unapply_action()` denormalizes and converts relative actions back to absolute;
4. `JointPose._compute_relative` implements joint-relative semantics as subtraction;
5. `JointActionChunk.to_absolute_chunking` restores absolute positions by adding
   the frozen reference state.

For NON_EEF joints:

```text
a_rel = q_target - q_reference
q_target = q_reference + a_rel
```

Therefore different reference states can produce different action tensors for
the same target without changing the local physical execution contract.

## Cross-ecosystem importance

The ManiSkill source-anchored assay and the GR00T source-anchored assay use
different runtime stacks and different action-processing code, yet both expose
the same distinction:

> action coordinates are not the physical contract.

A useful DEC must survive the train/inference representation boundary and
compare behavior only after semantic lifting into a canonical physical space.

## What this still does not prove

This is source-anchored controller evidence, not policy evidence. The decisive
next experiment remains two frozen policy families under matched physical support
interventions, where DEC similarity must predict held-out runtime decision
agreement better than raw action Jacobians, support-set overlap, or static
metadata.

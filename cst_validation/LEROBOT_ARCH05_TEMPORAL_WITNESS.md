# LeRobot ARCH-05 temporal-anchor differential witness

Status: **pinned-upstream semantic witness, not maintainer validation**.

This check executes the real `to_relative_actions` / `to_absolute_actions`
function bodies from two external refs:

- LeRobot main: `8c920c4270460851cedd2737657584586d3dc66f`;
- open ARCH-05 PR #4779 head: `bcef363a3d5d2ce42a576766c449acfd073ddef2`.

It also executes the real PI0.5
`state_observation_delta_indices` property body.  With default memory
parameters it returns:

    [-150, -120, -90, -60, -30, 0]

so semantic delta 0 / current state is the final history slot.

The shared relative-action processor in both refs collapses a 3-D stacked state
with `state[:, 0]`.  The PI0.5 processor itself independently uses
`state[:, -1]` as the current proprioceptive state when preparing a prompt.

The regression makes all six history slots distinct and demonstrates:

1. real upstream relative conversion equals subtraction from the oldest slot;
2. it differs from subtraction from semantic delta 0;
3. relative -> absolute round-trip still reconstructs the original action
   exactly, so ordinary round-trip tests cannot detect the semantic error.

This is a narrow correctness witness for the combination
`use_proprioceptive_memory=True` and `use_relative_actions=True`.  It does
not claim that all LeRobot temporal policies are affected: future-window
policies can legitimately place delta 0 at slot 0, and Flux3 history mode uses
a separate history normalizer.

The upstream-shaped fix should bind relative-action anchoring to semantic
temporal metadata (the unique slot whose delta index is 0) or an explicitly
resolved anchor index.  A hard-coded "first" or "last" slot merely moves the
bug between policy families.

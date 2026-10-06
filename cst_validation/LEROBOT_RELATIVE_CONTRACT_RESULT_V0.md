# CST × LeRobot relative-action contract witness v0

Status: **pinned-source compatibility evidence; not external adoption**.

Workflow run: `37394287171`  
CST validation commit: `9cb3af02ebf47f97071fa8105a1c547f63cdda2d`  
LeRobot source commit: `8c920c4270460851cedd2737657584586d3dc66f`  
LeRobot `relative_action_processor.py` git blob: `3405402904cf15ca18227b3a3fe006d7936f9d53`.

## What was frozen

The audit first downloads the exact LeRobot source and verifies the git-blob
identity before evaluating the semantic mirror. The pinned implementation:

- computes relative action as `action - state` on masked dimensions;
- broadcasts one state across the action horizon;
- collapses temporal observation state to its current frame;
- caches the state anchor;
- does not refresh that anchor while an action chunk remains in flight.

CST models this as `relative_latched`: every action position in one chunk is
decoded against one fixed `q_latched`.

## Differential result

Across 480 randomized cases spanning horizons 1, 2, 8, and 50 and action
dimensions 3, 7, and 8:

- LeRobot relative→absolute round-trip max residual:
  **4.440892098500626e-16**;
- CST `relative_latched` vs the pinned LeRobot contract max residual:
  **4.440892098500626e-16**;
- constructed witnesses separating the same chunk from per-step
  `delta_current` semantics: **480 / 480**.

The result establishes compatibility with this pinned source contract. It does
not mean LeRobot has adopted CST.

## Why this matters

The same informal word "relative" or "delta" can refer to different reference
machines:

- current-relative: reference is measured state at each step;
- target-relative: reference is the controller's accumulated target;
- latched-relative: the whole predicted chunk shares one cached state.

A converter that ignores the reference machine can preserve tensor shape while
changing the physical goal sequence.

# Second Stack: robomimic / robosuite Absolute → Delta Action Compiler

External anchor: robomimic issue #270 requests the inverse of the existing
delta→absolute dataset converter.  A maintainer explicitly replied that they
are happy to accept a PR.

## Why simple differencing is wrong

robosuite OSC first clips and rescales the policy-native action from
[input_min, input_max] into a physical delta range [output_min, output_max].
For orientation, the controller composes

    R_goal = R_delta @ R_baseline

so the inverse is

    R_delta = R_goal @ R_baseline.T.

For robosuite >=1.5 the absolute goal may live in the controller input
reference frame (base or world), while <=1.4.1 absolute OSC goals are in the
world frame.  The converter therefore has to extract the correct achieved pose
in the same chart as the dataset absolute action.

## Current prototype

The public CST branch now contains a version-independent semantic core that:

- inverses robosuite action scaling instead of applying np.diff;
- recovers orientation deltas using the controller's left-composition rule;
- supports achieved-goal and desired-goal update semantics;
- extracts current >=1.5 base/world reference-frame poses;
- extracts legacy <=1.4.1 world-frame poses;
- preserves gripper / action remainder;
- returns explicit SATURATED evidence when an absolute goal is outside the
  delta controller's representable range.

## Intended upstream integration

Mirror the existing RobomimicAbsoluteActionConverter:

1. Read dataset env metadata.
2. Construct a delta-controller environment from an absolute-controller dataset.
3. For each episode step, reset the delta environment to the recorded MuJoCo state.
4. For each robot arm, extract its OSC controller baseline pose and action scaling contract.
5. Convert the absolute pose action to the policy-native delta action.
6. Preserve gripper/remainder values.
7. Write a new actions_delta dataset and report saturation counts.
8. Add --add_delta_actions to convert_robosuite.py.

The PR should remain scoped to fixed-impedance OSC pose actions, matching the
capabilities of the existing absolute-action converter.  Variable-impedance
actions should be rejected rather than guessed.

## Evidence target before upstream PR

- pure semantic round-trip tests;
- 1.4.1 and >=1.5 runtime-contract unit tests;
- one real robomimic demonstration with
  delta → absolute → recovered-delta comparison;
- replay success / trajectory deviation report;
- no silent saturation.

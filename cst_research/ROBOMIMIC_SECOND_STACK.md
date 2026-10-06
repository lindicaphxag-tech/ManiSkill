# Robomimic / Robosuite OSC Inverse Bridge

This is the second-stack CST bridge motivated by robomimic issue #270
("Conversion from absolute actions to delta actions").

## Why simple subtraction is insufficient

Current robosuite OSC delta semantics include:

1. clipping and affine input->output scaling;
2. position updates against either the achieved pose or previous desired goal;
3. orientation updates on SO(3), with
   `R_goal = R_delta @ R_base`;
4. optional statefulness through desired-goal memory;
5. action remainders such as gripper commands.

Therefore a correct inverse must compute

```
delta_p = p_goal - p_base
R_delta = R_goal @ R_base.T
delta_R = Log(R_delta)
native_delta = inverse_scale([delta_p, delta_R])
```

and explicitly report when the requested physical delta is outside the
controller output range.

## Current evidence

The bridge includes:

- exact inverse affine action chart;
- SO(3) exponential/logarithm round trip;
- achieved-goal and desired-goal modes;
- explicit previous-desired-goal state dependency;
- saturation/refusal evidence;
- preservation of gripper/other action remainder;
- 2000 randomized executable-goal round trips across achieved/desired modes.

This is a research-side prototype shaped to match the existing robomimic
delta->absolute converter.  It is not yet an upstream robomimic PR because the
current GitHub connector cannot create a fork of that repository.

## Upstream integration target

The minimal upstream implementation should extend
`robosuite_add_absolute_actions.py` with an inverse converter that derives
delta actions from controller semantics, not raw consecutive action
subtraction, and should write to a new non-destructive dataset key.

The strongest validation is a controller-level round trip:
`delta -> current absolute converter -> inverse converter -> controller goal`.

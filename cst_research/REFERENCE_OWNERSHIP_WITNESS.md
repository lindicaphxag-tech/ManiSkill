# Reference Ownership: a Controller-State Impossibility Witness

ManiSkill's current `PDJointPosController.set_action` contains two delta
semantics with the same action dimensionality and potentially the same
normalization / physical delta range:

```
use_delta=True, use_target=False:
    target_qpos = current_qpos + action

use_delta=True, use_target=True:
    target_qpos = previous_target_qpos + action
```

The second controller owns hidden dynamic state (`previous_target_qpos`), and
ManiSkill explicitly serializes that state through `get_state/set_state`.

For a current-relative source command with desired goal

```
g = q + d,
```

transport into a target-relative controller requires

```
v = g - r,
```

where `r` is the target controller's previous target state.

Consider two executions with the same policy-visible `(q,d)` but different
controller histories `r_a != r_b`.  Any memoryless adapter must emit the same
`v` in both executions.  Their target goals are then separated by

```
(r_a + v) - (r_b + v) = r_a - r_b.
```

Therefore they cannot both equal the same desired goal.  By the triangle
inequality, at least one execution incurs residual

```
>= ||r_a - r_b|| / 2.
```

This gives a constructive lower bound, not just an empirical failure.

A stateful adapter removes the obstruction exactly by emitting

```
v_a = g - r_a
v_b = g - r_b.
```

## Why this matters for CST positioning

A static hidden-action ABI grammar can describe that an action is "delta", but
that label alone does not specify **who owns the reference state** or its
lifetime.  Controller migration therefore requires dynamic state semantics, not
only action-vector semantics.

This is a narrow mechanistic distinction from hidden-contract identification
benchmarks: CST assumes concrete controller implementations are available and
asks whether one closed-loop executable contract can be compiled into another.

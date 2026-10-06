# ManiSkill Joint-Position Controller Contract Bridge

This module is the first bridge from the general CST theory back to the real
controller semantics implicated by ManiSkill issue #429.

It models three executable joint-position contracts:

- absolute target;
- delta from current qpos;
- delta from previous target qpos.

For each contract it also models normalization and physical action bounds.

The compiler first evaluates the source controller goal, then solves the target
controller's inverse action chart for the same goal.  It never treats physical
qpos as a normalized action.  If the target command lies outside its physical
range, the result is SATURATED and the goal residual is retained as evidence
instead of being silently erased by clipping.

This gives a practical distinction:

- representation-equivalent and in-range -> EXACT;
- semantically representable but requiring source/target memory -> EXACT with
  explicit state dependency;
- outside target action range -> SATURATED / refuse exactness.

The randomized matrix test covers 3 source modes x 3 target modes x 2 source
normalization choices x 2 target normalization choices x 100 states/actions =
3600 controller migrations.

The upstream #429 patch remains separate and minimal.  This research bridge is
evidence for the generalization, not part of the proposed upstream diff.

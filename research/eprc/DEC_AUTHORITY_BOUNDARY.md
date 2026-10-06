# DEC authority boundary: saturation as a physical contract phase change

A representation-invariance claim must stop at the controller's physical authority boundary.

For an invertible local action reparameterization, semantic lifting cancels the coordinate change and preserves the Differential Execution Contract (DEC).

A saturating controller is different. If `physical_command = clip(scale * action, lower, upper)`, the local action-to-physical Jacobian loses rank whenever a coordinate is saturated. The target controller then loses local authority in that physical direction.

## Runtime implication

EPRC must not say that two stacks have the same DEC merely because action tensors or support sets look the same. It first checks controller authority.

- full authority + matching lifted DEC -> candidate exact equivalence
- authority loss -> reject exact transport

This is the representability bridge between CST/CSIR and DEC.

## Falsifiable prediction

If the target controller saturates a direction needed by a held-out support perturbation, the lifted DEC should lose rank before task-level failure is necessarily visible. That rank loss should predict when exact transport ceases to be valid.

The next robot-policy experiment should test whether this certificate predicts held-out transport/repair failure better than action-norm clipping flags alone.
# Effect-space DEC: bounded cross-embodiment extension

## Motivation

Physical-command DEC is only directly comparable when two stacks share a common canonical physical-command space. Different robot embodiments often do not: joint counts, controller dimensions, and internal command coordinates can all differ.

The narrow extension is to compare them only after mapping each embodiment into a shared, measurable task-effect tangent space.

Let:

- J_phys,i = local physical support-response Jacobian for embodiment i;
- E_i = local physical-command -> task-effect Jacobian;
- J_eff,i = E_i J_phys,i.

Two embodiments are locally equivalent for the current disturbance only if their task-effect DEC agrees in this common space.

## Cross-embodiment transport

For target action-to-physical Jacobian L_t, the effective target authority is:

  A_t = E_t L_t.

An exact local cross-embodiment transport exists on the identified support response iff:

  Im(J_eff,source) subseteq Im(A_t).

The minimum-norm target action response is:

  J_action,target = A_t^+ J_eff,source.

This is the same support-restricted authority criterion, but applied in shared task-effect space rather than requiring equal physical command dimensions.

## Claim boundary

This file does NOT establish cross-embodiment policy evidence. The linear algebra is standard and not claimed as new.

The research value would come only if E_i can be obtained from deployment-observable execution probes and if effect-space DEC predicts held-out cross-robot transport/repair outcomes better than static embodiment metadata or end-effector-controller labels.

Until that experiment exists, effect-space DEC is a constrained extension and must not be promoted to the paper's primary claim.

## Kill criteria

Remove this extension if:

- E_i requires privileged simulator state unavailable at deployment;
- cross-embodiment effect-space similarity does not predict held-out behavior;
- a simpler shared end-effector descriptor performs equally well;
- the task-effect map is too unstable over the operating region.
# Black-box task-effect identification

Effect-space DEC is only deployment-relevant if the embodiment-specific physical-to-effect map can be obtained without privileged simulator Jacobians.

This capsule therefore treats the local task-effect map as another measurable runtime object.

For action probe directions z_m around action a0, observe task effects e(a0 +/- eps z_m) and form:

  y_m = [e(a0 + eps z_m) - e(a0 - eps z_m)] / (2 eps).

Stacking rows gives:

  Y ~= Z J_effect^T.

The local effect Jacobian is estimated by least squares:

  J_effect^T = Z^+ Y.

## Certificate

An identified map is accepted only when:

- the probe design is numerically well-conditioned;
- an independent held-out set of action directions is predicted with low residual.

This is deliberately parallel to CASJ's held-out intervention gate. A low training residual alone is not enough.

## Deployment interpretation

The effect vector must be measurable from deployment telemetry or perception, for example:

- end-effector displacement/twist;
- object pose displacement;
- contact wrench or force proxy;
- task-relevant relative geometry.

No claim is made that every task has a stable low-dimensional effect representation.

## Kill criterion

If effect maps require privileged simulator state, fail held-out locality, or add no predictive value over a simpler shared descriptor, the cross-embodiment extension is removed from the main method.
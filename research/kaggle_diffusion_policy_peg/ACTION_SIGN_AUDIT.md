# Action-sign compatibility audit

This note is a static derivation from the current PR heads, not an empirical
robot rollout.

The trajectory converter receives the inverse relative quaternion
`q_data = q_current * inverse(q_target)`, inverts it to recover the desired
relative rotation, converts that rotation to XYZ Euler `e`, and the current
#1495 head returns `-e`. With symmetric physical action bounds `[-s, +s]`,
`inv_scale_action(-e, [-s, +s])` produces normalized action `u = -e/s`.

- On current ManiSkill main, `PDEEPoseController._clip_and_scale_action`
  multiplies by `rot_lower = -s`; the realized Euler increment is
  `u * rot_lower = (+e)`. The #1495 negative sign is compensating for this
  legacy controller mapping.
- On the proposed #1472 head, rotation is multiplied by `rot_upper = +s`; the
  same action realizes `u * rot_upper = (-e)`. Thus the current #1495 head and
  #1472 head are sign-incompatible when stacked, for unsaturated actions.

The existing #1495 regression test explicitly models the legacy negative
scaling. Before #1495 can safely follow #1472, its conversion and regression
must be updated for the positive scale, or the controller API must expose a
stable action-scale contract that the converter can query. The corrected
Diffusion Policy assay therefore compares #1495 against current main only; it
does not silently combine these two heads.

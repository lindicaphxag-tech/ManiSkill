# Upstream #1495 interaction handoff

GitHub integration write to `mani-skill/ManiSkill#1495` is currently blocked
with `403 Resource not accessible by integration`. The following is the exact
maintainer-facing update to post from the contributor account after reviewing
the public matrix result.

## End-to-end interaction finding

A public replay assay found that this converter-only change is **not
independently safe on current main**.

Using the same first 10 official `PegInsertionSide-v1` motion-planning
demonstrations under `pd_ee_delta_pose + physx_cpu`:

- current-main conversion saved about **9/10** replayed trajectories;
- converter-only #1495 saved **1/10**.

The assay asserts the exact source checkout before replay, so the baseline does
not import the fix branch accidentally.

The result is consistent with the independent controller sign bug in
#1469/#1472: current `PDEEPoseController` multiplies normalized rotation by
negative `rot_lower`. The old converter's inverse-rotation sign and that
controller inversion partially compensate. Correcting only the converter
removes the accidental cancellation.

I am therefore treating this PR as **blocked on the converter/controller
interaction**, not as ready to merge independently. A four-way public replay
matrix uses the same demonstrations:

1. current main;
2. converter-only #1495;
3. controller-only #1472;
4. composed #1472 + #1495.

I will follow that result even if it means revising or closing this patch.

This replay result is not a Diffusion Policy training-success claim.

## AI disclosure

Per ManiSkill/LeRobot-style transparency practice if relevant to the host
project: substantial AI assistance was used to audit the interaction and build
the validation harness; the contributor is responsible for reviewing the code,
the exact source identities, and the reported evidence.

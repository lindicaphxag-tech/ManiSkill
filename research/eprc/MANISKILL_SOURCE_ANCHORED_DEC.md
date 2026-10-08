# Source-anchored ManiSkill DEC assay

This assay removes a specific confound before expensive policy experiments:

> Does DEC merely rediscover the action tensor chart, or does semantic lifting recover the same local physical command map across real controller representations?

## Frozen source

- repository: `mani-skill/ManiSkill`
- commit: `62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3`
- file: `mani_skill/trajectory/utils/actions/conversion.py`

The production conversion functions distinguish absolute joint-position targets, current-state-relative joint deltas, and previous-target-relative joint deltas.

For a normalized delta controller with physical scale matrix D:

  a_delta = D^{-1}(q* - q_anchor)

while the physical target recovered by the controller is:

  q* = q_anchor + D a_delta.

Therefore a support perturbation gives raw action Jacobian J_action^delta = D^{-1} J_phys even though semantic lifting recovers the same J_phys.

## What the regression proves

1. raw action-space contract signatures differ across the source-frozen charts;
2. current-delta and target-delta can emit different action values because their anchors differ;
3. after semantic lifting, all charts recover the same differential physical contract.

This is a necessary condition for the broader EPRC claim, not sufficient robot-policy evidence.

## Next gate

Replace the hand-defined support-to-target matrix with intervention-estimated CASJ from at least two frozen policy families on the same ManiSkill task. Compare raw action-Jacobian distance, static metadata/controller-mode match, support-set overlap, and lifted DEC distance against held-out PASS / TRANSPORT / REPAIR / REJECT decision agreement.
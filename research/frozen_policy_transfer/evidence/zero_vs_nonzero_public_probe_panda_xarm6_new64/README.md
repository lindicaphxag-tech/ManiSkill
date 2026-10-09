# Original first-pass ZERO versus NONZERO physically executed probe on Panda/xArm6
Frozen design commit 84c0968d26d939c6b758e3cc769613afc9d3e92f; original protocol blob c03e7c6d2343ec6fcfe1824d4f4b76f5df00b755.
First completely successful native PhysX run 37910081496, original source commit 82599f25b0ee34f9a1ca787916b5a58486da8ce9; 8/8 CI jobs succeeded.
Six original unchanged source JSONs + one original first-run aggregate JSON all match EXACT before-archival SHA256SUMS. Six first-run native stdout logs are retained. FULL_ARCHIVE_SHA256SUMS covers all preserved files and posthoc gap analysis.
Native physical calibration: two robot morphologies x 8 historical reset states x two actual ACK truths x two probes = 64 controller worlds.
NEW blind native original: two real robot morphologies x 8 heldout seeds x two physical truths x two probes = 64 different PhysX controller worlds, 16 distinct reset states.
ZERO: 32/32 correct confidently labelled actual ACK and commanded target XYZ restored after native correction, 0 wrong, 0 abstain, 0 private target reads BEFORE decision.
FIXED NONZERO +0.15 normalized native X: identical 32/32, 0 wrong, 0 abstain, 0 private predecision read. There is NO demonstrated task-level improvement from the extra probe command.
Genuine physical achieved-XYZ two-truth separation: Panda zero 37.842488mm, nonzero 38.257733mm; xArm6 zero 41.623059mm, nonzero 42.067339mm. Although all 16 paired state gaps increased slightly (~0.4mm), this did not improve already perfect identification in THIS finite high-SNR test.
This is a negative marginal probing-value experiment, NOT a pretrained PPO transfer experiment, optimized probing, certified dynamics, equal-energy comparison, real ROS ACK loss, safe grasp/collision/force control, or independent third-party reproduction.
Final full original-source audit:
python -m research.audit_zero_nonzero_probe_two_robots --input-dir research/frozen_policy_transfer/evidence/zero_vs_nonzero_public_probe_panda_xarm6_new64 --output /tmp/verified.json
For original SHA-256: (cd research/frozen_policy_transfer/evidence/zero_vs_nonzero_public_probe_panda_xarm6_new64 && sha256sum -c ORIGINAL_SHA256SUMS)

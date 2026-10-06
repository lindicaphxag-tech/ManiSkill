# Frozen VQ-BeT PushT public-policy smoke

This is the first policy-level EPRC/DEC evidence gate.

Frozen objects:
- policy: `lerobot/vqbet_pusht`
- LeRobot: `8c920c4270460851cedd2737657584586d3dc66f`
- environment: `gym_pusht/PushT-v0`
- support: physical T-block pose `(x, y, yaw)`
- agent state: fixed during counterfactual queries
- device: CPU

Required pass conditions:
1. checkpoint loads through the pinned LeRobot API;
2. preprocessing is deterministic;
3. same-seed VQ-BeT queries are repeatable enough for paired finite differences;
4. central action-support derivatives are finite;
5. symmetry and scale-curvature diagnostics are retained even when unfavorable.

There is deliberately no threshold requiring a large or attractive derivative.

Negative outcomes narrow the claim. This smoke does not establish runtime repair, cross-policy DEC, superiority, third-party replication, L8, or L9. The next gate is the pre-registered two-policy held-out DEC discrimination protocol.

# Two-robot native PhysX: a fixed nonzero common probe does NOT improve already separable hidden ACK decisions

**9 October 2026 · pre-outcome frozen dual-truth study · genuine author-operated CPU PhysX, not third-party reproduced, not a full policy/grasp task-success evaluation.**

## Mechanism, controls and original-source guarantees

When a target-accumulating controller can be in either commanded-memory history `M_applied` or `M_held` after an unacknowledged t2 command, it may be tempting to send a larger known-delivered probe at t3 to disambiguate. In an ideal shared-gain response model `y_h = x + alpha(M_h+u-x)+e_h`, with the same fixed `alpha` and probe-independent bounded residuals, center displacement cancels common input: `y_applied-y_held=alpha(M_applied-M_held)+(e_applied-e_held)`. Under identical noise envelopes, a common nonzero `u` cannot improve worst-case observation-ball separability. This algebra is **elementary, not a newly discovered theorem**; realistic dynamics could be nonlinear or contact-dependent.

Before writing the new runner or seeing any new seed outcome, the physical probes, both robot bodies, two fault truths, old calibration seeds, fresh heldout seeds and full denominator were frozen at [original protocol commit 84c0968d26d939c6b758e3cc769613afc9d3e92f](https://github.com/lindicaphxag-tech/ManiSkill/commit/84c0968d26d939c6b758e3cc769613afc9d3e92f), Git protocol blob `c03e7c6d2343ec6fcfe1824d4f4b76f5df00b755`.

- Real native robots: Panda and xArm6 Robotiq with their different actual gripper composite action charts. ManiSkill `PickCube-v1` scripted controller commands, **not** frozen PPO task transfer.
- At t2: both **actually applied** and **actually held/zero arm action** physical truths, the ACK flag hidden from the classifier. At t3: known-delivered **zero** `[0,0,0,0,0,0]` or fixed **nonzero** `[0.15,0,0,0,0,0]` native arm probe. Gripper controls remain zero. Both arms have identical step counts, **NOT** identical actuation magnitude, work, energy or contact risk.
- Old truth-labelled calibration uses Panda 420001–420008, xArm6 430001–430008; for each robot/truth/probe a separate physical world is run and one empirical label response envelope is computed, with the prespecified `+0.002m` radius margin. **These finite-data envelopes are NOT trusted deterministic physics error bounds.**
- New blind test uses Panda 660001–660008 and xArm6 670001–670008. Sixteen unique reset states × two physical truth branches × two physically executed probes = **64 new genuinely stepped PhysX worlds**. The new tests are not used to adjust probe amplitude, class calibration, fault step or model.
- After a unique public achieved-XYZ motion label, the adapter actually sends a native t4 correction to the desired held commanded-target position, accounting for t3's different common probe; the true private target getter is used only **AFTER** that correction for audit. No privileged state is read for decisions.

## Complete original results (32 worlds per probe; 64 test worlds total)

| Original real native Physical PhysX measurement | Zero arm probe | Nonzero +0.15 X probe |
|---|---:|---:|
| Panda correct actual ACK history | 16/16 | 16/16 |
| xArm6 Robotiq correct actual ACK history | 16/16 | 16/16 |
| **Pooled correctly classified** | **32/32** | **32/32** |
| Confident but wrong decisions | 0/32 | 0/32 |
| Abstentions / refused corrections | 0/32 | 0/32 |
| Actually executed t4 commanded-target XYZ correction within `1e-4m` | 32/32 | 32/32 |
| Decision-time privileged controller-target reads | 0 | 0 |

**A real physical response difference, but no observed decision benefit.** Independently recomputing the original 64 actual world rows, the public achieved XYZ distance between physically applied versus held histories at the *same* seed/probe has:

| Physical robot | Mean response separation, zero probe | Mean response separation, nonzero probe | Nonzero minus zero |
|---|---:|---:|---:|
| Panda | 37.842488 mm | 38.257733 mm | +0.415245 mm |
| xArm6 Robotiq | 41.623059 mm | 42.067339 mm | +0.444280 mm |

The nonzero probe increased the measured response gap on **all eight new reset states of each robot**, with average gain around 0.4mm, which is a departure from the ideal shared-gain common-input invariant for this exact physical response. But **both probes already identify all accepted labels and restore the native commanded target on all original test cases**; the nonzero method does not improve success count or coverage here. The largest original postcorrection commanded-target XYZ error was `1.90735e-8 m`. These minuscule simulation controller setpoint residuals do NOT measure achieved end-effector tracking, contact, collision, applied force, or hardware risk.

## Source, statistical discipline and permission to falsify

- [First fully completed 64-new-world genuine PhysX CI with both independent calibration jobs and final source audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37910081496): **all 8 pipeline jobs succeeded**. Original executed source HEAD `82599f25b0ee34f9a1ca787916b5a58486da8ce9`.
- [Full-denominator auditor](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/dualrobot-nonzero-probe-identifiability-20261009/research/audit_zero_nonzero_probe_two_robots.py) independently recomputes all old calibration models and every blind label, refuse decision, native t4 controller target error, source probe identities and privacy budget. [Python 3.11/3.13 adversarial source-data tests, both green](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37909989173).
- [Original first-run 7 JSON dataset ZIP artifact](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37910081496): SHA-256 `4c0f64b2fba0c85a2d273cc4285427b5531fc708090beb21d30830abc7a5a1ff`. Includes **two historical calibration source JSONs**, four heldout physical source JSONs and one original recomputed aggregate. All files are retained unchanged.
- [Precommitted null model implementation](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/dualrobot-nonzero-probe-identifiability-20261009/research/common_probe_information_null.py) and [paired original physical response-gap auditor](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/dualrobot-nonzero-probe-identifiability-20261009/research/frozen_policy_transfer/review/physical_probe_informativeness.py) supplement the observed label counts without inventing another experiment.

### Claim boundaries

This is a precise negative **marginal information-value** result in a finite high-SNR scripted native control task, not a proof that zero probing is always best. All 64 test-world outcomes share only **16 distinct source reset seeds** across two robot bodies. The empirical fit uses old labelled cases; the test includes one fixed command amplitude, one fault step and one observation horizon. We do NOT optimize nonzero probe actions, compare equal probe energy, run pretrained Panda PPO on xArm6, measure manipulation-task completion, model contact/force safety or simulate real missing ROS/TCP acknowledgments. The work was run by this repository's owner, without any independent third-party PhysX execution or official ManiSkill upstream integration.

**Decisive next study:** freeze an intentionally lower-SNR regime (smaller fault amplitude, sensor noise, partial contact load, or significant actuator lag) where baseline zero action has measurable uncertainty; compare a physically optimized probe with an energy-matched fixed nonzero probe, zero probe, readback, and ActionShift's task-regret probe while preserving actual privileged reads and robot actuation work. Unless the optimized probe beats the strong zero baseline on genuinely fresh seeds, a sophistication claim would be misleading.

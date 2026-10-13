# Real PhysX two-ACK recovery-loss matrix and optimistic signal capacity

**First-outcome experimental report, 2026-10-13.** Source-only author-operated ManiSkill native CPU PhysX, not an externally replicated VLA policy. The historical 48-world zero/X/Y probe pilot remains an explicitly NEGATIVE fixed-probe separation result; these two studies have different preregistered reset seeds and must not be pooled as independent subjects.

## Prospective protocol and immutable run

- [Frozen original protocol](../TWO_ACK_REAL_RECOVERY_MATRIX_PREREG_20261013.json), Git blob `6789866ddfdc48350a56be6b50da66fd07014457`.
- [Real simulator source](../two_ack_real_recovery_physx.py) reproduces the documented native `pd_ee_target_delta_pose` contract.
- [Original completed GitHub Actions](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38331837905), both Panda and xArm6 jobs **SUCCESS**. The two unmodified run artifacts contain each robot's **80 original world rows** and native console logs. Total: **160 physically simulated conditions, 8 independent reset clusters** (four per morphology), *not* 160 independent episodes.
- Frozen four hidden execution histories: 00, 01, 10, 11 for two source-valid target-relative commands; frozen five decision outputs: four history-conditioned inverse-translation corrections and native zero-action. Every hidden truth, candidate action, robot and seed combination was executed; no success-based exclusions.
- Identical recovery action was constructed from each guessed history's source-replayed target; **the actual hidden ACK truth was not used to choose the candidate action**. Native private target reads occur only after all action choices and physics steps for integrity auditing.
- Primary loss: distance from achieved EE XYZ to the **source-constructed common all-applied controller target** after one correction followed by eight native zero-hold controller steps. This is not PickCube task success, collision-free safety, direct motor energy, robot autonomy, or a learned-policy score.

## Physical task-space cost matrices (mean across four reset seeds; millimeters)

### Panda

| Actual two ACKs / fixed guess | 00 | 01 | 10 | 11 | NO_ACTION |
|---|---:|---:|---:|---:|---:|
| 00 | 0.083 | 23.908 | 34.169 | 30.991 | 30.991 |
| 01 | 23.883 | 0.113 | 50.188 | 34.179 | 34.179 |
| 10 | 34.270 | 50.191 | 0.297 | 23.829 | 23.829 |
| 11 | 31.145 | 34.248 | 23.988 | 0.135 | 0.135 |

### xArm6

| Actual two ACKs / fixed guess | 00 | 01 | 10 | 11 | NO_ACTION |
|---|---:|---:|---:|---:|---:|
| 00 | 0.420 | 23.644 | 34.084 | 31.094 | 31.094 |
| 01 | 23.504 | 0.404 | 49.783 | 34.140 | 34.140 |
| 10 | 33.856 | 49.720 | 0.341 | 23.772 | 23.772 |
| 11 | 30.487 | 33.793 | 23.365 | 0.262 | 0.262 |

Under a hypothetical **perfect history-aware oracle** choosing each row's matching correction, mean achieved XYZ errors were **0.157 mm (Panda)** and **0.356 mm (xArm6)**, compared with **22.284 mm** and **22.317 mm** for a fixed no-action baseline averaged uniformly over the four true histories. This is a counterfactual *upper benchmark* on how useful true ACK knowledge could be, NOT an achieved automatic history-detection policy or a claim of improving PickCube completion rate.

Every mismatched history action in these matrices exceeds **23 mm** on average, so for a strict 5-mm task-space error threshold these four nominally different histories did not collapse into an equivalent two-recovery-action class under the frozen controller/policy set. This is specific to the task-space loss, symmetric goal, simulated robot states and four fixed actions; no general robotics safety theorem follows.

## Task-loss signal-capacity floor (idealized, not observed sensing performance)

Let a decoder observe at most M distinct frozen signal outcomes, and select one fixed candidate recovery action per output, with all four true histories treated as **equally likely**. Even an impossible perfect observation encoder cannot beat

`min_{S subset of four corrections, |S|<=M} (1/4) sum_true min_{d in S} observed_real_physx_error(true,d)`.

Enumerating every finite recovery-action subset against the **actual 4×4 physical cost matrix** gives:

| Distinct signal outputs available | Panda lower bound (mm) | xArm6 lower bound (mm) |
|---:|---:|---:|
| 1 | 22.284 | 22.067 |
| 2 (one binary observation) | **11.983** | **11.907** |
| 3 | 6.040 | 6.132 |
| 4 (hypothetically perfect four-way information) | 0.157 | 0.356 |

This is the **optimistic** expected-error floor over a perfectly informative M-valued measurement, not the error of an implemented probe. At 5 mm desired mean error, a policy using **only one binary observation and one of these four native corrective actions** cannot meet the budget in this empirical cost model. It must obtain more distinct reliable information, acquire an authoritative source readback, use different recovery actions (such as a universally admissible safe correction if one exists), or abstain. A four-way sensor is necessary for this predeclared candidate class, but NOT sufficient to ensure successful physical diagnosis or target tracking.

## Audit, uncertainty and novelty limitations

- Independent second workflow: [full-denominator artifact audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/workflows/audit-two-ack-real-recovery.yml) re-reads the two frozen artifacts, verifies the 160 (robot, seed, true-history, candidate) cells, reconstructs matrix means from original worlds, checks candidate actions and goal are invariant to hidden truth, and independently enumerates the capacity bound. Workflow completion must be checked separately.
- **Eight distinct reset clusters**, not eight patients or 160 independent statistical samples; no independent laboratory replication, sampling-confidence interval, clinical generalization, physical robot hardware validation, contact-safety guarantee or external adoption.
- The induced task is target restoration to an externally chosen canonical goal, not autonomous cube grasping, and its recovery architecture receives an asserted hypothesized history rather than a sensor-estimated history.
- Hidden history for scoring is intentionally available to the experimental auditor after the experiment, never to the action selector. All 160 worlds are actual PhysX, but the best row-of-matrix and M-output capacity comparisons are **offline oracle analyses**.
- The mathematical lower-bound construction is standard constrained decision theory. The *engineering/scientific contribution proposed* is exposing and measuring the coupling of a pinned controller's persistent target semantics, missing ACK state, recovery-action equivalence and information budget. Priority over prior art and task-level generality remain open questions.

**Next falsification gate:** On fresh independent seeds, an actual *public-observation-only* multistep or authoritative readback strategy must be trained/calibrated without using true hidden ACK, compared against NO_ACTION, four fixed recovery arms, and a privileged oracle under identical contact/motion/query budgets, with paired confidence intervals and held-out robot-task performance. A positive gap is not currently established.

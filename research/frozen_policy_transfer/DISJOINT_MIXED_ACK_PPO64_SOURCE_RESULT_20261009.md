# A second, reset-disjoint prospective mixed-ACK frozen-PPO replication

**Source-authenticated result; 9 October 2026.** This is genuine author-operated ManiSkill CPU PhysX, **not third-party replication, hardware validation, or VLA task success**. This result is distinct from, and should not silently replace, the source-frozen original studies. **No historical negative finding is discarded.**

## Central replicated observation

Two released, unchanged third-party frozen PPOs on ManiSkill `PullCube-v1` and `StackCube-v1` operated through an achieved-relative source controller and a stateful commanded-target-relative destination controller. Two consecutive acknowledgements were unavailable, but **the first fault command alone** was genuinely applied or replaced by native target hold (16/16 per task); **the second was physically held in all 64**. The destination action chart and historic public-motion response envelope were fixed before these outcomes. The observer sees only public achieved XYZ before/after the known held/neutral physical step; a controller-private target getter is used only for an explicitly counted fallback or later, audit-only truth verification.

**The new study deliberately repairs an independence defect:** previously cited mixed-ACK 64 reset IDs (860001–860032, 870001–870032) reused 32 IDs from an earlier full-pose-survivor study. This new protocol instead precommitted **PullCube 1180001–1180032 and StackCube 1190001–1190032** and held the pre-existing native runner/classifier code blobs unchanged. These 64 source reset identities are disjoint from the known earlier source cohorts. Different random simulator resets are **not** independently trained policies or evidence of new robot embodiment generalization.

### Actual all-64 source-audited native control results

| Physically stepped policy | Official task successes /64 | Decision-time private target reads /64 |
|---|---:|---:|
| Public complete-pose history identify-or-one-read | **57** | **33** |
| Precommitted task-specific strong route (Pull=geometry-selective; Stack=fixed-read) | 56 | 52 |
| Mandatory fixed step-four read | 57 | 64 |

The public method's actual task-success pairing versus the task-selected strong comparator is **56 both, seven neither, one public-only, zero strong-only**. Its private reads fell by **19/52 = 36.54%** relative to the task-aware strong comparator, **without** an experimental demonstration of a statistically significant task-success increase. The fixed-read baseline matched 57/64 task successes while spending 64/64 private reads.

| Original task resets | Public success | Strong task-conditioned success | Public private reads | Strong private reads | Unique public history / mistaken confident labels |
|---|---:|---:|---:|---:|---:|
| PullCube, 32 | **32** | 31 | **11** | 20 | 21 / 0 |
| StackCube, 32 | 25 | 25 | **22** | 32 | 10 / 0 |
| **Total, 64** | **57** | **56** | **33** | **52** | **31 / 0** |

All eight preregistered eight-seed physical shards and all 64 original trials appeared in the independent auditor, with **576 separately stepped simulator/controller arm worlds**, 32 actual first-command APPLIED and 32 HELD truths, **64 physically held second commands**, and 31 unique public full-history decisions. The 33 undecidable cases caused explicitly counted authoritative reads. **Zero observed wrong confident labels in 31 decisions is not a zero future-error certificate**: even with hypothetical iid Bernoulli draws, the exact one-sided 95% upper bound is `1-0.05**(1/31)` (~9.2%). Here correlated episodes, identical controllers, response envelope assumptions and unseen contact/OOD cases preclude interpreting that as a hardware safety bound.

### Reproduce or falsify at source-level

- [Pre-outcome protocol on fixed branch](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/replicate-mixedack-disjoint64-20261009/research/DISJOINT_MIXED_T2_PPO64_PREOUTCOME_V1.json), Git blob `68443c6a0913f4b6a988e3a0cda74a650c86273f` (source says not full 2×2)
- [Original all-green 10-job genuine native PhysX+independent source audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37916917436), exact branch head `98b2a4259ece268f5fe4f51a77c0b9063f7de3ad`
- [Original complete raw source plus independent full audit GitHub artifact](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37916917436/artifacts/11610315765) — workflow-artifact retention is finite. An immutable Git-tracked SHA256 archive is still required before declaring long-term independent reproducibility.
- [Original source-locked runner](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/replicate-mixedack-disjoint64-20261009/research/frozen_ppo_mixed_ack_truth_physx.py), Git blob `36e672446407435e656cbf8aba6fa2de7c1e9d0e`
- [Independent complete-population source auditor](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/replicate-mixedack-disjoint64-20261009/research/audit_disjoint_mixed_ack_new64.py), Git blob `a54373fe053bf5a7de8504531a17734b778639cf`.
- [Original shard-source launcher](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/replicate-mixedack-disjoint64-20261009/research/run_disjoint_mixed_ack_new64.py), Git blob `90ba8538ed4b2e84f084b2eac50f6269e634332c`.

**Integrity rule:** previous 64-mixed results, disjoint-64, and two earlier all-held cohorts are separately frozen methods/fault regimes; do not collapse them into an iid mega-sample or call the disjoint source cohort an external reexecution. Original complete-trial data are attached to the workflow; the descriptive per-task table above is checked against the eight PhysX shard logs, and the pairing/outcome aggregate against the independent all-population log.

## What is falsified, what remains unanswered

1. **An always-held shortcut cannot be dismissed using only the original all-held ACK generator.** The subsequent first-command physically mixed studies specifically address this threat; they do not test an independently mixed second unknown execution truth.
2. **The four histories are four `belief` candidates, not four demonstrated physical `(t2,t3)` execution combinations.** In the two mixed cohorts, real t3 is held in every case; the four physical combinations `(held,held)`, `(applied,held)`, `(held,applied)`, `(applied,applied)` have **not** all been demonstrated.
3. **Information accounting:** there are two public achieved-XYZ measurements per reached trial (128 measured values total as observation events), one known delivered neutral physical step, and decision-time controller-target reads. The query reduction is **only** against privileged target reads, not total sensing, compute, energy, or wall-clock latency.
4. **No unverified certificates:** empirical response intervals are calibrated envelopes, not formal invariant guarantees under shifted dynamics/contact. All native target checks concern target-setpoints, not collision or grasp safety.
5. **Scientific comparators not yet sufficient for a peak-method claim:** mandatory/fixed-reads and task-ID route are useful, but there is no matched-budget adversarial public-observation method with fully balanced two-ACK physical truth or experimentally established superiority on multiple unseen frozen policies.

## Next decisive preregistered test gate — do NOT claim completed

A real 2×2 truth test must independently choose `t2` and `t3` physical APPLIED/HELD, log both dispatched 6D native actions, preserve original frozen PPOs, and give **every faulted comparator the identical extra known-delivered neutral measurement step** if the public method needs one. The existing t3-as-neutral data are not adequate. Register entirely new reset identities, avoid seed-parity access to any decision rule, use both task strata, and report all 2×2 strata and paired failures.

At equal observed public data, compare **public unique-or-query** against both task-aware strong and an **equal-private-read-budget** risk-aware or active-probe comparator. Track target getter count, public sample count, actual extra actuation steps, per-condition official task success, confident wrong history, refusal and pre-fault losses. If a truthful t3 APPLIED makes the frozen response envelope invalid, abstain/query rather than silently treating a nonneutral command as a neutral probe.

**A 2×2 result, independent outside-lab rerun, real VLA action semantics, and end-to-end VLA-controlled task success are outstanding.** The stronger contribution is a falsifiable, low-information stateful command-transport interface, not a claimed new POMDP theorem or a performance guarantee.

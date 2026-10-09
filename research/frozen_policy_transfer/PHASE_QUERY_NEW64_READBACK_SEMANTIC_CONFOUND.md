# BeliefBridge: prospective 64-state Phase-Value query and fixed-read control confound

**2026-10-09, real original ManiSkill/PhysX pilot. Author-operated, NOT outside-lab reproduced, peer reviewed or robot hardware safe.**

## Original evidence
- [BEFORE-OUTCOME registered 820001-820032/830001-830032 task-phase query rule](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/phase-value-query-fresh64-20261009/research/PHASE_VALUE_QUERY_NEW64_PREREG_V1.json). The rule was suggested by an *earlier seen* 64-state development cohort and is not a claimed uninformed model discovery.
- [Original actual nine-controller-world PhysX run #37911547899 (9/9 jobs success)](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37911547899). Two published, SHA-frozen third-party PPOs, unchanged original K-history geometry, real native held target actions at t2 and t3. **576 genuinely stepped task/control worlds**, 64 independently seeded original resets, not 576 independent trained PPO models.
- [Full source SHA and matched-outcome audit #37912403644 (SUCCESS)](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37912403644), including all 64 rows, no excluded task failures, **1,638 verified post-actual-dispatch controller setpoint checks** and **320 fault-masked attempted commands NEVER counted as physically executed**.
- [Original 64-state source auditor](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/phase-value-query-fresh64-20261009/research/audit_phase_information_new64.py).

## Real outcomes, with strong unchanged-world comparators

| Controller query policy / full native-world rollout | Task success /64 | True privileged controller-target decision reads |
|---|---:|---:|
| Precommitted **phase-dependent** information query | **56** | **58** |
| Old fixed-time readback at t4 | 54 | 64 |
| Strong task-only route: Pull reactive; Stack old fixed-t4 | 53 | **57** |
| Task-blind proactive margin >= .75 | 55 | 63 |
| Reactive robust-or-query on first refusal | 44 | 45 |

By task: phase policy **32/32 Pull** with **26** readbacks; **24/32 Stack** with **32** readbacks. The old fixed-t4 control completed **32/32 Pull and 22/32 Stack**, using 64 combined reads. This is an *observed* resource/success comparison on these particular genuine physics worlds, not statistically powered general superiority.

Paired phase vs simple task-only route: **53 both succeeded, 3 phase-only successes, 0 task-route-only, 8 both failed**; exploratory two-sided exact sign p=0.25 (unadjusted and based on only two frozen PPO/task families). No legitimate population-level superiority claim.

## CRITICAL ORIGINAL CONTROL SEMANTICS CONFOUND (do not hide)

In **Stack original seeds 830004 and 830020**, the old fixed query policy and the new phase policy both read the *exact authoritative controller target at t=4* and spent exactly one read, yet the phase policy completed the task and old fixed failed.

Source inspection identifies a specific causal-path implementation confound to isolate experimentally:

1. The old fixed arm caches `maybe_two = (len(beliefs[name].hypotheses)>1)` **before** its t=4 trusted read.
2. Its `beliefs[name].require_external_resync(actual)` collapses the target-memory belief to **one** controller pose, yet the cached `maybe_two` variable remains True.
3. It enters `if maybe_two` and calls the *single-hypothesis instance of the robust common-command geometry routine*, rather than the direct single-target projection path.
4. The new phase arm sets `maybe_two=False` after its t=4 read and uses normal one-target projection. Therefore these arms are **not identical apart from query timing**, and the observed Stack gain **CANNOT be attributed to smarter query timing**.

This is a *real executable stateful ABI/readback semantic error*, not a theorem or an independently accepted official upstream ManiSkill fix. The correct repair requires invalidating/recomputing every decision predicate that depends on belief cardinality after a privileged resynchronization, and retesting on **new unseen original PhysX seeds**.

## Pre-outcome repair experiment
- [Fresh 16-state register, 920001-920008 Pull and 930001-930008 Stack](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/resync-semantic-control-fresh16-20261009/research/READBACK_RESYNC_BELIEF_INVALIDATION_FRESH16_V1.json).
- [Fixed readback source](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/resync-semantic-control-fresh16-20261009/research/frozen_ppo_fixed_resync_corrected.py). Same published PPO, controller chart, interventions, task-phase query heuristic and finite-state belief; only fixed comparator's cached ambiguity flag reset and resulting source-native single-target command semantics change.
- [Real nine-controller-world PhysX test and fail-closed full Stack equivalence assertion](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37912764218). The corrected post-readback Stack fixed control and Stack phase control should give identical official task outcomes on all eight new Stack seeds. A counterexample will be preserved as failure, not hidden.

## Scientific interpretation
Existing work, including [Krishna et al. (ICLR 2025), *The Value of Sensory Information to a Robot*](https://proceedings.iclr.cc/paper_files/paper/2025/hash/e1126028d9f1f69c13571ec462084d31-Abstract-Conference.html) and [Trombetta et al. (IEEE RA-L 2026), asking when information is worth its cost](https://doi.org/10.1109/LRA.2026.3703246), already studies selective sensing/information value. A prospective high-level contribution would need a *new and correct* framework for **privately stateful controller target memory, explicit action-delivery uncertainty, belief updates and task-sensitive query-cost control**, empirically exceeding strong matched-control/query baselines after readback semantics are fixed. Finite-set geometry and task-conditioned thresholds alone do **not** establish that originality.

No third-party or academic reviewer has accepted this new research result. A SHA audit run by the contributor is not outside-lab scientific replication.

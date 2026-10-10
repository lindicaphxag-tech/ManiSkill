# New physical causal probe + cluster-safe authority gate (2026-10-10)

**Research status:** 96 NEW **native ManiSkill CPU PhysX** scripted controller worlds have been PHYSICALLY stepped, across **16 independent resets**. Four original producer shards succeeded; the *separate whole-population aggregator* must still be verified from workflow job status. This is a native commanded-target mechanism study, **not frozen PPO/VLA task-success improvement**, unannounced performance claim, outside independent validation or hardware safety certification.

## Pre-registered and executed original physics

Preregistered protocol `research/CAUSAL_PROBE_PREREG_20261010.json` Git blob `34cb7673a0d5acd64be25d03b926ea6b0f20b54c`. Workflow [38010868593](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38010868593); original successful shard jobs **114091749061**, **114091749085** (xArm6) and **114091749114**, **114091749126** (Panda).

The actual source runner steps real PhysX CPU Panda and actual xArm6 Robotiq articulation (not relabelled Panda); for each robot, 8 never-used registered seeds × 2 physically held/applied ACK truths × 3 physically delivered probe variants. For each triple, the EXACT commanded-target pose was matched before probing. Native commanded-target readbacks were **AUDIT-ONLY**, not available to select probe or authorize future repairs.

**Raw native controller transition means from four actual producer logs:**

| Real native robot | Zero mean target translation | X mean target translation | Y mean target translation | Correlated physical worlds |
| --- | ---: | ---: | ---: | ---: |
| Panda | 0 mm | 14.999986 mm | 15.000001 mm | 48 |
| xArm6 Robotiq | 0 mm | 14.999986 mm | 15.000001 mm | 48 |

The number of **independent reset clusters is 16**, not 96. On a known controller, a 0.15 normalized target increment producing 15 mm motion in commanded-target space is expected and should NOT be sold as a novel improvement. It confirms nonzero active probing **intervenes** in latent controller state instead of passively observing it. No end-to-end manipulation policy or task success was evaluated by this experiment. No out-of-sample generalization claim follows.

## Distinct algorithmic correctness and statistical gate

Previous finite, exact, action-conditioned chance-constrained POMDP reference runs passed **6/6 OS×Python 3.11/3.13 jobs** in [38010871520](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38010871520). That is **model-conditional** correctness, not calibrated reality.

New work: `research/reset_cluster_authority_calibration.py` computes Clopper–Pearson bounds over INDEPENDENT reset clusters and applies Bonferroni simultaneity over both tails/tasks/frozen threshold-grid. Define:
`Bad(reset)=any wrongly authorized complete target history among registered ACK truths`;
`Cover(reset)=any authorized complete target history`.
Under iid reset clusters within a fixed task distribution, and a frozen score/grid, `P(Bad|Cover)<=U_CP(P(Bad))/L_CP(P(Cover))` with simultaneous confidence. If a task or threshold fails either risk or minimum coverage, **no public authorization is certified: mandatory getter**. The CI tests reject treating four correlated ACK worlds as four iid samples and verify CP numeric endpoints.

**Old owner-operated task-level native PhysX source**, 32 distinct task resets, 128 correlated ACK cells, 1,280 actually stepped comparator worlds: method A and a strong executed same-public B each succeeded **109/128**, while getter counts are **94 vs 98** and both explicitly pay **256** public XYZ samples. [SHA-locked independent original source comparator CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38011580011) PASSED. Do not assert significant superiority or noninferiority.

Old A makes some public state authorizations in **14 of 16 PullCube** reset clusters and **8 of 16 StackCube** reset clusters; no wrong selected history was observed. With a single frozen threshold, two tasks and familywise 95% confidence, one-sided `eta=.05/4=.0125`. Bounds are:

| Source task | n iid resets | any authorized | any wrong | U(bad) | L(any covered) | U(cond. wrong) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| PullCube | 16 | 14 | 0 | 0.23957 | 0.58046 | **0.41273** |
| StackCube | 16 | 8 | 0 | 0.23957 | 0.21953 | **1.00000** |

These are conservative **confidence limits**, NOT actual error probabilities. Old source does NOT substantiate a “less than 10% selective error” guarantee. A new exactly source-pinned retrospective auditor `research/calibrate_original_physx_128.py` is provided. Source labels being retrospective means this is a **power falsifier**, NOT a fresh separately calibrated experiment.

## Compared with accepted top robotics papers

- [RSS 2024 TAMPURA](https://roboticsproceedings.org/rss20/p118.html): risk-aware uncertain task/motion planning, actual robots.
- [RSS 2025 Map Space Belief Prediction](https://roboticsproceedings.org/rss21/p039.html): learned calibrated belief propagation with real zero-shot shelf transfer.
- [CoRL 2025 B-COD](https://proceedings.mlr.press/v305/puthumanaillam25a.html): real platform just-enough sensing, measured energy saving.
- [ActionShift public baseline](https://github.com/Archerkattri/actionshift): hidden-action-contract adapted belief/probe/learned methods on actual ManiSkill tasks.

Exact finite POMDP chance constraints, CP intervals, Bonferroni and cumulative target memory are NOT inherently new theorems. An RSS/CoRL flagship requires **new heldout frozen-policy task improvements at same public observation / privilege / intervention cost**, independent sufficiently powered risk calibration with nontrivial coverage, cross-controller semantic generalization, contact/latency/energy outcomes, and outside laboratory reproduction. Fail those gates: preserve negative results and refrain from top-conference superiority claims.

**Remaining pending tasks:** 96-world full artifact audit, cross-platform statistical CI, SHA-pinned old-source retrospective CP audit, then independent training/calibration/test full task study. Do not label pending tasks completed.

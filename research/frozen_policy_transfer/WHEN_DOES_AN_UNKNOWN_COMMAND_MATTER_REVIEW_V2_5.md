# When Does an Unknown Robot Command Actually Matter?
## Matched-Reset Four-Truth Experiments, Belief-State Failure, and the Limits of Public-Motion Recovery

*Evidence-first manuscript v2.5 · 9 October 2026 · research draft, not a peer-reviewed or accepted top-conference paper.*

### Abstract

A robot receiving uncertain action-execution acknowledgements may propagate several possible previous commanded targets, even when its frozen task policy and native action chart remain intact. The resulting uncertainty is discrete but consequential: acting on the wrong target history can redirect the next controller-relative command, and successful manipulation does not prove the true hidden state was recovered. Previous ManiSkill frozen-PPO experiments isolated 64 reset states under four actual applied/held pairs of hidden acknowledgements, but different fault combinations were assigned to different initial states. We therefore preregistered a prospective two-by-two **same-reset** factorial experiment, crossing four physically dispatched unknown-ACK truths within each of 32 untouched initial task states. An initial 128-cell execution produced all 1,152 intended physical simulator control-world instances but failed its independent whole-population audit because **seven StackCube original reset states differed across conditions in their initial source-policy observation hashes**. We retain this failure and reran the unchanged physics/policy/classifier using disclosed common-random-number initialization and all four truth conditions in one Python process per shard. The explicitly **amended** study passed independent exact initialization checks over all 32 same-seed four-condition groups. Across 128 real PhysX seed–truth cells, a public complete-target-history selection or counted fallback state read completed **111 tasks with 95 privileged reads**, versus **104 tasks and 116 reads** for a physically executed task-labelled comparator, **105 tasks and 128 reads** for fixed-time private readback, and **70 tasks without reads** for an always-held assumption. The apparent task difference is **not statistically demonstrated** after accounting for within-seed pairing (32-cluster exact label-swap sensitivity p=0.1484; exploratory bootstrap per-cell difference interval [0, 0.117]). An additional original-physics source audit finds that **32/128 public-versus-task-aware comparisons had different native six-degree-of-freedom actions at the second ambiguous execution**, even though all three principal comparator worlds paid the same native neutral probe step. Therefore the task difference is an *end-to-end controller-method effect*, not an isolated causal effect of deciding to query private target memory. An earlier matched-public-information experiment separately supplies a genuine counterexample: a frozen PPO task succeeded while its public observer confidently chose a commanded target **67.6 mm and 0.0536 rad** away from the true state. Together, these findings expose a tractable, falsifiable hidden-controller-memory problem, but neither an unconditionally reliable motion witness nor an algorithmic dominance result against a strong equal-information actively probing opponent.

**Keywords:** uncertain command execution, target-relative robot control, finite latent execution histories, model misspecification, matched initial-state experiments, selective private-state sensing, manipulation policy transfer.

## 1. Problem: target history, not syntax

Consider a frozen policy \(\pi\) whose source controller defines a native relative action from achieved end-effector pose. A destination controller instead composes native displacement \(u_t\) from the last *commanded* target \(M_t\in SE(3)\). Given a physically applied/held execution truth \(z_t\in\{0,1\}\),

\[
M_{t+1} =
\begin{cases}
F(M_t,u_t), & z_t=1,\\
M_t, & z_t=0.
\end{cases}
\]

A missing execution acknowledgement hides \(z_t\). Two such unknown events produce up to four native target-pose histories, despite unchanged action-vector dimensionality and unchanged frozen policy weights. The achieved end-effector pose \(X_t\) is publicly observable; the controller's commanded target register \(M_t\) is private and counted when read.

A finite-history adapter reconstructs candidate full position-plus-quaternion targets from the known native action recurrence, then considers whether the observed achieved XYZ motion over a physically stepped known-delivered neutral target command is compatible with precisely one complete candidate. A conservative authority gate accepts one native target pose or reads the actual private commanded target.

Crucially, the gate's empirical response model can fail under different physical dynamics or contact. Set-membership uniqueness within an invalid model is **not** physical-state truth. A successful frozen task does **not** certify target identity: an original PullCube trial (seed 1760020) completed even though its public observer chose a target 67.6 mm and 0.0536 rad from the native controller's actual target.

Broader action-contract beliefs, robotic active identification and bounded probes predate this study; ActionShift/DualABI provides a more extensive official benchmark. Our narrower claim is a source-auditable account of **target-memory ambiguity after physically uncertain execution** and its effects in actual frozen-policy control.

## 2. Three separate estimands that must never be conflated

**Task end point.** \(Y_{s,z,m}\in\{0,1\}\) is the actual ManiSkill official task outcome for task/reset seed \(s\), two-bit execution truth \(z\in\{\mathrm{HH,AH,HA,AA}\}\), and adaptation method \(m\).

**Information cost.** \(R_{s,z,m}\in\{0,1\}\) counts private controller-target register reads at the method's decision step. Public achieved XYZ events and known-delivered physical neutral actions are charged separately.

**Authority correctness.** \(C_{s,z,m}\) records whether a confidently selected complete SE(3) latent history exactly matches the actual native commanded-target pose; verification requires a *strictly audit-only* postphysics true-target getter, never an inference input.

These quantities have different denominators. Binary task success may be true even when the adapter's hidden-history identity is false; an arm may fail to reach both fault steps; 1,152 physical controller instances are not 1,152 independent task-reset samples.

## 3. Source-locked two-by-two original experiment

### 3.1 Truly crossed physical truth rather than between-seed imbalance

The [original registered protocol](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/paired-four-truth-singleprocess-reset-audit-20261009/research/PAIRED_COUNTERFACTUAL_2X2_PPO128_PREOUTCOME_V1.json) chose **PullCube 1310001–1310016** and **StackCube 1320001–1320016**, sixteen distinct source reset identities per task. Within each seed, four actual physically dispatched unknown-ACK conditions were precommitted:

| True t2/t3 native command execution | Meaning | Independent simulator treatments |
|:--|:--|--:|
| HH | First physically held, second physically held | 9 |
| AH | First physically applied, second physically held | 9 |
| HA | First physically held, second physically applied | 9 |
| AA | First physically applied, second physically applied | 9 |

There are **32 independent original seed identities**, **128 seed–truth cells**, and **nine separately created/stopped native PhysX controller treatment worlds per cell (1,152 total)**. Both published PullCube/StackCube PPO checkpoints and the original native target-relative action chart remained unchanged; no policy retraining or after-outcome response-model epsilon tuning took place. Importantly, the statistical grouping unit is the **seed**, not each of the 128 cells or each of the 1,152 simulator worlds.

### 3.2 First attempt FAILED and remained public

The [first physically executed 16-shard run](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37930607707) completed every PhysX shard but **its original independent all-source factorial audit failed**. Exact hashes of the initial projected public source-policy observation did not agree across the four truth conditions on **seven of sixteen StackCube source seeds**. They did agree for all sixteen PullCube seeds and nine StackCube seeds. A [separate source-hash forensic audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37932125707) recovered **all 128 original physical cell sources** and preserved their own original SHA-256 while explicitly rejecting the mischaracterization of the first execution as a successful whole-factorial causal study.

The first failure is not a low task score and not automatically a data corruption. It is an *initial-state matching validity failure*: different original projected start observations block an exact same-start counterfactual comparison. We do not selectively drop the seven nonidentical start groups and claim a 25-seed preregistered result.

### 3.3 Transparently amended common-random-number repetition

The disclosed [implementation amendment](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/paired-four-truth-singleprocess-reset-audit-20261009/research/PAIRED_ACK_SINGLE_PROCESS_RESET_REPAIR_DISCLOSURE.json) ran **all four physical execution truths for each same seed inside the same Python process** and reset Python/NumPy/Torch from that original source seed before each world-group execution. It reused the original source-native physical intervention code, frozen checkpoints and original response classifier, and **did not alter original seeds, faults, decision rules or epsilon**.

This is an **amended repetition informed by a known first-run implementation failure**, not pristine independent prospective confirmation. Its [six-job actual PhysX and independent full128 audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37931800065) passed every source-initial-observation SHA256 equality check across all 32 seed groups. A second [nine-independent-artifact-hash and original data integrity run](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37932708148) recomputed the entire source, rejected five intentionally falsified original datasets and permanently archived all 32 physically executed original source/auditor JSONs, four reset-hash provenance records, two full-population auditors and 32-seed reviewer statistics.

## 4. Amended genuine PhysX task results

| Source-native treatment | Official successes /128 | Actual controller-private target reads |
|:--|--:|--:|
| Public unique complete-history identification, else counted read | **111/128** | **95** |
| Task-labelled selective-or-fixed strong comparator | 104/128 | 116 |
| Fixed true target read at t5 | 105/128 | 128 |
| Always assume two commands were held, no target read | 70/128 | 0 |

The source-level pairing between public observer and the task-aware comparator is **102 both successful, 15 neither successful, 9 public-only, 2 strong-only**. The paired mean task difference is \(7/128=0.0546875\) successes per seed–truth cell. The source-seed-cluster exact method-label sign-swap sensitivity is **p=0.1484375**, and 5,000 exploratory 32-cluster bootstrap resamples give a task difference percentile interval **[0, 0.1171875]**. The test does not prove higher population task success, superiority or noninferiority, and the sign-swap calculation is sensitivity under clustered label-exchangeability assumptions, **not** a randomized assignment test.

The public observer saves **21 real private reads** relative to the task-labelled strong controller, but it also consumes **256 public achieved-XYZ sampling events** across 128 actual executed neutral steps. The observed break-even ratio is \(21/256\approx 0.082\) private reads per XYZ event, *before* sensor latency and physical control costs. This is an information-accounting result, not an unconditional total-cost improvement.

The full source audit records **no confidently wrong public target-history identifications on these 128 cells**, but another independently executed, same-public-information 64-reset experiment **did contain one confidently wrong pose while the task still succeeded**. Zero observed wrong on an amended in-family trial set is not a physical safety or distribution-shift bound.

## 5. Reviewer-critical remaining confound: t3 native action is NOT fully matched between methods

An additional source-only physical actuation audit [independently validated against the permanent original 128-cell archive](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37933243054) distinguishes *same seed/fault truth* from *same physical native command before the first information decision*:

| Actually recorded native actions /128 | Public vs task-aware strong | Public vs fixed reader |
|:--|--:|--:|
| t2 native six-dimensional physical command exactly identical | **128** | **128** |
| t3 native six-dimensional physical command exactly identical | **96** | **64** |
| t4 known-delivered neutral controller action actually stepped in both main methods | **128** | **128** |

All three primary comparator arms physically paid for the neutral controller action in **all 128 cells**; the separate strict-common-exact treatment usually refuses earlier and therefore should **not** be included in a claim that *every* arm shared t4. The public observer obtained two achieved XYZ observations in each actual cell; the task-aware rule is **not** an independently optimized equal-public-information active inference algorithm.

The missing native t3 action match in **32/128 public-versus-task-aware** comparisons means the 111 vs 104 task difference is a *whole-method closed-loop comparison* involving different commands and subsequent states, **not** an isolated effect of information acquisition or selective target-memory readback. This limitation cannot be eliminated by adjusting p values or increasing the rhetorical weight of the task endpoint. A new controlled experiment must deliberately copy the same source public t3 native action to the comparator arms before their different information decisions (as a separate previous matched-prefix research program already did on other cohorts).

## 6. Task/ACK interactions: observed, not established as general mechanisms

A difference-in-differences view is possible because all four truth conditions are physically stepped at each of 32 original seeds:

\[
I_{s,m}=Y_{s,AA,m}-Y_{s,AH,m}-Y_{s,HA,m}+Y_{s,HH,m}.
\]

The original [reviewer cluster-interaction archive](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/paired-four-truth-singleprocess-reset-audit-20261009/research/frozen_policy_transfer/evidence/amended_same_seed_fourtruth_original128_1310001_1320016/source_only_reviewer_32cluster_statistics.json) reports mean \(I_s=-0.03125\) for public membership and \(I_s=0.0625\) for the task-aware strong method. Exploratory 32-seed bootstrap 95% intervals are respectively **[-0.25, 0.15625]** and **[-0.09375, 0.25]**. Both include zero. These are descriptive, and native commands themselves may change after a different first execution truth; the estimates should **not** be called randomized single-factor causal interactions without further intervention control.

Success heterogeneity between PullCube and StackCube and between HH/AH/HA/AA is preserved in the source JSON instead of averaged away. The full original per-cell audit reports physical faults actually reached, sample-specific private readbacks, public confidence, and whether other controls reached the shared neutral step; no negative case was silently excluded.

## 7. Why the unresolved contribution is deeper than read-count reduction

A controller can be wrong about its private commanded target and still reach the binary task goal. Conversely, a unique publicly feasible history may be an artefact of a misspecified motion model, not a reliable observation of the actual native target. To achieve an exceptional robotics-main-conference **algorithmic** contribution rather than an honest mechanism benchmark, a method would need to exploit a *new, independently justified information channel* or causally discriminative bounded action probe, and then prove a prospective **authority-risk vs read-cost vs task-success** benefit against serious equal-resource opponents.

Current candidate physical channels include **public achieved orientation**, not just achieved XYZ, and action-conditioned response under a deliberately selected, physically charged probe. Public SO(3) feasibility in separate genuine native PhysX frozen-PPO episodes is now a source-audited input channel, but *availability of the signal* is not demonstration of its target-history identification accuracy or any improvement in manipulation success. Earlier doubled passive probing and known-t1 dynamics witness experiments already produced adverse null/OOD results and should remain negative controls rather than hidden failed methods.

Statistical selective-confidence limits require sufficient independently sampled *accepted* states per task and actual controller-distribution validity. A source-implemented exact binomial risk/coverage gate in a separate PR has passed cross-platform adversarial tests, **but its preregistered larger-scale physical calibration/test stages have not run**. A bound on task success is not a bound on correctly identified private control memory. Existing ActionShift/DualABI and other active-belief/action-calibration approaches must be compared on equal public sensing, actuation and privacy budgets, not displaced by a deliberately conservative uncalibrated 0.95 score.

## 8. Reproduction, evidence, and explicit editorial conclusion

- [First-run FAILED whole-factorial audit, original 16 real PhysX shards intact](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37930607707).
- [Independent first-run 7 StackCube same-reset initial hash mismatches, full 128 original source files verified](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37932125707).
- [Disclosed amended actual source-unchanged 1,152 physical simulator worlds, 32 exact matched reset clusters and 128-cell full auditor](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37931800065).
- [Permanent hash-pinned 128 original source task/fault episodes, two independent whole-source audits and five forgery rejections](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37932708148).
- [Independent exact t2/t3 command equality and all-three-main-controls charged neutral audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37933243054).
- [Full original native PhysX evidence archive, exact 32-cluster paired statistics and verified four-truth interaction table](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/paired-four-truth-singleprocess-reset-audit-20261009/research/frozen_policy_transfer/evidence/amended_same_seed_fourtruth_original128_1310001_1320016).
- [Earlier source-authenticated false hidden-controller-memory case despite official PPO task SUCCESS](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37925148881).
- [Independent 64-reset actual same-public-information 0.60 tuned stronger competitor: 59/64 for both, only one private-read difference](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37929461571).

**Conclusion supported now.** The research establishes a reproducible physical execution-history uncertainty problem, an actual hidden-memory false-authority witness that binary task success masks, and a fully crossed same-reset experiment with transparent identification of both initial-state and preinformation action confounds. It has **not** yet demonstrated statistically significant superiority over strong source-matched competitors, verified zero wrong-history admissions, a new physically certified model-validity mechanism, genuine cross-controller task transfer, real communication ACK-loss survival, learned VLA fault recovery, outside-institution independent reproduction or top-conference publication acceptance. Those are the gates for a truly stronger algorithmic representative work, not conclusions to be written into existence.

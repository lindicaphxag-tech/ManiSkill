# When Does an Unknown Robot Command Actually Matter?
## Matched-Reset Four-Truth Experiments, Belief-State Failure, and the Limits of Public-Motion Recovery

*Evidence-first manuscript v2.6 · 9 October 2026 · preregistered 256-cell source recovery, strict action-confound limits, research draft; not a peer-reviewed or accepted top-conference paper.*

### Abstract

Robot policies can retain uncertainty about the last *commanded* end-effector target after a command executes without an acknowledgement. When a destination controller interprets actions relative to that hidden target, the same policy action may induce different next physical commands. We investigate whether public achieved-pose observations recover sufficient execution-history information without accessing the private target register. We preregistered an independently seeded, two-task, four-truth factorial study using frozen ManiSkill PullCube and StackCube PPOs: **64 task-reset clusters**, each crossed with four genuinely applied/held ACK histories, giving **256 physically executed conditions and 2,304 native controller comparison worlds**. An independent complete-source audit recovered all original outcomes after the first CI failed because it inadvertently invoked an old 128-cell auditor; the simulator data and pre-outcome protocol were unchanged. Complete-history public inference with fallback achieved **221/256** official task successes with **195** true private target reads; a task-aware physically executed comparator obtained **202/256** successes with **221** reads, fixed readback achieved **210/256** with **256** reads, and a zero-read held-history assumption achieved **133/256** successes. The first paired comparison yields a **+7.42-percentage-point** task-success difference; treating the 64 original reset clusters as statistical units gives an exploratory exact sign-swap sensitivity **p=0.00241** and cluster-bootstrap 95% interval **[+3.13,+12.11] percentage points**. However, native-action forensics show that **64/256** public-versus-task-aware pairs dispatch different six-channel control actions at the second missing ACK, preventing attribution of the entire gain solely to public-state inference. On the 128 *preassigned t3-held* cells, t2/t3 native commands match, but that subgroup alone does not establish a general causal mechanism. A separate physically successful PPO task with a confidently misidentified controller target displaced **67.6 mm** from truth further shows why task success cannot certify hidden-state correctness. The supported result is an auditable end-to-end fault-recovery advantage under this controlled controller family, not a proven safety guarantee, cross-robot VLA transfer or superiority to a fully matched actively probing baseline.

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

## 8. Confirmatory expansion: 64 truly new task-reset clusters and all 256 physical ACK truths

### 8.1 Why the expansion matters

The initial 32-cluster amended study was valuable for fault-mechanism investigation but insufficient to establish a 64-cluster main claim: (a) first execution failed its exact initial-state matching check, (b) its +7/128 end-to-end success difference did not pass a 32-cluster sensitivity test, and (c) comparator commands were often unequal *before* the first differing information decision. Rather than silently pooling that pilot, we committed the [separate 64-cluster, four-truth pre-outcome protocol](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/confirmatory-256-original-source-recovery-20261009/research/CONFIRMATORY_FOUR_TRUTH_NEW64CLUSTERS_PREOUTCOME_V1.json). PullCube seeds 3210001–3210032 and StackCube seeds 3220001–3220032 were disjoint from earlier development cohorts. Each seed is crossed with all four true physical ACK execution patterns: held/held, applied/held, held/applied and applied/applied. Nine actual native controller treatment worlds per original seed/truth cell yield **2,304 separately physically stepped simulator worlds**. The experimental unit for inference is **64 source task/reset seed clusters**, not 256 independent initial states and certainly not 2,304 independent robots.

The initially completed [physical run 37934425888](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37934425888) executed all 32 physical shard jobs, but its final audit failed. The traceback was **not** a bad physical result or missing original seed: the workflow invoked \`research.audit_numeric_parity_ack_factorial\`, whose expected denominator was the OLD 128-case pilot, instead of the already source-frozen \`research.audit_confirmatory_four_truth_new64clusters\`, which expects all 256 original cases. This is publicly retained. A new [source-only recovery and independent whole-population re-audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37936593520) succeeded using the original, unchanged physical ZIP artifacts and all 64 original seed clusters. [Second original-source verifier](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37937679903) also passed after correcting artifact pagination. The archive with raw original 32 shard pairs, SHA256 and full 256 physical-truth per-seed audit is [here](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/confirmatory-256-original-source-recovery-20261009/research/frozen_policy_transfer/evidence/confirmatory_64cluster_256truth_orig_3210001_3220032).

All original seed/truth cells meet the preregistered **5e-5** tolerance in initial public policy observations and achieved SE(3) poses across the four true ACK treatments; the recorded maximum initial numerical gap was **0**. The independent source auditor verified all 256 true two-ACK executions, no early unexposed public reference, and all four patterns for all 64 source task/reset clusters. The physical native-controller 6D actions were actually stepped; the intended ACK labels were never used as observer input.

### 8.2 Primary real-task results and exact denominator

| Fully source-audited method, 256 genuinely stepped task/truth cells | Official task successes | Decision-time private target reads |
|:--|--:|--:|
| Complete public execution-history belief + source-frozen fallback | **221 / 256 (86.33%)** | **195** |
| Task-aware frozen comparator (*task-specific comparator selection*) | 202 / 256 (78.91%) | 221 |
| Mandatory target-register readback at fixed t5 | 210 / 256 (82.03%) | 256 |
| Assume both unacknowledged commands were held; no target read | 133 / 256 (51.95%) | 0 |

Paired original public versus task-aware control outcomes: **197 both succeed, 30 neither, 24 only public succeeds, 5 only comparator succeeds**. Thus 221−202 = **19** additional task successes, an end-to-end paired improvement of **7.421875 percentage points**. A 64-seed-cluster exact method-label sign-swap sensitivity test yields **p=0.002410888671875**; original-seed cluster bootstrap with repeated four-truth rows held together yields **[0.03125, 0.12109375]** for the exploratory interval. These are descriptive conditional on the method-label sign-swap/exchangeability model, not an experiment randomly assigning the two algorithms to independent robots, not error-rate certification, and not a license to report 256 independent per-row p values.

The public observer consumed **512 achieved-XYZ measurement events** in addition to the shared physically executed t4 neutral control step, saving **26** true private target-register reads against the task-aware method. It is therefore **not proven to use fewer total sensing resources**: it only uses fewer *privileged target-register reads*. If comparable sensor costs are not known, the correct result is a two-resource Pareto tradeoff, not a universal latency win.

Task decomposition: PullCube public 123/128 versus task-aware 113/128; StackCube public 98/128 versus task-aware 89/128. The source auditor retained every original task failure, including all eight joint ACK-truth strata (32 per task/truth). There were **zero observed confidently incorrect complete histories** on this new cohort, but the historical source-authenticated PullCube 1760020 wrong 67.6-mm target-selection witness survives independently and must not be erased by later clean samples. With finite, correlated confident decisions and possible physical regime shifts, zero observed errors in this cohort is **not** a conditional safety bound.

### 8.3 Mechanistic source audit: the critical causal limitation

A [separate reviewer-triggered actual native-action forensic CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37937110132) traversed the unchanged 256 original simulator trials and compared the true **physically dispatched native 6D action at t2 and t3** for the public observer, task-aware comparator, and fixed reader. All main methods performed the same known-delivered neutral t4 action, but equality of a probe action does not guarantee equality of earlier controller commands.

The original observed public-vs-task-aware t3 native action matched exactly in **192/256** cells, and public-vs-fixed t3 action matched in **128/256**. Differences in native actuation upstream of information acquisition are a substantive causal confound: a later task-success difference may arise from command content, not from choosing when to query the controller's hidden target memory. The full 221/256 vs 202/256 comparison therefore measures **end-to-end controller-strategy differences**, not a purified "value of public information" effect. This physical source audit materially limits the claim in the abstract, main figures and conclusions.

One preassigned truth stratum helps test mechanisms without retrospective success selection. Under **second command physically held** (two of four factorial truths, 128 original cells), the physically dispatched t3 action is the all-zero native hold in all three methods, and the source forensic audit also confirms t2 equality. In that stratum, public **111/128** succeeded versus **105/128** for task-aware control; the 64-seed cluster sensitivity p was **0.03125**. However, this is a **subgroup analysis after seeing results**, one of several task/truth comparisons, and post-t5 control strategies still differ. It is neither a predeclared primary test nor evidence that the information decision *alone* explains the success difference. The observational subset of 192 matched t2/t3 actions is selection-on-observed-actuation and is not randomized; its outcome should only serve as an additional sensitivity check.

### 8.4 Why this is a stronger research narrative, without a top-tier acceptance claim

Relative to the earlier pilot, the independent 64-cluster experiment moves from a non-significant pilot to an observed stronger end-to-end advantage on disjoint reset states, with exact first-state matching, a fully crossed physical applied/held intervention and immutable replayable source records. Its distinct technical contribution is a **hidden execution-history validity and native-controller semantic transfer problem**, rather than a generic prompt or simulated confidence score.

But the field already has strong structured belief, bounded active probing and task-regret-guided adaptation, including [ActionShift/DualABI](https://github.com/Archerkattri/actionshift). The current comparator is task-labelled and partially uses different true native commands, not a formally equal-budget official implementation. We must therefore distinguish (1) recovery under the current known-controller action chart, (2) resource tradeoffs between public pose sensing and privileged target reads, (3) wrong confident authority even when tasks complete, and (4) actual out-of-model/cross-controller robustness. Only the first three have substantive native-physics evidence; the fourth is open.

### 8.5 Current independent new algorithm experiment: joint public SE(3) history

A fresh study [freezes 64 entirely new original seeds](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/joint-public-se3-execution-new64-20261009/research/JOINT_PUBLIC_SO3_XYZ_FROZEN_NEW64_PREOUTCOME_V1.json) and executes an actual new **joint XYZ+SO(3)** public history gate on true native PhysX. A prior 16-state [real measured-quaternion developmental frontier](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37936002962) selected the **0.02-radian** response arc threshold after inspecting previous data; this is openly labelled training rather than calibration. The new algorithm requires the same complete SE(3) target-history candidate to fit BOTH the achieved-XYZ motion tube and genuinely measured achieved-quaternion rotation arc before it may skip one private target read; otherwise it abstains. It is compared within identical native predecision physical prefixes to original XYZ-only inference and fixed private read. The quaternion is an extra information *channel* of the same actual robot end-effector pose sensor, not a separate independent device and not an uncharged sensor measurement. No task success is attributed to this algorithm until original new64 physical full-source audit succeeds.

## 9. Reproduction, evidence, and explicit editorial conclusion

- [First-run FAILED whole-factorial audit, original 16 real PhysX shards intact](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37930607707).
- [Independent first-run 7 StackCube same-reset initial hash mismatches, full 128 original source files verified](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37932125707).
- [Disclosed amended actual source-unchanged 1,152 physical simulator worlds, 32 exact matched reset clusters and 128-cell full auditor](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37931800065).
- [Permanent hash-pinned 128 original source task/fault episodes, two independent whole-source audits and five forgery rejections](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37932708148).
- [Independent exact t2/t3 command equality and all-three-main-controls charged neutral audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37933243054).
- [Full original native PhysX evidence archive, exact 32-cluster paired statistics and verified four-truth interaction table](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/paired-four-truth-singleprocess-reset-audit-20261009/research/frozen_policy_transfer/evidence/amended_same_seed_fourtruth_original128_1310001_1320016).
- [Earlier source-authenticated false hidden-controller-memory case despite official PPO task SUCCESS](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37925148881).
- [Independent 64-reset actual same-public-information 0.60 tuned stronger competitor: 59/64 for both, only one private-read difference](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37929461571).

**Conclusion supported now.** The research establishes a reproducible physical execution-history uncertainty problem, an actual hidden-memory false-authority witness that binary task success masks, and a fully crossed same-reset experiment with transparent identification of both initial-state and preinformation action confounds. It has **not** yet demonstrated statistically significant superiority over strong source-matched competitors, verified zero wrong-history admissions, a new physically certified model-validity mechanism, genuine cross-controller task transfer, real communication ACK-loss survival, learned VLA fault recovery, outside-institution independent reproduction or top-conference publication acceptance. Those are the gates for a truly stronger algorithmic representative work, not conclusions to be written into existence.

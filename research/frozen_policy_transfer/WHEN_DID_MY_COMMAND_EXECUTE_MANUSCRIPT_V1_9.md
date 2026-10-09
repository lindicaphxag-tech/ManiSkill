# When Did My Command Execute?
## Observability and Information–Success Trade-offs in Stateful Frozen-Policy Transport

*Research manuscript v1.9 · 9 October 2026 · author-operated source-audited PhysX; no outside-lab replication, peer review or acceptance*

**Zhibo Zhang** · Hangzhou Dianzi University  
**Manuscript authorship and any collaborators must be confirmed before submission.**

### Abstract

Frozen robot policies can fail when transferred between controllers that interpret end-effector actions relative to different internal reference states. With missing execution acknowledgements, even a known controller chart admits multiple plausible commanded-target histories. We examine whether public end-effector motion can identify an entire latent SE(3) history and selectively replace a privileged native-controller target read. Our adapter propagates finite target-history hypotheses, admits a unique history under a fixed empirical motion-compatibility test, and otherwise requests an authoritative read. We evaluate two released frozen PPO policies on ManiSkill PullCube and StackCube with two physically applied or held unknown-ACK actions. Prior studies exposed differing pre-query physical commands, and then differing post-query state-machine implementations, as comparison confounds. To remove both, we preregistered 64 further unseen reset states and executed 576 native PhysX controller-policy worlds. The public and mandatory-read arms shared actual pre-query native commands, a neutral probe, audit-matched predecision achieved and target poses, and one identical post-query belief container and action compiler. Both achieved identical paired official outcomes: 53 jointly successful states, 11 jointly unsuccessful states, and zero discordances. The public arm used 48 privileged target reads versus 64 for mandatory readback (25% fewer), identifying 16 histories without observed error in this cohort. A separate prospective physical cohort contained one confidently wrong public identification, precluding a zero-risk claim. Byte-preserved original evidence and independently repeated source audits document the outcomes and the preceding failed attempts. The finding is an implementation-controlled selective-information trade-off, not proven noninferiority, generalized physical safety, VLA transfer, or external laboratory replication.

**Keywords:** robot learning; controller semantics; latent execution state; command acknowledgement; set-membership identification; frozen-policy transfer; selective observation.

---

## 1. Problem: execution truth is neither action syntax nor observable tool pose

The third-party source PPO policy \(\pi\) issues an achieved-relative end-effector action \(a_t\) based on the observation \(o_t\). The destination's native `pd_ee_target_delta_pose` controller instead maintains a *previous commanded target* \(M_t\). With an uncertain execution indicator \(z_t\), the native target update can be written

\[
M_{t+1}=
\begin{cases}
F(M_t,u_t), & z_t=1,\\
M_t, & z_t=0.
\end{cases}
\]

A missing acknowledgement does not disclose \(z_t\). Two missing acknowledgements can therefore leave up to four distinguishable commanded-target histories, even when the action chart \(F\) is completely known. Using achieved pose as the previous commanded target, or treating silence as a successful execution acknowledgement, is not a logically justified reconstruction. For a frozen policy this can invalidate the meaning of every subsequent native command.

The question addressed here is deliberately narrower than discovering arbitrary unknown robot-action interfaces: *given a known native controller chart and complete candidate histories, when can an ordinary public motion measurement replace an explicit privileged target-state read without sacrificing observed manipulation-task completion?*

## 2. Method: identify a complete discrete history, not independent pose coordinates

Let \(H_t=\{h_1,\ldots,h_K\}\) denote the complete set of possible native commanded-target poses computed from documented initial-state evidence and acknowledged/unknown native actions. Each \(h_i\) contains **both** XYZ target position and a quaternion target orientation. No simulator-private actual target getter enters its construction.

A known-delivered neutral native target-delta is executed at the second unknown-ACK fault step. Let \(x\) and \(y\) be the public achieved XYZ positions immediately before and after that *actual* physical step. The frozen response model is

\[
y=x+\alpha(M_i^{xyz}-x)+e,\quad
\alpha\in[0,1],\qquad \|e\|_2\le\epsilon_{task}.
\]

For each candidate history \(h_i\), compute the minimum Euclidean residual \(r_i\) between observed \(y\) and the complete interval of public positions predicted by \(h_i\). The task-specific empirical model tolerances were frozen from different historical PhysX seeds: \(\epsilon_{Pull}=0.0069443\,m\) and \(\epsilon_{Stack}=0.0071909\,m\). No test-set calibration or PPO updates are allowed.

**Authorize the complete latent history index \(i^*\)** only when exactly one residual \(r_{i^*}\le\epsilon_{task}\), and **every** competing history has \(r_j>\epsilon_{task}+0.002\,m\). The chosen history includes its own full target orientation. It is *not necessary* that all possible histories have identical orientations. This is a straightforward finite set-membership compatibility result, not a novel identifiability theorem: if two candidate public observation sets intersect, no position-only classifier can guarantee differentiation for a shared observation.

If no unique history meets the predeclared test, the adapter reads the authoritative native target exactly once at step four and resynchronizes. Every actual native command remains subject to the existing 0.05m positional and 0.05rad orientation **commanded-setpoint** admission contract. An action may pass this contract without assuring trajectory tracking, safe contacts, or task completion.

The public measurement is not free: the new controller explicitly uses two achieved-XYZ samples per task. It adds **no extra actuated probe step**, as the measured motion occurs during the common physical fault protocol. The experiments count private target reads separately from public sample access, simulator audit-only target getters, and actual native action dispatch.

### Failure and observability boundary

Two histories with identical XYZ target positions but different target orientations are not distinguishable under the position-only response model above. More generally, an empirical motion envelope can fail when contact, load, phase, actuation delay or observation noise changes; an erroneously unique hypothesis can then be harmful. Our physical study records every such confident mistake against a private target getter **only after** real physical execution, never as the method's decision input.

## 3. Prospective experiment: 64 frozen PPO reset states, 512 physical controller worlds

The [protocol was fixed before new execution](../PPO_DISCRETE_HYPOTHESIS_NEW64_PREOUTCOME_V2.json) (Git blob `b8c5205ca949720a2d39396c9f8c711e65d7982b`), selecting PullCube reset seeds `840001–840032` and StackCube `850001–850032`. Both original third-party released PPOs and their SHA-256 hashes were checked before physical rollout. The action interface is the real ManiSkill Panda controller, with source `pd_ee_delta_pose` converted to destination `pd_ee_target_delta_pose`.

In each of 64 new reset states we stepped **eight separate actual native PhysX controller-policy worlds** with the identical reset seed and relevant native fault pattern: no-fault source context, fully privileged oracle, optimistic unknown-ACK assumption, exact-or-refuse, bounded zero-query, geometry-triggered selective query, fixed step-four authoritative read, and the new public-identify-or-read controller. Actual native target holds occur at steps two and three, with gripper unchanged and missing ACK conveyed to the adapter. The test represents a **physical zero/hold injection**, not genuine network packet loss; 64 separate reset states are not 64 independently learned policies or robot embodiments.

The principal non-strawman baseline uses a **frozen task-only rule selected before the new seeds**: choose the previously developed geometric selective-query policy on PullCube and the fixed step-four query policy on StackCube. The source code physically runs both competitors and selects the entire corresponding native trajectory per registered task before any outcomes. It does not splice favorable per-timestep results after observation.

Every trial is retained, including refusals and both injected faults. We separately record official task success, privileged controller target reads, the number and audit-only correctness of confident latent-history assignments, public XYZ reads, native setpoint checks and all injected command masks.

## 4. Main results

All eight physical execution shards and the **independent full-population source auditor** completed successfully. The actual original source execution is [GitHub Actions #37913661619](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37913661619).

| Actual native PhysX policy | Task successes /64 | Counted privileged target reads |
|:--|--:|--:|
| **Full discrete-history public evidence + selective authoritative read (this method)** | **58** | **39** |
| **Strong pre-registered task-dependent route** | **58** | **57** |
| Fixed readback at step four | 58 | 64 |
| Original geometry-triggered read | 46 | 42 |
| Bounded control without reads | 8 | 0 |

The new method and the strong task-gated comparator have **identical paired official task outcomes**: 58 states were successful under both, six failed under both, and neither strategy uniquely won a state. Their source-audited *actual* private read counts were **39 versus 57**, a reduction of 18 (**31.6%**) relative to this strong policy; against always-query, 39 versus 64 is **39.1%** fewer. The data do not show higher task success than the strong comparator, and a 64-state identical success vector is insufficient to establish general statistical noninferiority.

The observer encountered the intended two physical native target holds on **64/64** registered trials and observed four candidate history targets on each. It resolved a unique whole-history candidate in **25/64** cases (zero observed wrong confident identifications); the remaining 39 used one counted authoritative native target read. With fixed prior empirical parameters, the per-task physical observations were:

| Task | Public unique-history cases | New method / task-gated successes | New privileged reads | Task-gated privileged reads |
|:--|--:|--:|--:|--:|
| PullCube (32 states) | 15 | 32 / 32 | 17 | 25 |
| StackCube (32 states) | 10 | 26 / 26 | 22 | 32 |
| **Total (64 states)** | **25** | **58 / 58** | **39** | **57** |

*The above task-specific figures are reconciled from all eight original physical execution shards. For exact original per-trial data and independent auditor, use the source archive linked below.*

### The necessary negative control

Our previous **separately prospectively executed** 32-state task study required the rotation targets of *all competing hypotheses* to agree before permitting a position-only public witness. It produced **zero** confident identification, **24/32** real task successes with **32** privileged reads, compared with **24/32** successes and **26** reads for the strong task-aware comparator. All 32 true double native fault exposures were reached, so this is a genuine negative mechanism result rather than a failed injection campaign ([original 32-state raw evidence](evidence/public_fourhistory_frozen_ppo_original32_780001_790016/)).

A **retrospective, outcome-exposed** diagnostic of those old 32 original motion trajectories revealed 12 unique complete-history indexes with no observed false labels, but **no improved controller was actually executed on that old population**. The new 64-state trial was frozen afterward, on different new seeds, before implementing and executing the improved full-hypothesis admission rule. This preserves the distinction between hypothesis development and prospective task validation.

## 4.1. Separately preregistered 32-state external-facing prospective replication cohort

A second protocol (rather than unregistered extra trials of the first one) froze new PullCube reset states `860001–860016` and StackCube `870001–870016`, prior PPO checkpoint SHA-256 identities, both actual native target-hold faults, the same empirically trained public-XYZ residual envelope and 2mm competing-hypothesis clearance, and a complete-hypothesis SO(3) survivor gate *before* the new source task outcomes. The protocol and eight independent four-state physical source jobs are [#37914343195](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37914343195). Its **32/32 double-fault exposures**, **256 actually independently stepped native PhysX controller worlds**, and independent full-denominator audit are GREEN. The complete unchanged original file archive is [survivor_fullpose_original32_860001_870016](evidence/survivor_fullpose_original32_860001_870016/).

| Replication cohort, preregistered rule | Task success / 32 | Counted authoritative target reads | Public uniquely resolved histories | Incorrect confident histories observed |
|:--|--:|--:|--:|--:|
| Complete full-SE(3) history survivor + query on unresolved | **28** | **22** | **10** | **0** |
| Preselected task-aware opponent, actually executed | **28** | **27** | — | — |
| Fixed at-step-four authoritative read | 28 | 32 | — | — |
| Older generic geometric-selective read | 24 | 18 | — | — |
| Bounded zero-query alternative | 6 | 0 | — | — |

The new adapter and the task-aware comparator have **exactly the same paired success/failure vector**: 28 successes for both, four failures for both, zero exclusive wins. In this second cohort, the information-cost difference is **task dependent**. On PullCube, both succeed **16/16**, but the proposed adapter reads **13** times whereas the task-gated method reads **11**, i.e., the proposed method is **worse by two privileged reads**. On StackCube, both succeed **12/16**, but the new adapter reads **9** versus **16**, saving seven. These counterexamples are not diluted or hidden by the favorable overall count.

The primary 64-state and second 32-state studies used **distinct** reset seeds and related but separately implemented discrete-history authorization code. A descriptive sum across studies is **96 task-reset conditions (768 physically stepped simulator/controller worlds), 86/96 task successes for each task-aware comparator, 61 versus 84 privileged reads, 35 public-history selections and zero observed false confident selections**. This is not a single prospective 96-case pooled method test or 96 independent robots, and the two different model versions must NOT be used to claim a single statistically established population effect. Their separately frozen source results are the primary evidence.

### Statistical accuracy is neither zero-error proof nor population equivalence

The 25/25 correct confidently selected histories in the first study and 10/10 in the second do NOT identify a zero population error rate. Under a hypothetical independent identically distributed Bernoulli trial model **within each studied task mixture**, the exact *one-sided* 95% upper bound for an unobserved wrong-history probability with zero observed errors among `n` confident decisions is `1 - 0.05^(1/n)`: approximately **11.3%** for 25 original confident decisions and **25.9%** for 10. These are **conditional iid sensitivity calculations**, not valid distribution-free certificates when the controller, samples, task or sensor model shifts.

Likewise, zero paired success discordances among 64 and 32 task states does **not** demonstrate noninferiority or equality of future policy success. Under the same hypothetical iid paired-outcome model, the one-sided upper bounds on a *binary discordance event* are approximately **4.57%** (64) and **8.94%** (32). Without IID across controller/task resets, such parametric bounds need not apply; with only two separately released pretrained PPOs, broader task-level generalization remains untested. Neither study quantified real robot network latency, wall-clock query cost, contact force, collision risk or physiological safety.

The [source-only two-cohort reviewer audit](review/verify_two_prospective_history_cohorts.py) refuses altered/missing original JSON hashes, independently recomputes every original seed's native task success and controller target-read count, checks both real native hold interventions on the new arm, and verifies complete-history decisions against the saved source and original individual-study independent audit. Its [adversarial test suite](https://github.com/lindicaphxag-tech/ManiSkill/blob/publication/reviewer-paired96-unbiased-verification-20261009/tests/test_two_prospective_history_cohorts.py) also refuses mutated source records or hidden denominators. **This is an independent re-analysis of the contributor's original data, not independent external laboratory execution.**

## 4.2. Necessary fault-truth falsification and reset-disjoint 64-state reproduction (new in v1.6)

The two all-held PPO cohorts above show that public motion can reduce controller-private reads, but do **not** rule out a cheap controller that blindly assumes every missing-ACK command was held. We therefore ran an additional first-ACK **physically mixed** falsifier, separately sourced in [original 64 mixed-ACK study #37915263314](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37915263314). Its method completed **58/64** official tasks with **31** private target reads, compared with a preselected task-aware route at **58/64, 58 reads** and a genuinely stepped zero-read always-held comparator at **43/64**. The original mixed cohort reused **32 reset identities** previously used in the separate 32-state full-pose study, so it is not a completely new set of 64 initial states relative to all earlier studies. That overlap is disclosed, not erased.

To repair that identity overlap, the [separately frozen disjoint protocol](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/replicate-mixedack-disjoint64-20261009/research/DISJOINT_MIXED_T2_PPO64_PREOUTCOME_V1.json) precommitted wholly different PullCube seeds `1180001–1180032` and StackCube `1190001–1190032`. The exact same original native simulator runner Git blob `36e672446407435e656cbf8aba6fa2de7c1e9d0e`, original frozen two PPO checkpoints, empirical public-motion classifier and task route were reused. All eight genuine nine-controller-world PhysX shards and the separate all-population auditor passed: [original workflow #37916917436](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37916917436), **64 distinct resets / 576 actually stepped simulator-controller worlds**.

| Cohort: independently reset, fixed first-ACK mixed truth, second ACK physically held | Proposed official task successes | Task-aware strong task successes | Proposed private target reads | Strong private target reads | Public unique full-history selections / wrong confident |
|:--|--:|--:|--:|--:|--:|
| PullCube 32 | **32** | 31 | **11** | 20 | 21 / 0 |
| StackCube 32 | 25 | 25 | **22** | 32 | 10 / 0 |
| **All 64 (same treatment; same frozen checkpoint per task)** | **57** | **56** | **33** | **52** | **31 / 0** |

The actual paired task result is **56 both succeed, seven both fail, one new-only succeeds, zero task-aware-only succeeds**; the fixed mandatory-read comparator obtained **57/64 tasks with 64** target reads. The method saves **19/52 = 36.5%** controller-private reads against the strong route and preserves its official task successes on this particular source cohort. We do **not** claim significant task-success superiority, formally established noninferiority, independent lab reproducibility or zero future wrong-history risk. Even under a hypothetical within-cohort iid model, zero errors among 31 confident histories implies a one-sided 95% binomial upper risk of about 9.2%, not zero. The two achieved-XYZ observations per public-method trial, public-model computation, physical actuation and audit-only private getters are **different resources** from decision-time private readbacks.

**The crucial remaining generalization gap:** in both physically mixed datasets the **second** command was always physically held as a known neutral motion probe. The latent belief may contain four candidate target histories, but actual delivered-command truth covers only `(APPLIED, HELD)` and `(HELD, HELD)`. We have not tested independently physically executed `(HELD, APPLIED)` or `(APPLIED, APPLIED)`, nor an external competing active probe with a matched sensing/actuation budget. Proper 2×2 truth testing requires a **separate, known delivered neutral probe step** offered to every comparator, recalibration or conservative abstention when the frozen envelope fails, and independent unseen reset IDs. See [falsifier and source-integrity report](DISJOINT_MIXED_ACK_PPO64_SOURCE_RESULT_20261009.md) for the archived original result, incomplete permanent Git tracking and explicit next decision gates.

## 4.3. Decisive prospective falsifier: both uncertain commands physically execute or not

The disjoint mixed-first-ACK study above still held its second command in every episode. We therefore froze a strictly new [two-unknown-ACK physical-truth protocol](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/true-twoack-2x2-new64-20261009/research/TWO_UNKNOWN_ACK_TRUE_2X2_PPO64_PREOUTCOME_V1.json) before original `PullCube-v1` resets `1280001–1280032` and `StackCube-v1` resets `1290001–1290032` were executed. Both physical command actions at zero-indexed steps two and three were independently set to native **APPLIED** or **HELD**, balancing the four ground-truth combinations on **eight different resets per task per combination**. The adapter was not exposed to the chosen truth bits. Candidate controller targets still included full XYZ and SO(3) orientation, with an empirical public XYZ response envelope and threshold frozen from previous research, rather than from the new trials.

Unlike the previous frozen experiment, a separate, **known-delivered neutral target-delta step at step four** was given to all faulted controls *that remained active*. The public method measured achieved XYZ before and after this step and made a whole-history decision; unresolved histories caused one counted authoritative controller-target read at step five. The fixed-read comparator also read at step five, and its interim step-three command was explicitly computed from **public achieved pose** instead of a private, invalidated controller-memory cache. The original first run [#37919161678](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37919161678) aborted when that cache was incorrectly accessed; **no complete original shard outcome existed**. A [recorded implementation-only amendment](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/true-twoack-2x2-new64-20261009/research/TWOACK_2X2_IMPLEMENTATION_AMENDMENT_BEFORE_RESULTS.md) fixed the information boundary before the fully successful corrected physical run. This change must be disclosed in any preregistration-fidelity review; the repaired comparator cannot be represented as byte-identical to the failed first implementation.

The corrected [authentic 64×9 native PhysX source run and full independent population audit #37919576643](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37919576643) passed all ten jobs. All 64 episodes exposed the **two actual unknown-ACK fault interventions** on the proposed arm, and nine separate native controller worlds were stepped per reset: **576 worlds total**, not 576 independent trained models. There was no PPO retraining or recalibration of the pre-existing public history classifier. Original all-state per-arm audit and trial-level results, including unsuccessful trials and SHA256SUMS, are retained in the [permanent original evidence directory](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/true-twoack-2x2-new64-20261009/research/frozen_policy_transfer/evidence/true_twoack_2x2_original64_1280001_1290032).

| Physically executed comparison, same 64 reset seeds | Official task successes | Privileged controller-target reads |
|:--|--:|--:|
| Complete history public evidence, unresolved → authoritative read | **55/64** | **50** |
| Frozen task-selected strong comparator | **56/64** | **59** |
| Fixed step-five controller target read | **57/64** | **64** |
| Never query, always assume command was held | **35/64** | **0** |

Paired new-versus-strong successes: **54 both, seven neither, one new-only, two strong-only**. Fourteen cases gave a unique full-history classification with **zero incorrect confident histories observed**, and the other fifty used an explicit private read. Private target reads decreased by **9/59 (15.3%)** versus the strong task-route, but **one fewer task completed**; they decreased by 14/64 (21.9%) versus fixed readback, but **two fewer tasks completed**. None of these finite observations establishes population noninferiority, zero error, or a favorable wall-clock/energy cost because public sensing and an extra physical probe step have costs.

The exact original **four executed truth combinations, not merely four latent histories**, expose heterogeneous task failures:

| True first / second command | PullCube: method / strong (N=8) | StackCube: method / strong (N=8) |
|:--|:--:|:--:|
| HELD / HELD | 8 / 8 | 6 / 7 |
| APPLIED / HELD | 8 / 7 | 4 / 4 |
| HELD / APPLIED | 8 / 8 | 7 / 7 |
| APPLIED / APPLIED | 7 / 7 | 7 / 8 |

The *StackCube APPLIED/APPLIED* and *StackCube HELD/HELD* strata each contain a strong-control-only task success. It is precisely the active second-command condition that the earlier all-held-second protocol could not investigate. Under broader two-ACK physical truth the method's public-only resolved histories decreased from 31/64 to 14/64 (relative to the earlier different 64-reset study), while its task-level advantage over the strong comparison vanished. **These different reset populations and physical fault generators are descriptive, not a paired estimate of the causal effect of the second ACK.** Within each of the eight task × truth groups, each method was physically paired at the same reset ID; the four truth groups themselves used different initial seeds.

### Explicit early-stop and observation-budget asymmetry

The strict exact-common-action zero-read negative control refused before step four on **64/64 trials** and therefore did **not** receive the shared neutral step. **Every other seven faulted control arm, including the proposed, task-selected strong, fixed read and always-held alternatives, received the one delivered neutral motion step at all 64 resets.** The all-control source audit correctly sets `equal_probe_per_full_source_population=false` because one early-refusing arm did not reach the probe. This does not mean the strong comparator was denied the probe; it means **equal opportunity was achieved only among the continuing primary and other seven faulted comparators**. The early refusal is preserved as failure rather than silently inserting an additional simulation step. The public method uses two ordinary achieved XYZ samples per reached episode. Its reduction is **decision-time privileged target reads**, not total observed information, control time, computation, or actuated probe budget.

This 2×2 study establishes a more informative **failure boundary** than a selectively favorable read-count comparison: a known-controller-chart whole-history observer can have lower private information consumption and still lose task completions as its empirical motion model becomes less discriminative. To claim reliable performance gains, future work must beat a *genuinely equal-private-read-budget* active information-seeking comparator, test all four physical execution patterns on each identical reset (rather than seed-stratifying them), verify realistic delay/contact shifts, and demonstrate task success with a task-specific action-correct VLA. These experiments are currently **uncompleted** and may provide further falsification.

## 4.4. Prospective matched physical prefixes: isolate the pre-query action confound (new in v1.8)

### Why a seemingly stronger four-truth comparison was not yet a query-only causal test

In the preceding [original four-truth 64 PhysX study](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37919576643), the new public and mandatory-read arms both experienced the same truth schedule and neutral probe, but the second command **actually dispatched** by each arm differed when the t3 action was physically applied. For example, before any step-five authoritative read, their t3 normalized 6D commands differed substantially on previously exposed PullCube and StackCube trials. Thus **55/64 vs 57/64** in that study mixes *information decisions* with *different earlier physical state trajectories*. It cannot be attributed exclusively to the public observer being worse at state identification. This is a discovered confound, not a retrospective excuse for the observed negative outcomes.

To control this threat, a [new experiment was registered before subsequent seeds were executed](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/matched-prefix-twoack-new64-20261009/research/MATCHED_PREFIX_TWOACK_FROZEN_PPO64_PREOUTCOME_V1.json), selecting **64 entirely new task-reset identities**: PullCube `1380001–1380032`, StackCube `1390001–1390032`. The same two released pretrained PPO SHA-256 identities, source/target native action charts, motion-model epsilon and 2 mm competitor clearance, 50-step horizon, and first/two missing-ACK truth schedule remained unchanged.

The public branch's **actual normalized dispatched** t2 and t3 arm commands were made identical to those of the fixed-read comparator, both under true APPLIED and under physically held actions. Both received a **known-delivered zero-delta t4 neutral probe** before their t5 private-read decision. At t4, an **audit-only** controller target getter verified, without entering either decision branch, that both real native worlds matched in the applied 6D commands **and** in achieved/commanded SE(3) poses within precommitted 5e-5 numerical tolerance. Any violation invalidated the cohort. This is an important strengthening over comparing equal reset seeds while permitting physically different earlier motor commands.

**This does not make the comparison a perfect same-code information-only randomized experiment.** The post-t5 public belief and always-read controller use related but distinct observer implementation paths. Their action compilers and physics may diverge downstream even when public history identification agrees with the private target. In addition, the public method consumes two achieved-XYZ observation events; the primary efficiency metric remains *privileged target reads*, not total sensing, CPU time, physical effort or hardware safety.

### Audited original 64-reset evidence

All eight actual nine-controller-world PhysX shards ran successfully at the fixed source head; the first all-64 auditor failed **only from an incorrectly substituted Python module import name**, after all physical executions and per-shard audits had completed. The [separate original-data-only audit and permanent archive](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37922389404) then fixed the import path and rechecked the **same original 16 PhysX source JSONs**, without retraining, altering thresholds or repeating physics. Its full independent denominator/physical-prefix verification passed. This distinction is recorded, not suppressed.

| New frozen 64-reset actual native PhysX study | Official task success | Decision-time private commanded-target reads |
|:--|--:|--:|
| **Public complete SE(3) history, read only if ambiguous (new)** | **56/64** | **43** |
| **Fixed late authoritative target read, physically matched prefix** | **55/64** | **63** |
| Original task-preselected comparator (Pull: geometric-selective; Stack: fixed read) | 55/64 | 58 |
| Zero-private-read always-assume-held | 39/64 | 0 |

Against the physically prefix-matched fixed read, the public observer saved **20/63 = 31.7%** actual *privileged* reads; one early-completed original trial needed no fixed read and remains in the denominator. Against the task-gated route it saved **15/58 = 25.9%** reads, but that comparator was not forced to share the same earlier 6D actions for every task and is not the isolated causal reference. The paired task outcomes versus both fixed and strong comparison were **55 both successful, eight neither, one public-only success, zero comparator-only successes**. That exclusive success came from **StackCube reset 1390002**, true t2=APPLIED, t3=HELD. It is not evidence of a statistically meaningful success-rate improvement; exact paired discordance is dominated by one case.

| Original reset task | Public method successful | Matched fixed-read successful | Public private reads | Matched fixed reads | Public unique whole-history labels / observed wrong |
|:--|--:|--:|--:|--:|--:|
| PullCube (32 new reset IDs) | 32 | 32 | 20 | 31 | 12 / 0 |
| StackCube (32 new reset IDs) | 24 | 23 | 23 | 32 | 9 / 0 |
| **Total 64** | **56** | **55** | **43** | **63** | **21 / 0** |

The experimental rollout contains **576 actually independently stepped native simulator/controller worlds** on 64 distinct initial reset states, with a balanced four-case native executed/held truth schedule across resets **within each task**. The public branch experienced both intended fault opportunities on all 64 resets. The 64 public-versus-fixed physical prefixes passed exact original-data checks. The strict-common-action refusal baseline terminated before the common probe in registered cases; claiming all nine methods received identical neutral steps would be false. Each other surviving faulted comparator received the original physical probe according to its rollout.

### Risk, interpretation and remaining falsification

No observed confidently wrong labels occurred among 21 unique public history decisions; this is an *empirical count*, not a guaranteed error bound. Under an illustrative iid binomial model, even 0/21 erroneous decisions have a one-sided 95% upper error-rate bound of approximately **13.3%**, and robot-task or fault-domain shifts need not satisfy that iid assumption. Zero confident wrong histories also **does not** guarantee unchanged task outcome: after t5, any differences in native inverse pose encoding, bounded projection, policy observation, contact dynamics or numerical rounding may alter the future trajectory. The one public-only win in a single new reset state is a hypothesis-generating observation, not a theorem or general performance advantage.

The new evidence supports **reducing private target-state queries in a controlled two-ACK native fault population**, with a substantially fairer pre-query physics comparison. Before any high-stakes deployment, or a defensible state-of-the-art robotics method claim, an independent outside-lab physical rerun, an independently mixed four-truth experiment on each *same* reset identity, a post-query identical-action-compiler control, task-matched action-interface models beyond two Panda PPOs, and a matched-public-observation/action-cost Active-Probing comparator remain necessary. This study is **not** a VLA task success, real packet-loss experiment or physical safety certificate.

**Immutable verification links:** [original registered experiment and initially failed full-audit workflow #37921574816](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37921574816); [corrected full original-data-only audit and permanent 19-file raw SHA256 archive #37922389404](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37922389404); [permanent source original JSONs, per-shard audits, full independent auditor, digest manifest](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/matched-prefix-audit-original64-20261009/research/frozen_policy_transfer/evidence/matched_prefix_twoack_original64_1380001_1390032).


## 4.5. Prospective shared post-query compiler: removing the remaining implementation confound (new in v1.9)

### Pre-outcome causal contract and genuine physically matched source

The prior matched-prefix study in §4.4 established equality of native fault-step arm commands and target/achieved poses **before** the information decision, but retained a material *post-decision implementation difference*: its public method continued through `UncertainDeliveryBelief`, whereas the fixed-read comparator used `ActionHistoryObserver`. Different reference-state bookkeeping, ACK update paths, and their interactions with the inverse native action compiler could therefore affect subsequent task outcomes. An information-only interpretation remained stronger than the code justified.

The new [before-outcome protocol](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/shared-compiler-twoack-prospective64-20261009/research/SHARED_COMPILER_TWOACK_FROZEN_PPO64_PREOUTCOME_V1.json) (Git blob `b57973e28897c40125069fb0205e83b1c46d1885`) froze a **third distinct** population of 64 reset states: PullCube `1480001–1480032` and StackCube `1490001–1490032`. It preserved both published source PPO checkpoints, their original SHA256 identities, the known achieved-relative to target-relative native action chart, the original externally calibrated motion tolerances and the 2-mm competitor margin, the original 50-step horizon and the physically dispatched two-ACK fault schedule. Each task has eight seeds in each t2/t3 execution state: HELD/HELD, APPLIED/HELD, HELD/APPLIED and APPLIED/APPLIED. The execution schedule is available to the physical *auditor*, never to the experimental adapter.

Each registered seed instantiates **nine independently stepped native ManiSkill CPU PhysX policy/controller worlds**. The proposed and mandatory-read comparator physically dispatch the same actual native six-axis actions under both unknown-ACK events (including both zero holds and nonzero executed actions), then both dispatch a known-delivered zero-delta t4 arm command. Immediately before information acquisition at t5, the audit-only native target getter and achieved end-effector pose must match between these two worlds within predeclared \(5\times10^{-5}\) translation and rotation tolerances, or the paired experiment is rejected. The frozen policy observation excludes the private target field. Neither public decision uses the physical execution truth or the audit-only private read as a hidden input.

**Post-t5 both comparators use the exact same `UncertainDeliveryBelief` state container, the same `base.normalized_target_delta(..., approximate=True, old_override=single_hypothesis)` native compiler, and the same `prepare/acknowledge` state update.** The treatment is the information source at t5. The proposed method uses the unique compatible *whole* six-dimensional history when the fixed empirical public-motion rule accepts it, otherwise it makes one counted private target read; the mandatory-read control always makes one counted private read before invoking the shared compiler. Per-step source-policy seven-dimensional proposals, selected belief target pose, compiled native six-dimensional commands and cumulative private reads are recorded. The [independent 64-case source auditor](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/shared-compiler-twoack-prospective64-20261009/research/audit_shared_compiler_twoack_new64.py) requires the same post-query compiler schema in all original traces.

The two methods are **not required to dispatch identical actions after t5**: different legitimate information can change which source policy observation and target-history reference they encounter, and hence their actions and future contact states. The methodological improvement is that differences can no longer be attributed to *different source-code compiler/state-container implementations*. This is an implementation-controlled information intervention, not a proof that all remaining downstream physics are identical.

### Original physical rollout, disclosed execution failures and permanent independent re-audit

The first pinned pilot [#37924300007](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924300007) correctly **failed** its dynamic post-query guard: the mandatory-read branch cached `maybe_two` *before* the authoritative t5 resynchronization collapsed its candidate set. A source-only correction moved the cardinality calculation after resynchronization; it did not alter registered seeds, checkpoint weights, thresholds or endpoints. The error and code change are described in the [permanent failure disclosure](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/shared-compiler-twoack-prospective64-20261009/research/SHARED_COMPILER_PROSPECTIVE_FAILURE_DISCLOSURE_20261009.md). A separate rerun [#37924949613](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924949613) failed **before physics** because its top-level replay workflow was still checking the old source SHA. Neither failed attempt enters the successful source population, and neither is misreported as a performance-negative trial.

The corrected program used source blob `89248363b5bc52c0568495f3f78efc58d9a1ac67`, executed from frozen exact Git commit `12b0156be54222e4a3ecf573898ab337c046426e`. [Main fixed-source physical run #37925044658](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37925044658) completed all eight real native PhysX shards and its original all-64 audit. A [separate source-only re-audit and archival run #37925642641](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37925642641) independently recomputed the complete 64-state audit over the same **16 byte-identical original per-shard raw/audit JSONs**, compared its output byte-for-byte with the original completed-run audit, and permanently archived 19 files including a SHA256 digest manifest. The archive is [publicly inspectable](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/shared-compiler-evidence-original64-20261009/research/frozen_policy_transfer/evidence/shared_compiler_twoack_original64_1480001_1490032). Source-audit independence here means an independently rerun verification program; the physical execution remains author-controlled and **is not independent investigator replication**.

### Entire original denominator, task pairing and private information cost

| Same preregistered 64 task resets, actual native PhysX | Official task success | Privileged target reads | Unique complete public histories / observed wrong |
|:--|--:|--:|--:|
| **Public whole-history evidence, fixed-rule admission, private read on ambiguity** | **53/64** | **48** | **16 / 0** |
| **Mandatory native target read using the *same post-t5 compiler*** | **53/64** | **64** | Not applicable |
| Previously selected task-gated strong route | 50/64 | 60 | Not applicable |
| Assumed HELD at both unknown ACKs, no read | 33/64 | 0 | Not applicable |

The strongest isolated comparator here is the **matched-physics, common-code mandatory-read** method, not the stronger task-conditional route from earlier studies that may use different physical prefixes. The public arm saved exactly **16/64 = 25% of the actually charged privileged native target reads**, not 25% of elapsed time, compute, total information or actuated physical actions. The public method additionally consumes **two public achieved-XYZ motion samples**, and both primary methods experience the neutral t4 control opportunity.

The original per-seed audit establishes a stronger pairing fact than equal aggregate success rates: **53 both-success, 11 both-failure, zero public-only success and zero fixed-read-only success**. This is an exact same-seed task-outcome vector over the 64 original states, and thus success did not diverge *in these tested cases*. It is not a hypothesis-test-derived population noninferiority certificate.

| Entire new task-reset population | Public success /32 | Common-code fixed success /32 | Public private reads | Fixed private reads | Public complete histories / observed wrong |
|:--|--:|--:|--:|--:|--:|
| PullCube (32) | 31 | 31 | 21 | 32 | 11 / 0 |
| StackCube (32) | 22 | 22 | 27 | 32 | 5 / 0 |
| **Total (64)** | **53** | **53** | **48** | **64** | **16 / 0** |

All 64 public arms experienced their two registered fault opportunities, the four applied/held truth groups were balanced in each task, all audited paired physical prefixes passed, and every original source and per-shard statistic was retained. The exact-action-refusing negative comparator terminates before the neutral probe in the full population, so **all nine arms having received the same probe is false**. The shared probe claim applies to the matched public/fixed core pair and the other continuing arms, not to the early-refusing comparator.

### Identifiability is conditional: a direct falsification across an independent seed cohort

For a finite candidate target-history set \(H\), let \(Y_h\) denote the set of feasible public achieved motions under a *valid* response uncertainty envelope for history \(h\). If \(Y_i\cap Y_j\neq\varnothing\) for histories with different targets, an observation in the intersection cannot identify the target from public motion alone; any always-deciding deterministic classifier must be incorrect for at least one of the two possible histories. Conversely, a unique compatible history is identified **only if the candidate set is complete and the envelope truly covers actual physics**. This is standard set-membership logic, not a newly proven robotics theorem or a blanket identifiability guarantee.

Our numerical residual tolerance and 2-mm margin are *empirically fixed heuristics*, not a certified conservative physical observation envelope. A **different** prospective matched-public Bayesian study on its [own 64 authentic native PhysX resets](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924192162) yielded **52/64 successes, 48 reads, 16 public history admissions and one audit-confirmed confidently wrong public history** for the residual-based rule. A more conservative posterior comparator from that study yielded 52/64, 63 reads and zero observed wrong, illustrating a real selectivity–risk trade-off rather than proving that conservative Bayesian inference always wins. Its samples are **not merged into** the present 64-state causal test.

Even zero observed wrong labels among the present 16 public admissions permits a considerable unseen error rate; with an illustrative iid Bernoulli model the one-sided exact 95% upper misidentification probability is \(1-0.05^{1/16}\approx17.1\%\). No independence or stationarity assumption has been established across robot contact and fault strata, so this numerical bound must **not** be presented as a deployment safety guarantee. The wrong-admission case in a different run directly falsifies any universal zero-risk assertion.

### Remaining scope: why this is a more credible representative result, not yet a top-tier acceptance

The present experiment removes an avoidable software-implementation confound and demonstrates a complete same-seed information/read-versus-task success comparison under two physically applied/held ACK events. It does **not** establish lower wall-clock intervention cost, greater task success, formal margin-specified noninferiority, hardware contact safety, true packet loss, generalization across unrelated controllers, a successful VLA rollout, an executed equal-budget ActionShift-style active-probing challenger, or any independent external laboratory adoption. The same Panda native chart and two PPO task settings still dominate the evidence.

The next decisive independent falsifier is an investigator-operated checkout with investigator-selected reset and fault distributions and original audit-trace publication; second is a distinct controller family or a separately verified task-competent VLA policy; third is an active-observation competitor charged for the same public sensors, probe actuations and private reads. Merely merging this manuscript into the author's own GitHub repository provides **none** of those external endorsements.

## 5. Limitations and comparison with related methods

Our geometrical observation-set test draws on standard set-membership reasoning. Existing [ActionShift](https://github.com/Archerkattri/actionshift) and [ActionABI](https://github.com/Archerkattri/actionabi) studies already investigate action-interface identification, belief updates, active probes and abstention; this work does not claim to invent those broad concepts. The narrower empirical target is an **otherwise known action ABI with missing execution truth**, in which the prior commanded target is a state variable distinct from observed achieved pose.

All positive and negative experiments are **author-operated within ManiSkill CPU PhysX**, mostly on the same Panda robot and two released PPO policies. The public-response tolerances are prior empirical samples, not a certified deterministic world-model envelope. Our environment deliberately masks arm commands at known steps; it does not simulate real network transport, arbitrary interrupted execution, delayed bursts, contact-force safety or robot hardware. The new method receives additional public achieved XYZ samples, so the cost comparison is explicitly about **privileged hidden target reads**, not total system information or exact wall-clock computation. Full SE(3) proprioceptive models, contact-dependent disturbances, task-general active-query opponents and genuinely independent laboratory/fork re-executions remain unproven.

In particular, 25 correct observed history labels are not proof that the probability of a wrong confident assignment is zero on new systems, and zero paired discordances on 64 trials are not proof of task noninferiority under an arbitrary population shift. A strong ActionShift-style alternative given the same public motion samples, actuation opportunities and query cost must be executed before making any state-of-the-art comparison claim.

## 6. Reproduction, negative evidence and external reviewer challenge

**Highest-quality causal evidence (v1.9):** [registered shared-compiler protocol](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/shared-compiler-twoack-prospective64-20261009/research/SHARED_COMPILER_TWOACK_FROZEN_PPO64_PREOUTCOME_V1.json); [SHA-pinned genuine 576-PhysX-world rollout and all64 original auditor](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37925044658); [separate unchanged-original source archive verifier](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37925642641); [permanent 19-file source audit and SHA256 manifest](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/shared-compiler-evidence-original64-20261009/research/frozen_policy_transfer/evidence/shared_compiler_twoack_original64_1480001_1490032); [first failed dynamic-guard run](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924300007) and [disclosure](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/shared-compiler-twoack-prospective64-20261009/research/SHARED_COMPILER_PROSPECTIVE_FAILURE_DISCLOSURE_20261009.md); [different 64-state observed wrong public admission](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924192162).



- **Full new64 source-frozen actual physical experiment and 10-job independent audit:** https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37913661619
- **Original source/data archive (17 original PhysX JSON and SHA256SUMS, when automated archival is complete):** [full new64 original source evidence](evidence/discrete_hypothesis_ppo_original64_840001_850032/)
- **Fresh-run original protocol and physical controller source:** [PPO_DISCRETE_HYPOTHESIS_NEW64_PREOUTCOME_V2.json](../PPO_DISCRETE_HYPOTHESIS_NEW64_PREOUTCOME_V2.json), [frozen_ppo_discrete_history_v2_physx.py](../frozen_ppo_discrete_history_v2_physx.py), [independent source auditor](../audit_public_discrete_hypothesis_new64.py).
- **Earlier correctly preserved negative experiment:** [original new32 source](evidence/public_fourhistory_frozen_ppo_original32_780001_790016/), [registered initial 32-state experiment](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37912591209), [reproducible retrospective pilot (NOT PhysX intervention)](../audit_development_old32_full_history_index.py).
- **External researcher-owned fork entry:** [independent eight-reset PhysX workflow](../../.github/workflows/outside-discrete-history-v2-physx.yml) and [source-locked runner](../outside_discrete_history_v2_replication.py). This workflow being available is **not** an external laboratory replication.

**Current conclusion (v1.9).** Under frozen source policies, a known stateful target-relative native controller chart, and an executed two-ACK fault population, a finite set of complete target-history hypotheses can sometimes be disambiguated using ordinary public end-effector motion. The new prospective **common-code, physically matched-prefix** 64-reset evidence records **53/64 paired identical task outcomes using 48 versus 64 charged privileged target reads** (25% reduction), with 16 accepted public histories and no observed error *in that cohort*. A different fresh 64-state cohort independently recorded one confidently wrong public identification; the empirical gate is therefore not a certified authority to command. This is defensible evidence for a selective information mechanism and an auditable failure boundary, not a safety result, general statistical noninferiority, VLA success, novel set-membership theorem, external laboratory reproduction, peer-review acceptance or official upstream adoption.

*Do not call this result an accepted top-tier paper, independent outside validation, a new set-membership theorem or hardware safety certificate.*

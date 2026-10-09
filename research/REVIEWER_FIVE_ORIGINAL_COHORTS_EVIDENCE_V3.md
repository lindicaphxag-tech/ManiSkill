# Reviewer-Grade Original Evidence: Five Disjoint Native PhysX Cohorts

**Source audit:** [pure-stdlib, frozen original Git blobs, exact paired statistics](reviewer_independent_original_5cohort_stats.py) · [passed GitHub Actions Python 3.11 and 3.13](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37931401502).

**Important scientific status:** these are five SEPARATE, internally source-matched, preregistered author-run physically stepped simulator cohorts, 64 task initial states each. **Do not pool the 320 original states as 320 independent demonstrations of one method's effect.** Studies differ in true execution-ACK distribution, probe actuation/timing, physical dynamics, and source/controller settings. The original full data are retained, including failed tasks and adverse latent-state predictions. No third-party reproduction, hardware experiment, actual network-packet loss, confirmed novelty priority, or paper acceptance.

## Actual on-seed paired original PhysX results

| Prospective study, and which method is PRIMARY | PRIMARY official task successes | Matched SECONDARY task successes | PRIMARY reads | SECONDARY reads | PRIMARY public-authorized complete histories | PRIMARY truly wrong confident histories |
|---|---:|---:|---:|---:|---:|---:|
| First mixed ACK, second HELD: public observer vs task-ID strong query | 58/64 | 58/64 | **31** | 58 | 33 | 0 |
| Both ACK steps genuinely mixed: public observer vs task-ID strong query | 58/64 | 57/64 | **46** | 62 | 18 | **2** |
| Extra t4/t5 neutral actuation: double public observation vs single | 48/64 | 48/64 | 43 | **41** | 21 | 0 |
| Prior 32 real true-target residual calibration per task: wider response envelope vs original narrow | 58/64 | 58/64 | 53 | **51** | 11 | 0 |
| True physically changed Panda joint drive gains: t1 known-target-anchor filter vs original narrow t4 public witness | 56/64 | 56/64 | 62 | **56** | 2 | 0 |

All data are **actual independently stepped within-cohort true PhysX policy worlds**, not task labels spliced from old rollouts. Each study's exact source hashes, matched task discrepancies and other uncertainty measures are recomputed from its original bytestream by the auditor. The double-ACK source producer failed only an early-refusal auditor condition; the 8 original physical job artifacts were subsequently independently source-audited, with the failed producer status explicitly retained. The OOD producer's 8 real job artifacts passed but its aggregated source-only CI initially lacked NumPy; source-only re-audit succeeded without simulation reruns.

## Paired binary success, not merely total score coincidence

| Study | Both methods complete task | PRIMARY only | SECONDARY only | Neither | Task-level interpretation |
|---|---:|---:|---:|---:|---|
| First mixed/held | 57 | 1 | 1 | 5 | Equal aggregate task counts do NOT establish statistical noninferiority |
| Both ACK mixed | 56 | 2 | 1 | 5 | Only three discordant trajectories; no robust task-success gain |
| Two motion observations | 48 | 0 | 0 | 16 | Both physical policies produced the same binary outcome on each reset |
| Wider prior-residual model | 58 | 0 | 0 | 6 | Identical task vector, more private reads |
| t1 anchor under true changed PD drives | 56 | 0 | 0 | 8 | Identical task vector, more private reads and observations |

Absolute native getter savings are not a task success test. Within the FIRST cohort the public method saved private reads on **30** paired resets, the strong control saved on **3** and they tied on **31**. Its exploratory exact two-sided sign p is **1.401×10⁻⁶**. In the BOTH ACK-truth cohort the public method saved on **17**, lost on **1**, tied on **46** (exploratory p **1.45×10⁻⁴**). Neither should be described as a preregistered familywise-confirmatory p-value or as arising from 64 independent task/policy/dynamics systems.

## False authorization is an extremely low-count endpoint

For a binomial model **only under independent identically sampled accepted decisions**, the one-sided exact 95% Clopper–Pearson UPPER limit is reported *conditional on the public model authorizing a native history*, not misleadingly over all 64 resets.

| Original actual confident wrong / uniquely authorized | Observed error | One-sided 95% conditional upper bound (IID only) |
|---|---:|---:|
| First mixed/held: **0/33** | 0% | **8.68%** |
| Both ACK truths mixed: **2/18** | 11.11% | **31.03%** |
| Double correlated probe: **0/21** | 0% | **13.29%** |
| Single correlated probe control: **0/23** | 0% | **12.21%** |
| Wider prior residual envelope: **0/11** | 0% | **23.84%** |
| Narrow residual control: **0/13** | 0% | **20.58%** |
| Dynamics OOD pre-fault t1 anchor: **0/2** | 0% | **77.64%** |
| Dynamics OOD original t4 narrow witness: **0/8** | 0% | **31.23%** |

These bounds are **not robot hardware safety probabilities**. Time-correlated actions, multiple hypotheses, task-conditioned acceptance and changes in physical gain/contact can invalidate the binomial model. They DO show that declaring **zero failures = certified safety** is grossly unwarranted.

## More revealing endpoint: Does the correct controller history FIT the model?

There are at least THREE scientifically different observables:

1. **True-response model coverage:** after actually stepping the native PhysX controller, *audit-only* privileged actual target identifies the true complete native target-history candidate; was its public response residual below the model's predeclared epsilon? This label must **never** be read by the public decision-time algorithm.
2. **Wrong confident authorization:** did the public algorithm pick a unique **incorrect** complete native target history? This requires true-model miscoverage under the complete-candidate assumption but is a strictly smaller event than general model miscoverage.
3. **Official frozen PPO manipulation task success:** did the independently physical task succeed? A wrongly identified history can coincidentally still reach the task goal.

Original true residual analysis shows **12/64 response-model misses** for the original narrow model in the prior true-residual calibration experiment, reduced to **6/64** using the training-source broader margin, without any recorded wrong confident selections in EITHER arm and without real task-success improvement. In the physically changed Panda drive study the original old envelope missed **8/64** physically realized true histories, even though no wrong confident unique target prediction occurred. A pre-fault known-target physical-response anchor correctly warned on only **4/8** of those eventual invalid histories while incorrectly warning on **30/56** physically valid histories. These results support a failure-mechanism distinction, **not** a working reliable causal validity classifier.

## Unavoidable comparison and novelty objections from actual prior literature

[ActionShift](https://github.com/Archerkattri/actionshift) already includes frozen policies, a structured latent action interface, active bounded probes, and multi-method privilege-aware baselines. [FAIL-Detect (RSS 2025)](https://roboticsproceedings.org/rss21/p073.html) already uses sequential OOD detection and conformal uncertainty in robot policy failure monitoring. [When to Act, Ask, or Learn (RSS 2026)](https://roboticsproceedings.org/rss22/p142.html) already calibrates act/ask/learn choices; [SPI-Active (CoRL 2025)](https://proceedings.mlr.press/v305/sobanbabu25a.html) already targets informative dynamic identification with physical task benefits. Consequently **belief, conformal abstention, system identification and probing are NOT our new concepts**. The potentially distinctive task is native controller *realized execution-history uncertainty* under a known action ABI and **the measurable risk of public response model miscoverage producing unsafe belief authorization**, not a general-POMDP priority claim.

The reported old t4 **zero-native-command** was a real additional PhysX advancement and may allow passive physical relaxation; **it is not an optimized actively selected nonzero identification probe**. The separate [32-real-state nonzero t4 action pilot preregistration](CAUSAL_NONZERO_NATIVE_PROBE_PILOT32_PREOUTCOME_V1.json) expressly distinguishes those interventions and charges real native displacement, public XYZ and task costs. New pilot outcomes MUST be reported independently only after physical original audit; never promote a cherry-picked pilot as main-conference proof.

## Gate for a publishable high-confidence primary claim

A defensible paper needs a new, truly matched physical post-change intervention that makes **materially more correct native-history identifications or lowers privileged read cost without reducing heldout task utility**, compared with both an equal-actuation and equal-privilege competitor. It must include the achieved XYZ cost, actual extra native step and displacement, and **the active action's effect on native controller target and gripper/contact trajectory**. It also needs at least a second controller/robot family or genuinely different control regime, independent fresh-seed replication by a non-author researcher, and an honest strong ActionShift-style active information baseline. Until those succeed, the safest supported output is a well-evidenced *negative-plus-information-economy* robotics mechanism study, not a top-main-oral/award-level method superiority claim.

**All exact quantities in this table are regenerated directly from five SHA-pinned original source audits in [one reproducibility script](reviewer_independent_original_5cohort_stats.py).** 

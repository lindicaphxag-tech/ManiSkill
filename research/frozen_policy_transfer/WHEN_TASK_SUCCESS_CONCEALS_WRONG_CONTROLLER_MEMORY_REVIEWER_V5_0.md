# When Task Success Conceals Incorrect Controller Memory
## Hidden Execution Truth, False Authority, and Truly Matched Strong-Comparator Frozen-Policy Experiments

*Reviewer manuscript v5.0 · 9 October 2026 · source-audited task-level failure-mechanism study with stronger original controls, OOD falsification, prospective public SO3 feasibility and scientifically failed factorial; NOT peer reviewed, externally reproduced, or hardware-safe.*

**Authorship requires confirmation before submission.** The named frozen PPO checkpoints are third-party published models, not newly trained models.

### Abstract

Uncertain robot-command execution acknowledgements may leave a deployed policy with multiple plausible internal commanded-target histories, even when the native action interface and the policy weights remain unchanged. Public achieved motion can resolve some of these histories without reading the destination controller's private target register. Yet a candidate that uniquely fits an empirical motion model is not necessarily the physically executed history, and binary task success may conceal this error. We report three source-frozen ManiSkill CPU PhysX comparisons using released PullCube/StackCube PPO checkpoints and actually applied or held command faults. A first preregistered, physically prefix-matched 64-reset study found that a complete-history set-membership gate finished **52/64** tasks while reading private target memory **48** times; a deliberately conservative same-public Gaussian-shaped residual score used **63** reads. In one officially *successful* PullCube rollout, the set gate confidently installed a target **67.6 mm and 0.0536 rad** away from the actual controller target, falsifying a zero-error authority interpretation. A subsequent development-selected conjunction with a 0.65 residual-score floor did **not** demonstrate improved correctness on a separate amended 64-reset cohort, and spent **four additional reads**. To test whether the original comparator was simply too weak, we selected a more competitive **0.60 score-only threshold exclusively on the prior development data**, froze it before a new 64-reset task cohort (new seeds 1940001–1940032/1950001–1950032), and physically stepped **640 independent native controller comparison worlds**. All 64 new resets completed both true ACK interventions and exact predecision full-pose prefix matching. The set gate, tuned score-only gate, and fixed target reader each achieved the **same 59/64 official task outcomes**, with respectively **52, 53, and 64** private target reads. No confidently wrong authorization was observed in the new cohort (12 and 11 authorizations); the sample is far too small to infer safety. These results expose a genuine discrepancy between task-level and latent-state correctness and demonstrate that the apparently large read advantage largely disappears against a better-matched, training-selected public-information challenger. The unresolved research question is how to validate the motion model itself, not merely compare hypotheses under an unverified model.

**Keywords:** robot action semantics; latent execution history; controller target memory; physical acknowledgement uncertainty; set-membership inference; model misspecification; task success masking.

### Main scientific scope update: explicit non-equivalence of three outcome types

**Task success \(S\)**, **correct authorized complete native controller history \(H\)** and **the empirical physical-response model being in support \(V\)** are *different endpoints*. A rollout can have \(S=1\) and \(H=0\) simultaneously. A sensor can expose \(H\) correctly while a frozen policy still fails the task. A useful paper must report all three with separate exposure and decision denominators; none implies the others.

**Four sources of evidence are ranked distinctly:** genuine physically stepped task worlds with successful full original-source audit; source-only recomputation of unchanged actual worlds; pilot observations NOT entering action selection; and experimental designs with failed matching gates. A green CI is evidence of successful computation and audit, never automatic task success or outside replication.

## 1. The scientific question

A frozen policy produces native action intention \(a_t=\pi(o_t)\). A destination target-relative robot controller maintains its previous *commanded* target \(M_t\in SE(3)\) separately from the achieved tool pose \(X_t\in SE(3)\). If an intended native command \(u_t\) was physically applied, the controller target becomes \(F(M_t,u_t)\); if not, the target remains \(M_t\). A missing acknowledgement makes the transition choice latent. Two such events can produce up to four complete target-pose histories even with a known, otherwise correct native action chart.

A public observer may see achieved XYZ before and after the destination's known neutral control step, but not the internal target-memory register. Earlier experiments demonstrated that it can save private state reads under both-held and mixed-execution fault distributions. The present study imposes two additional integrity constraints: (i) the observer, the direct-reader and the competing same-public-information algorithm must share exactly the same physical prefix before information decisions; and (ii) the methods' access to achieved XYZ, native probing opportunities and target reads must be reported separately. This isolates information-authority decisions from unequal prior physical actuation.

## 2. Two adaptation mechanisms, three independently stepped controllers

Let \(\mathcal H_t=\{M^{(1)},\ldots,M^{(K)}\}\subset SE(3)\) be all possible complete native controller-target histories following the two actual unacknowledged commands. A candidate's position predicts a possible achieved-XYZ motion segment over unobserved gain \(\alpha\in[0,1]\). Given before-probe \(x\), after-probe \(y\), empirical motion tolerance \(\epsilon_{\mathrm{task}}\) and candidate position \(m_i\), define

\[
r_i = \min_{0\le\alpha\le 1}\|y-[x+\alpha(m_i-x)]\|_2.
\]

The **set-member admission** authorizes one entire candidate pose only if precisely one \(r_i\le\epsilon_{\mathrm{task}}\), and all other candidates satisfy \(r_j>\epsilon_{\mathrm{task}}+0.002\) m. Otherwise it spends exactly one true private target-memory read at the fixed resynchronization step. The full orientation from the surviving native execution history is preserved; there is no coordinatewise recombination of mutually incompatible pose hypotheses.

The **same-public residual-weight competitor** sees the *identical* \(x,y,\{M_i\}\) and historical \(\epsilon_{\mathrm{task}}\). It computes normalized nonnegative scores
\[
w_i=\frac{\exp[-\tfrac12(r_i/\epsilon_{\mathrm{task}})^2]}{\sum_j\exp[-\tfrac12(r_j/\epsilon_{\mathrm{task}})^2]}
\]
and identifies the argmax only when \(w_{\max}\ge0.95\) and its residual does not exceed \(\epsilon_{\mathrm{task}}\); otherwise it makes exactly one private target read. The threshold 0.95 and response scale were preregistered, and have not been changed after inspecting results. **These numbers are probability-shaped heuristic weights, not calibrated Bayesian posteriors.** The competitor is not the official ActionShift DualABI algorithm or a proven optimal same-information strategy.

The **fixed-read competitor** physically performs the same applied/held unknown ACK commands and the same known-delivered neutral control step, but always reads the controller target at the preregistered resume time. Its lack of a public inference decision does not make its physical prefix different.

All methods are actually stepped, never replayed from a stored demonstration. Source-physical audits verify that each relevant controller begins from the same source-policy observation, executes identical actual t2/t3 normalized 6D native commands, and agrees in achieved and privately audited commanded SE(3) immediately before the differing resynchronization decision. The authoritative getter is forbidden in public-history decisions, but used after a real PhysX step for ground-truth *auditing*.

## 3. Earlier source-frozen study: first matched-public information experiment

The main [preregistration Git blob 9c758954…](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/matched-public-bayes-native16-20261009/research/MATCHED_PUBLIC_BAYES_NEW64_PREOUTCOME_V1.json) was committed before executing the new 64-state cohort or viewing the outcome of the earlier 16-state development pilot. The new reset identities are PullCube **1760001–1760032**, StackCube **1770001–1770032**. For each task, all four true t2/t3 applied/held patterns are physically realized eight times. The native action chart, original third-party PPO checkpoints, source empirical motion epsilon and competing score threshold are frozen. All 64 original states launch ten independent physical comparator worlds, for **640 genuine controller simulations**. The statistical unit is 64 task/reset states, not 640 separate robots or learned policies.

The original [10-job real PhysX and independent source auditor succeeded](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924117746). All nine original ZIP hashes, 16 unmodified shard source/audit JSONs, full-source paired results and five-way/greater adversarial evidence checks were independently [reverified in the archival run](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924749286). The [complete original archive](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/matched-public-bayes-native16-20261009/research/frozen_policy_transfer/evidence/matched_same_public_bayes_original64_1760001_1770032) retains all failures, all private read counts, the complete source ledger and deterministic uncertainty calculation.

## 4. First matched-public result: historical false-authority witness

| Actual frozen-PPO controller treatment | Official task success | Privileged target reads | Public XYZ sample events | Confident full histories | Confident wrong |
|:--|--:|--:|--:|--:|--:|
| Complete-history set-member admission | **52/64** | **48** | 128 | 16 | **1** |
| Same-public uncalibrated residual-weight gate | 52/64 | 63 | 128 | 1 | 0 |
| Mandatory private target read | 52/64 | 64 | 0 as an inference input | — | — |

All 64 binary task outcomes match across the three compared methods: **52 tasks jointly succeeded, 12 jointly failed and zero paired success discordances**. The physical probe has been shared; the extra two achieved-XYZ public measurements are counted for both adaptive methods. Against the same-public heuristic, complete-history set membership saves 15 of the competitor's 63 private target reads (**23.8% relative**) with the same public samples and the same 52 official successes. Against fixed readback, it saves 16 of 64 private reads (**25%**), but fixed does not use the extra 128 public decision observations. The private read saving outweighs XYZ acquisition only under a declared read-equivalent unit cost larger than **0.125** per extra XYZ sampling event, before latency and hardware sensing overhead. None of these numbers establishes equal all-sensor resource cost against the fixed reader.

The 64 original resets include 32 PullCube episodes with 31 successes and 32 StackCube episodes with 21 successes under all three methods. PullCube's complete-history method used **21** privileged target reads and authorized 11 histories, with one wrong. StackCube used **27** reads and authorized five histories without an observed wrong. The same-public score admitted zero complete histories on PullCube and one on StackCube. It is **overly conservative on this trial bank** and cannot stand in for a fully tuned or officially implemented active adaptation baseline.

The separately frozen [stratum-preserving 10,000-resample original-source paired analysis](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/matched-public-bayes-native16-20261009/research/frozen_policy_transfer/evidence/matched_same_public_bayes_original64_1760001_1770032/paired_cost_and_uncertainty.json) gives descriptive 95% intervals of **9–21 private reads saved against the same-public score** and **10–22 against fixed readback**. These are source-population resampling intervals, not universal error guarantees, formal method noninferiority or evidence for a higher task-success probability. A zero discordance count has exact two-sided McNemar p=1, which cannot prove equivalence.

## 5. Counterexample: successful manipulation with a false hidden-history authorization

The critical counterexample is **PullCube seed 1760020**, a physically executed **Applied/Applied** double-ACK trial in the original cohort. The set-member method confidently selected candidate history **0**, whereas audit-only actual controller target memory identified candidate **3** as the physically true native target. The wrong selected target differed from the true one by **0.06763037 m in position and 0.05358308 rad in orientation**. Nonetheless the official frozen-PPO task success was **true** for all three comparison treatments.

The target identity error is mechanistically explained by response-model invalidity rather than missing physical fault exposure. Under the frozen tolerance \(\epsilon_{\mathrm{PullCube}}=0.00694426\) m, the wrongly selected candidate generated motion residual **0.00392475 m** and appeared uniquely compatible. The physically true candidate had residual **0.00926964 m**, exceeding both the empirical compatibility tolerance and the nonwinner cutoff of \(\epsilon+0.002\) m. Thus the model *accepted a false history and excluded the true history*, despite the physical command and pre-decision motion being identical to the other methods. The posterior-shaped same-public competitor declined to infer and paid one private read; the fixed reader also read privately. All three still satisfied the task's success flag.

The [byte-frozen original-source 1760020 verifier](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/matched-public-bayes-native16-20261009/research/reviewer_counterexample_task_success_not_state_correctness.py) checks the actual task-success, matched-prefix, target identity mismatch, prior response epsilon and identical public observation without rerunning or editing a simulator trial. Its [independent source-only CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37925148881) succeeded. This falsifies any claim that the empirically calibrated motion compatibility gate certifies zero incorrect target-history authorizations, or that manipulation success implies correct hidden controller-memory inference.

**Why this case matters:** a policy can finish a task after its adapter has already installed a false latent controller target. Task success is a downstream endpoint and does not measure the correctness of the transient control state. A paper reporting only task success would hide this important, source-authenticated failure. The empirical false-authority rate is **1/16 = 6.25% among 16 confident history identifications** in this particular author-operated cohort, not a future-population estimate or hardware safety risk bound.

## 6. Failed refinement: why more motion-model confidence filtering was insufficient

A deeper method must determine when the response model itself is trustworthy. Requiring one residual to be lower than every other predicted residual only compares hypotheses *inside* the assumed motion model; it does not test whether actual physical dynamics lie inside the model. The 1760020 source witness shows that a highly separated but misspecified response can be worse than honest abstention.

A defensible new method would estimate out-of-sample motion-model error on truly disjoint calibration resets, explicitly include this epistemic uncertainty in complete-history admission and issue a private target read whenever model validity is not supported. Candidate approaches include independently calibrated residual tubes with coverage assumptions, public orientation/velocity consistency channels or a genuinely discriminative additional low-risk probe. They have different physical sensor/action costs, and sequential correlated repetitions of one public probe have previously failed to improve this benchmark. None of these proposals is counted as an already verified positive result. New outcome-free pre-registration and independent unseen physical trials are necessary.

This also clarifies why the result is not a general SE(3) identification theorem. If different actual latent histories produce overlapping public observation distributions under unknown dynamics, history identity is not identifiable from those public samples alone. To claim safety, one must either add a validated sensor/assumption or abstain and query the private state.

## 7. Stronger same-information opponent: truly prospective physical validation

### 7.1 Avoiding an intentionally weak baseline

The first matched-public comparator used normalized motion-residual weights with a fixed admission floor of 0.95. It admitted only one complete target history among 64 trials and is therefore too conservative to sustain a claim of algorithmic superiority. We acknowledged this threat, then [published an original-source development-only sensitivity grid](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37928937261). On the **already inspected** source cohort 176/177, lowering the score-only floor to **0.60** predicted 17 public admissions with no observed wrong selection, compared with 16 admissions and one wrong selection for the original set rule. The 0.60 threshold was thus selected *after* studying previous outcomes; these training figures are **not independent validation, calibrated probabilities, or an official ActionShift/DualABI baseline**.

To obtain a fresh falsifier, we froze the 0.60 rule in a [new original preregistration before constructing or running the new 194/195 simulator cohort](https://github.com/lindicaphxag-tech/ManiSkill/commit/a8dbef81da3f7640a452a94d1bd1e90266c4b289). Its admission requires only the maximal normalized Gaussian-shaped residual weight to exceed 0.60 and that winning candidate's achieved-XYZ segment residual to fall within the *old* task-specific epsilon; critically, it **does not require the original set-membership unique-winner and 2-mm gap conditions**. No threshold was optimized using the 194/195 outcomes and no source-policy checkpoint was retrained.

### 7.2 Physically matched experiments and results

The new PullCube and StackCube original reset identities are **1940001–1940032** and **1950001–1950032**, respectively. Each task contributes eight genuine native command *applied/held* cases for each of the four t2/t3 execution truths. At each original reset, ten independently stepped ManiSkill native controller treatments experience a shared policy-command/fault-control intervention. Before their first differing information decision, the source-physical auditor verifies equal native command traces and equal achieved *and private-audited commanded* full SE(3) physical prefixes for the methods being compared. The two adaptive methods receive **the same two achieved XYZ public observation events per original reset**, and both pay for the same t4 actually stepped known-delivered neutral control opportunity. Thus no no-information opponent is mislabeled as an equal-sensing baseline.

[First real 10/10 fully successful native PPO PhysX experiment and original full64 auditor](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37929461571); [second permanent independent source reconstruction and six intentional original evidence corruption checks](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37930210264); [full 16 original shard/source auditor JSONs, two full audits, and exact hash manifest](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/strong-score060-matched-ack-new64-20261009/research/frozen_policy_transfer/evidence/strong_score060_original64_1940001_1950032).

| Genuine new 64-state native PPO controller study | Set history admission | **Prior-training-selected 0.60 score only** | Always private read |
|:--|--:|--:|--:|
| Original official task successes | 59/64 | 59/64 | 59/64 |
| Authentic controller target readbacks | **52** | **53** | 64 |
| Complete native SE(3) history public authorizations | **12** | 11 | 0 |
| Audit-only wrong confident native target histories | 0 | 0 | N/A |
| Achieved XYZ sample events used in information decision | 128 | 128 | 0 |
| Actually matched double-ACK / predecision full-pose source reset states | 64/64 | 64/64 | 64/64 |

All three methods have exactly the same 59 success and five failed reset/task identities, and the set rule's one-read advantage over the stronger **same-public** challenger is a trivially small empirical difference. Binary official success provides no task-level treatment discrimination on this cohort, and none is claimed. The fixed private-reader control does not use the 128 public information events as its authority criterion; its 12-read excess is not an equal-total-information superiority result.

The [original-source exact paired and conditional-risk cost report](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/strong-score060-matched-ack-new64-20261009/research/frozen_policy_transfer/evidence/strong_score060_original64_1940001_1950032/reviewer_complete_risk_sensing_and_task_stats.json) shows no task-success discordances and an exact paired McNemar two-sided p value of 1. This does **not** establish formal noninferiority or method equivalence. Among only 12 set authorizations, no wrong native target was observed; even under the unjustified iid Bernoulli approximation, the one-sided 95% exact upper wrong-rate bound would be **22.1%**, and 11 successful strong-score authorizations permit **23.8%** by the same idealized calculation. Shared controller dynamics and source-trained response envelopes invalidate a simple iid deployment guarantee. These numbers should never be called physical-control safety certification.

### 7.3 Scientifically meaningful negative finding

The new test eliminates a potential low-quality interpretation of the earlier 15-read saving against a nearly-always-query 0.95 threshold. The stronger 0.60 baseline reaches essentially the same task-success, sensing-cost and observed latent correctness as original set membership, under the same physically executed actions and publicly sampled XYZ. In the first cohort, the original set method *did* authorize one significantly incorrect controller target on a successfully completed task. In the later cohort, both methods observed zero wrong confident target histories, but confidence sample sizes were small. It is therefore incorrect to call unique set-history admission intrinsically safe, or to claim a large advantage over tuned same-public models.

### 7.4 A separate negative control: 0.65 dual-evidence gate

A [previously disclosed posthoc 0.65 set-uniqueness AND score-filter trial](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37927919064) used a different 64-reset cohort (182/183), with **62 actual fully fault-exposed matched states** and **two early stopped original StackCube states** retained in the intention-to-treat denominator. It reported **53/64 official tasks with 41 private reads** for the original set rule, **53/64 with 45** for the 0.65 conjunction, and **54/64 with 62** for the fixed reader; both adaptive strategies had **zero observed confidently incorrect histories** on that cohort. The extra 0.65 filter was not independently calibrated, increased private target reads by four, and did not demonstrate a causal safety benefit. The original first-run failure and amendment history are deliberately preserved. This negative result is not pooled with the 194/195 prospective study.

## 8. A theoretical distinction that explains the empirical failure

Let \(H\) be the physically true native target history, \(Y\) the available publicly observed motion segment, and \(C_\epsilon(Y)\) the set of native SE(3) history indices whose projected achieved-XYZ residual is at most \(\epsilon\). A set gate may authorize if \(|C_\epsilon(Y)|=1\); yet that unique member may be wrong if the physical response law does not cover the real \(H\). For the event \(A\) that a unique history is authorized and \(W\) that its identity is physically wrong, elementary logic gives

\[
 W\cap A \subseteq \{H\notin C_\epsilon(Y)\}.
\]

Hence a **separately justified** distributional coverage statement \(P(H\in C_\epsilon(Y))\ge 1-\delta\) would imply only the *unconditional* \(P(W\cap A)\le\delta\). At nonzero admission probability, it implies the weak *conditional* bound \(P(W\mid A)\le \min\{1,\delta/P(A)\}\), which need not be small if the observer admits few samples. None of our currently source-trained physical response residual envelopes has been shown to satisfy a distribution-shift-robust coverage guarantee; thus even this numerical bound is **not instantiated** for the robot experiments. These elementary probability statements are not presented as a new theorem, but as necessary restrictions on any proposal advertised as "certified" or "safe" hidden controller-memory recovery.

The actual PullCube 1760020 case demonstrates why model comparison and model validity are different. The wrong executed history fitted the model inside epsilon and won by more than the selection gap, while the true target history was excluded; after an erroneous full-pose authority decision, the third-party PPO nevertheless completed the task. No number of stronger winner-gap tests on the *same invalid response model* guarantees this cannot recur.

## 9. Main-conference evidence requirements and final supported claim

The present work now provides a real, source-replayable physically executed **state correctness vs official task success** discrepancy, a full crossed 2×2 unknown-ACK controller experiment, a truly held-out direct read-cost vs strong same-public competitor and disclosed negative calibration/threshold results. It does **not** yet provide a prospectively validated algorithmic mechanism that consistently dominates a genuinely strong same-information and same-probe-budget opponent on a new controller family. A research paper should not solve that gap by renaming abstention as zero-error safety.

Necessary further validation includes (i) an independent **out-of-model physical-dynamics validity channel** that can prevent true-target exclusion without using private target information, (ii) matched-resource actual strong active action probes from the authors' ActionShift/DualABI benchmark rather than a manually tuned static residual score, (iii) a truly different verified target-relative controller/robot family with successful frozen-policy closed-loop manipulation, and (iv) external investigator-chosen reset seeds executed and audited outside the authors' fork. The real LIBERO SmolVLA tasks currently use a source-inspected *achieved-frame* native OSC controller action convention and cannot be relabeled as the same ManiSkill target-relative hidden-memory fault. Other-body VLA forward calls do not count as fault-recovered closed-loop tasks. No physical hardware safety, actual packet loss, peer-reviewed acceptance or top-conference status follows from this manuscript.

**Current defensible conclusion:** public achieved motion can sometimes substitute for a controller target-register read after two real missing ACK truth possibilities, but the private-read advantage largely vanishes against a prior-data-tuned same-public-information opponent, while task completion can completely mask a materially erroneous hidden-state authorization. Correctly estimating **model validity** is the unresolved central algorithmic target.

## 10. Exact reproducibility and prior-art declaration

The core observed mechanism is *missing native execution truth* when a known action ABI compounds increments from internal commanded target memory. Broader belief adaptation, controller inference and active probing already appear in ActionShift, ActionABI and classical set-membership estimation. This is a narrow physically audited robot policy-transfer study, not the first such uncertainty framework or a full official ActionShift comparison. An uncalibrated 0.95 residual-weight gate is an intentionally source-frozen comparator, not a state-of-the-art Bayesian model.

The limitations are substantial: one Panda/controller semantics family, two published frozen PPO tasks, one native PhysX engine, two particular fault indices, a known action chart, no actual communication packet loss, a manually enforced neutral physical step, no independently certified dynamics error bound, no force/collision hardware safety, no physically executed new learned VLA checkpoint and no genuinely outside-investigator reproduction. There is no peer-reviewed paper acceptance or upstream research integration.

Original primary provenance and falsifiable review entrances are public:

- [First 64-state/640-controller-world native PhysX execution and full original all-state auditor](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924117746).
- [Hash-pinned second independent full-source audit and permanent archive, including the incorrect confident sample](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924749286).
- [All untouched original task-fault datasets, SHA-256, paired statistics and failure cases](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/matched-public-bayes-native16-20261009/research/frozen_policy_transfer/evidence/matched_same_public_bayes_original64_1760001_1770032).
- [Source-backed concrete 1760020 false confident history even with true task success](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37925148881).
- [Independent complete source audit code](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/matched-public-bayes-native16-20261009/research/audit_matched_public_bayes_new64.py) and [source-only paired cost auditor](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/matched-public-bayes-native16-20261009/research/reviewer_matched_public_cost_and_uncertainty.py).
- [Earlier physically matched full 64-state 2×2 native prefix experiment](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37921574816), a distinct cohort and comparator protocol.

**Supported conclusion:** public history inference can substitute for some private controller target reads under finite, known native action semantics and empirical motion assumptions; nevertheless an actually successful manipulation trial can contain a materially wrong confidently selected target history. Scientific progress therefore requires measuring *authority correctness* alongside downstream task success and designing a validated abstention mechanism under motion-model misspecification, not merely optimizing read counts.


## 11. Fresh physical response-shift stress: failure of a known-command anchor

The author's new source-frozen 64-reset/640-native-PhysX-world Panda joint-drive stress independently changed physically read-back stiffness/damping across the seven arm joint drives. Slow and fast source conditions were 500/70 and 1500/130, respectively. This is a real simulated *dynamics-shift* intervention, distinct from changing the controller's target-memory ABI. The same frozen PPO, four true ACK patterns and source model stayed fixed. Two source methods received the same actual t4 public probe, but a new candidate validity monitor observed **two additional achieved-XYZ samples at known-delivered t1** (and incurred their public-sensing cost) to decide whether the task's empirical response model was trustworthy later.

| Real 64-state/640-world OOD task cohort | Official completions | Private target reads | Public XYZ samples | Public histories admitted | Confident wrong observed |
|---|---:|---:|---:|---:|---:|
| Original frozen public history witness + query | **56/64** | **56** | **128** | **8** | 0 |
| Earlier known-delivered t1 public anchor + query | **56/64** | 62 | 256 | 2 | 0 |

The actual historical model was outside support on **8/64** future response states. The earlier known-response anchor caught **4/8** invalid cases but also flagged **30/56** physically valid later states. The resulting sensitivity is 4/8; specificity is 26/56, with denominators verified from the original 64 raw source cases. **This is a negative result for the proposed preventive response anchor**: extra early evidence can be invalidated by a subsequent physical regime change. It is not a test of a genuinely contemporaneous second sensor or an officially proven OOD-safe algorithm.

- [Authentic initial run: eight genuine physical shards; original final audit failed due to missing dependency](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37928529745)
- [Audit-only repair, permanently archived unchanged original 640 worlds](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37929383380)
- [Source-locked actual OOD detector sensitivity/specificity](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37929735330)
- [Full original OOD raw source archive](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/dynamics-shift-anchor-ack-new64-20261009/research/frozen_policy_transfer/evidence/ood_pd_drive_known_ack_anchor_original64_960101_970132)

**Falsifiable new mechanism challenge:** Model support must be tested *at the intended point of authorization*, using information whose physical cause is tied to current response rather than a stale earlier certificate. The existing evidence does not yet establish how to do this safely or cheaply.

## 12. Actual additional public motion degree-of-freedom feasibility: SO(3), and why naive fusion is wrong

Before developing a quaternion-based authority algorithm, we preregistered a **read-only actual physical SO(3) sensor study** on **16 genuinely new reset states and 160 native PhysX controller worlds** (8 PullCube, 8 StackCube; 4 true physical ACK combinations twice per task). Unchanged frozen PPO and unchanged original XYZ and 0.60 public-score history decision branches physically executed an original known-delivered t4 native neutral action. We newly measured the public end-effector **quaternion before and after that exact actual physical action** from its genuine native achieved-EE pose. The resulting public score for each intact candidate history is the SO(3) geodesic to the shortest geodesic arc connecting the pre-probe achieved orientation to that history's hypothetical commanded-target orientation.

These quaternion scores **never entered the robot's target-history decision or downstream action**. The actual current controller target is used only by the source auditor after physical stepping to label which candidate was truly correct. Thus this is an **observability feasibility experiment**, not a performance claim for a new SO(3)-aware controller.

| Original new 16-state feasibility cohort | XYZ-residual minimum agrees with audit-only true history | SO(3)-arc minimum agrees with audit-only true history |
|---|---:|---:|
| All 16 actual source histories representable | **13/16** | **7/16** |

All 16/16 probe pairs were successfully physically measured in both original public arms, and original source methods completed **15/16** tasks each, with **10 versus 12** private target reads. Across the 16 original cases, XYZ and orientation argmin choices disagree **9** times: 6 are *XYZ correct and SO(3) wrong*, 3 are *both wrong*, and **zero** are *SO(3) correct but XYZ wrong*. Therefore merely replacing the XYZ ranking with a simple SO(3) geodesic ranking is **worse on this source cohort**; this is a real **negative** rather than a proposal for an unsupported new fusion. A method that claims independent sensor reliability based on the same robot's achieved-pose quaternion is also mistaken: XYZ and SO(3) are distinct degrees of freedom, but not necessarily statistically independent sensors, and their response model may share contact/regime shift errors.

- [Original successful physical 16 × 10 true PhysX simulation and actual quaternion telemetry CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37931907253)
- [Permanent original 16-state physical quaternion/XYZ candidate-residual archive, 16 complete original task identities and audit-only true labels](https://github.com/lindicaphxag-tech/ManiSkill/tree/evidence/genuine-so3-public-16-pilot-20261009/research/frozen_policy_transfer/evidence/physical_public_so3_original16_2040001_2050008)
- [Independent original source-only measurement feasibility audit and SHA256](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37932588618)

**Next legitimate algorithm question:** Can one actively choose *physically safe bounded informative native probe actions* that separate otherwise observationally indistinguishable complete histories **under verified current-model uncertainty**? Probe selection, energy/control motion, sensing and private reads must all be charged and actually executed. The source study above does NOT demonstrate such a new active method.

## 13. Source forensic: why a real 1,152-world factorial did not establish the intended causal contrast

A more ambitious preregistered experiment physically stepped the same **32 nominal reset seed identifiers under all four applied/held truth patterns** using nine actual native controller arms per cell: 128 task/fault cells and 1,152 real native PhysX worlds. All 16 physics shards completed, but the original independent full-population **strict exact source-state identity auditor failed**. We independently downloaded and re-scored **every original 128 source case without rerunning physics**, rather than lowering an exact-match criterion.

The forensic result: **25/32** nominal seed groups had bitwise identical initial policy-source observation SHA256 values across all four truth conditions; **7/32** did not, *all StackCube*. The original source contains two different initial observation hashes in each offending group. This failure invalidates any blanket conclusion that all 32 four-truth physical comparisons are strictly matched initial-state causal pairs. No cherry-picking 25 passing seeds is allowed after outcomes.

All original task outcomes remain preserved (descriptively: 111/128 public task completions versus 106/128 fixed read, 95 versus 128 private reads), but they **cannot be asserted as a validated paired causal effect from strictly identical physical starting states**. Deterministic seed reuse does not itself certify equal source physical state across jobs. A new physically rerun prospectively frozen experiment should explicitly record a canonical full simulator state, restore it into each truth-arm simulator using verified original ManiSkill state APIs, compare actual physical state tensors/initial observation to preregistered numeric or byte-exact criteria **before task control starts**, and only then report all original conditions, every refusal and genuinely clustered statistics.

- [Original genuinely stepped but failed strict factorial audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37930607707)
- [Entire original 16-shard/128-episode physical evidence forensic original full audit PASS](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37932146708)
- [Permanent raw 1,152-world original and all 32 source hashes, including 7 mismatches](https://github.com/lindicaphxag-tech/ManiSkill/tree/audit/forensic-factorial-reset-identity-20261009/research/frozen_policy_transfer/evidence/original_1152_factorial_failed_identity_audit)

## 14. Closest prior work and reviewer-grade claim revision

The released [ActionShift](https://github.com/Archerkattri/actionshift) / ActionABI line already addresses hidden action contracts, finite beliefs and active probes. Its original benchmark changes hidden channel permutation/sign/gain, frame, target convention, delay and gripper semantics; the present narrower tested problem is *unknown actual execution of already understood target-relative native commands*. This is a **distinct fault axis**, not an invention of belief-state inference or active probing. Official DualABI full active identification **has not been executed** with this precise missing-execution-ACK truth and matching public/private read budget; a custom matched same-XYZ score baseline is not an ActionShift SOTA comparison.

A close high-quality contemporaneous caution is Jessie Yuan, Yilin Wu and Andrea Bajcsy, **When to Act, Ask, or Learn: Uncertainty-Aware Policy Steering**, RSS 2026 (DOI: **10.15607/RSS.2026.XXII.142**), which already applies conformal calibration to an execute/clarify/intervene steering decision and demonstrates simulation plus hardware. The present research **does not invent calibrated abstention or “act/ask” logic**. Its domain-specific focus is *reconstructing and verifying a latent commanded-target execution-history variable* under a known native controller, including the epistemic difference between a correct task and an incorrect authorized memory. Unlike the RSS 2026 accepted method, our current evidence has no actual hardware generalization or validated cost-efficient OOD controller-authority recovery.

Classic total-variation two-point testing, data processing for deterministic score reweighting, and standard split-conformal marginal coverage should be **attributed as existing theory**; the latter does not guarantee conditional error given authorization, controller collision safety, or reliability under nonexchangeable dynamics.

- [RSS 2026 UPS official paper](https://www.roboticsproceedings.org/rss22/p142.html)
- [Original ActionShift research package](https://github.com/Archerkattri/actionshift)

## 15. Explicit outstanding-main-conference gates (not satisfied by wordsmithing)

The current research earns credit for source-frozen fault-injection experimental design, demonstrated false authority even on successful tasks, numerous genuine counterexamples and careful external reproduction packets. It **does not yet show a superior, original and reliable recovery algorithm**, or a full cost-matched official active state identification comparator. A credible **outstanding CoRL/RSS/ICRA main-paper** claim would require all of:

1. A **novel verified physical intervention or real contemporaneous source-validity measurement** that improves hidden target-state authority, with a preregistered separate calibration and holdout, and wrong-confident decision rate plus uncertainty; never transform the same signal twice and call it an independent modality.
2. Task success, complete latent history correctness, refusal/read count, physically executed probe command cost, XYZ + SO(3) sensor bandwidth, wall-clock latency and task-contact regime, stratified by task and all actual four ACK truth conditions.
3. Fair, physically executed, truly equal-public-information/cost strong score and active-information gathering baselines, not only fixed privileged readback. The stronger prior-tuned 0.60 score-only genuine native PhysX comparator had the same **59/64** official tasks and used **53** reads versus the original **52** — the proposed query advantage there is **ONE read**, not 25–35%.
4. A task-competent checkpoint and verified **second true target-relative controller or robot family**, rather than treating the existing achieved-EE-relative LIBERO VLA controller as target-memory-equivalent.
5. A real outside investigator independently choosing unpublished task seeds and running the original native PhysX source on their own fork; author-only CI cannot substitute. Repaired source audits verify author artifacts, not adoption.
6. Rigorous true identical-initial-state physical counterfactual pairing and predeclared seed-cluster statistics; the original 7/32 reset-hash mismatch must be disclosed.
7. A venue-compliant anonymous eight-page main paper with source-derived figures and scholarly citations, whose central claims are actually supported before submission.

**Current publication ceiling:** a carefully falsified, unusually source-auditable study of *observability versus authority under unknown command execution* in frozen simulated manipulation policies. Future method breakthroughs may lift it toward an outstanding main paper, but cannot be asserted prospectively. This manuscript is a research draft, not accepted, published or externally replicated.

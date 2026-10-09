# When Task Success Conceals Incorrect Controller Memory
## Matched-Information Evidence and a Failure Witness for Hidden-ACK Robot Policy Transfer

*Research manuscript v2.3 · 9 October 2026 · author-operated genuine ManiSkill CPU PhysX results; not peer reviewed, externally reproduced or formally safe.*

**Authorship requires confirmation before submission.** The named frozen PPO checkpoints are third-party published models, not newly trained models.

### Abstract

Robot policy transfer can fail when an action described as an end-effector displacement is interpreted relative to a destination controller's last *commanded* target rather than the achieved tool pose. With uncertain command acknowledgements, this target becomes a latent execution-history variable. A finite-history adapter may use observed end-effector motion to identify a complete target pose and avoid reading the privileged controller register, but task completion alone does not establish that the resulting hidden-state belief is correct. We study this distinction in a preregistered 64-reset, 640-controller-world ManiSkill PhysX experiment with two genuinely applied/held unknown ACKs, four balanced fault patterns per task, and source-frozen PullCube/StackCube PPO policies. Before their first different information decision, all compared controllers execute identical native actions, agree in achieved and target SE(3) pose, and experience the same known-delivered neutral motion. We compare complete-history set-membership admission, a separately executed normalized-Gaussian-residual *uncalibrated* score gate using **the exact same two public XYZ observations**, and mandatory state readback. The methods complete the exact same 52/64 tasks. Set-membership admission uses 48 privileged reads and identifies 16 complete histories; the same-public residual-weight gate uses 63 reads and identifies 1, and fixed readback uses 64. Crucially, set-membership makes **one confidently wrong complete-history selection**: a physically executed, officially successful PullCube episode infers a commanded target displaced **67.6 mm and 0.0536 rad** from the true target. A pre-frozen empirical response envelope admits the incorrect candidate while excluding the physically true one. Thus our supported positive result is conditional private-target-read economy with a nonzero false-authority rate, not safe hidden-state recovery. The counterexample motivates an explicit future reliability-verification channel or calibrated abstention rule; neither has been validated in this paper.

**Keywords:** robot action semantics; latent execution history; controller target memory; physical acknowledgement uncertainty; set-membership inference; model misspecification; task success masking.

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

## 3. Prospective experiment and denominator

The main [preregistration Git blob 9c758954…](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/matched-public-bayes-native16-20261009/research/MATCHED_PUBLIC_BAYES_NEW64_PREOUTCOME_V1.json) was committed before executing the new 64-state cohort or viewing the outcome of the earlier 16-state development pilot. The new reset identities are PullCube **1760001–1760032**, StackCube **1770001–1770032**. For each task, all four true t2/t3 applied/held patterns are physically realized eight times. The native action chart, original third-party PPO checkpoints, source empirical motion epsilon and competing score threshold are frozen. All 64 original states launch ten independent physical comparator worlds, for **640 genuine controller simulations**. The statistical unit is 64 task/reset states, not 640 separate robots or learned policies.

The original [10-job real PhysX and independent source auditor succeeded](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924117746). All nine original ZIP hashes, 16 unmodified shard source/audit JSONs, full-source paired results and five-way/greater adversarial evidence checks were independently [reverified in the archival run](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924749286). The [complete original archive](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/matched-public-bayes-native16-20261009/research/frozen_policy_transfer/evidence/matched_same_public_bayes_original64_1760001_1770032) retains all failures, all private read counts, the complete source ledger and deterministic uncertainty calculation.

## 4. Primary results and information-budget transparency

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

## 6. What an actual next algorithm must overcome

A deeper method must determine when the response model itself is trustworthy. Requiring one residual to be lower than every other predicted residual only compares hypotheses *inside* the assumed motion model; it does not test whether actual physical dynamics lie inside the model. The 1760020 source witness shows that a highly separated but misspecified response can be worse than honest abstention.

A defensible new method would estimate out-of-sample motion-model error on truly disjoint calibration resets, explicitly include this epistemic uncertainty in complete-history admission and issue a private target read whenever model validity is not supported. Candidate approaches include independently calibrated residual tubes with coverage assumptions, public orientation/velocity consistency channels or a genuinely discriminative additional low-risk probe. They have different physical sensor/action costs, and sequential correlated repetitions of one public probe have previously failed to improve this benchmark. None of these proposals is counted as an already verified positive result. New outcome-free pre-registration and independent unseen physical trials are necessary.

This also clarifies why the result is not a general SE(3) identification theorem. If different actual latent histories produce overlapping public observation distributions under unknown dynamics, history identity is not identifiable from those public samples alone. To claim safety, one must either add a validated sensor/assumption or abstain and query the private state.

## 7. Reproduction, prior art and honest acceptance boundary

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

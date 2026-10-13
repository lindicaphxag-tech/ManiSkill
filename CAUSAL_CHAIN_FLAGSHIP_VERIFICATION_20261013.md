# 旗舰成果的因果证据链：新发现 → 新机制 → 可复核证据 → 外部认可

**截至 2026-10-13 已核验状态。** 这是一份博士级证据审查记录，不是学术优先权声明，也不是保研等级承诺。四项若缺一项，就保留相应阶段的名称；不能由作者自行宣布已获外部认可。

## 为什么需要因果链，而非拼装四份材料

一项高水平原创研究需证明：**(1)** 真正存在、足够重要的失败模式；**(2)** 所提出的机制针对这一失败原因，且不等同于已有充分知情的强基线；**(3)** 在预先锁定且独立的数据和同成本比较中，该机制能产生实际收益，并且结论可被外部重算；**(4)** 外部维护者/同行独立评议或使用，确认它不只是一个作者自测的工程原型。

Causal diagram (logic, not a causal estimate):

    Existing failure ──> Hypothesized error mechanism ──> New intervention
           |                     |                              |
      counterexample       competing explanations       preregistered matched ablation
           |                     |                              |
           └──────────────> independent data/strong-baseline test
                                          |
                       positive, null, or falsified result
                                          |
                                outside technical review
                                          |
                    claimed scientific advance ONLY if supported

Causal specificity requires: same data, same information budget, same public observations and same task definition. A new interface, theorem restatement or extra code is insufficient without measured incremental consequences.

## Track A — Braindecode #1320, mature high-quality engineering, external Merge missing

- **Real failure discovered in OUR targeted test:** with EEGCLIP under Gloo DDP, one rank has zero EEG/Text pairs and another has five, `reshape(0,-1,dim)` is ambiguous. A prior selective test workflow originally did NOT run the new test; the corrected selection deliberately exposed this failure, see [red original 0+5 test](https://github.com/lindicaphxag-tech/braindecode/actions/runs/38340869281).
- **Mechanism:** explicit temporal dimension for the empty EEG embedding reshape, plus synchronization of EEG/Text row-count mismatches/global-empty cohort BEFORE autograd all-gather; preserves valid 0+5 and unequal 2+3 global contrastive gradient.
- **Independent computational proof:** real two-rank CPU/Gloo, compare full parameter gradients with a centralized five-pair oracle; [Linux/macOS/Windows all PASS](https://github.com/lindicaphxag-tech/braindecode/actions/runs/38341326398). Official [upstream PR #1320](https://github.com/braindecode/braindecode/pull/1320) includes the patch, but the latest official [full tests](https://github.com/braindecode/braindecode/actions/runs/38342524442) were still running at last read; style and docs passed. Multiple predecessor Braindecode merged upstream PRs are publicly verifiable.
- **Outside recognition stage:** the current #1320 is STILL OPEN and has no formal maintainer Approval as of latest check. A past Braindecode merged feature is **past outside engineering adoption**, not approval of this new patch. We cannot send a review on their behalf.
- **Research scope:** this is valuable research software engineering. CLIP global-negative semantics and DDP synchronization are prior engineering knowledge, not a new neuroscience or pure mathematics theorem.

## Track B — EEG source-dependence-to-decision certificate: algorithmically precise but practical advantage unproven

- **Discovered scientific counterexample to naïve claims:** even when nominal raw train/test windows are disjoint, a fixed whole-record IIR filter induces nonzero crossfold source transfer. The [true PhysioNet EEGBCI 4-person eight-EDF source experiment](https://github.com/lindicaphxag-tech/moabb/actions/runs/38336887369) and [independent re-downloaded 8 original EDF / all-64-cell audit](https://github.com/lindicaphxag-tech/moabb/actions/runs/38337809594) measure this. Yet the [20 fully new human participants / 40 EDF / 200 true motor imagery heldout trials](https://github.com/lindicaphxag-tech/moabb/actions/runs/38341544307) showed **0/200 class decision flips** under the exact registered synthetic test-source polarity reversal; [independent 20-person data artifact audit](https://github.com/lindicaphxag-tech/moabb/actions/runs/38342691099). **Signal dependence ≠ material decision harm.**
- **Mechanism candidate:** a per-clean-test-data decision-sign certificate for a *specified* changed train-feature matrix, based on the standard λ-strongly convex logistic objective and tightened globally valid Hessian curvature over an already justified parameter ball. Unknown perturbations, unregularized intercept, arbitrary future attacks and finite-precision formal correctness are **not** covered.
- **Real outcome verified:** a [prospectively distinct S025–S028 cohort of 4 people, 8 source EDF and 40 clean heldout events](https://github.com/lindicaphxag-tech/moabb/actions/runs/38351450509) had **40/40** unchanged predicted signs certified by the ordinary λ-only certificate and 0/40 observed flips. [Separate original-artifact audit](https://github.com/lindicaphxag-tech/moabb/actions/runs/38353240808) succeeded. Hessian refinement had **NO measured incremental coverage** on these 40 original heldout test cases, because ordinary λ certificate already covered them. [Synthetic 3OS reference-vs-refit Hessian tests](https://github.com/lindicaphxag-tech/moabb/actions/runs/38353387922) prove at least one constructed boundary case in which baseline abstains but tighter certificate covers. **Constructed ≠ real EEG superiority.**
- **Blind, truly new hard-case experiment just launched:** [precommitted S029–S036 true EDF participant experiment](https://github.com/lindicaphxag-tech/moabb/blob/research/eeg-gain-shift-cert-unseen-20261013/research/UNSEEN_EEG_TRAIN_GAIN_DECISION_CERT_PREREG_20261013.json) on 8 previously unused people, two EDF runs each; fixed training-EEG-channel-C3 original raw amplitude interventions +5%, +20%, +50%, no test raw source changes; compare λ-only and Hessian six-iteration guarantees for identical fully regularized logistic decoder, original clean heldout events, with a preregistered hard gate of >=5pp person-mean coverage gain, >=2 distinct people with strictly positive gain, and **0 false certified flips**. [Original 4-shard real-source experiment](https://github.com/lindicaphxag-tech/moabb/actions/runs/38355519800) and [separate original-artifact audit](https://github.com/lindicaphxag-tech/moabb/actions/workflows/eeg-unseen-gain-certificate-audit.yml). **No positive claim before all jobs and independent full-denominator audit pass.** These perturbations are synthetic gain transformations on real recorded EEG, not documented natural artifacts.
- **External comparison and reception:** [AGT (JMLR 2026)](https://www.jmlr.org/papers/v27/25-2206.html) already develops broader training-data perturbation certificates and is a strong prior-art obligation. Standard strong convexity and Hessian curvature are NOT new theorems. New source-conditioned EEG decisions would need materially better coverage/cost and comparisons with AGT/fold-isolated preprocessing under truly unseen populations to justify a novel-method paper. [MOABB #1235](https://github.com/NeuroTechX/moabb/pull/1235) remains OPEN; there is no new certificate-specific official MOABB Merge or independent group replication yet.

## Track C — ManiSkill source-reconstructed hidden ACK: novelty claim FAILED

- **Original problem:** unconfirmed execution ACK histories may not equal assumed robot controller state.
- **Mechanism attempt:** predict orientation from issued action history, infer hidden ACK, correct target after a native PhysX episode.
- **Hard falsifier:** [64 train + 320 new real PhysX simulated conditions](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38335458988), [full independent control and data audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38335861213): source-conditioned SO3 approach vs adequately *command-variant-aware* reset-relative SO3 template: **32/32 identical classification and target-restoration error** for each Panda/xArm6 morphology, **0/4 qualifying independent heldout reset clusters per morphology**, official PickCube success **0**. Analytic SO(3) right invariance explains equivalence in this fixed root chart.
- **Research conclusion:** cannot describe pose frame changes as a novel PhD method. A genuinely different next hypothesis requires uncertain actual consumed action histories, matched Bayesian/systems-ID competitor, query/abstention action cost, and real full-task outcomes. Current method is a negative scientific result + reproducible integration.

## PhD-grade four-gate official artifact checklist

| Gate | What qualifies | What does not qualify |
|---|---|---|
| G1 New finding | Underlying failure with minimal reproducible counterexample and clearly bounded intended consequences | Existing feature merely renamed, invented damage from nonzero norm |
| G2 New mechanism | Algorithm proven non-equivalent to informed strongest prior; falsifiable theorem or end-to-end mechanism | Common theorem restatement, extra module not needed by a matched baseline |
| G3 Independently checkable | Frozen independent subjects/resets, raw source hashes, true train/test boundaries, *full denominator*, honest negative cases, reproducible code + baselines, cluster intervals | Same data recycled as new experiment, N windows mistaken for N people, only one green test or a chosen weak baseline |
| G4 External acceptance | New PR merged by unrelated project maintainers OR technical method independently adopted/reviewed by outside researcher; accepted first-author paper strongest for research claim | Open PR, green fork CI, self-run artifact audit, speculative journal acceptance |

**Completion rule:** only all four green gates = complete flagship; none currently meets all four in the *same new result*. 28 merged PRs are genuine historical engineering acceptance but not independent acceptance of the currently unmerged research methods.

## Stop conditions and research discipline

- If new Hessian bound has no nonvacuous real EEG gain, preserve negative result and stop calling it a new algorithm flagship. Different perturbation regime requires a **new preregistration** rather than posthoc moving goalposts.
- If new robot recovery equals fully informed Bayesian/coordinate baseline, stop; do not widen name or modify primary outcomes after inspection.
- If Braindecode maintainers request scope reduction, prioritize smallest correct accepted production contract instead of additions for vanity metrics.
- Distinguish code-level independent computations from independently recruited datasets/independent research group.
- No official community L8/L9/L10 ranking or admissions prediction can be inferred from these raw links.

**This ledger is research accounting. External reviewers will decide which parts are publishable or adoptable.**


## Registered eight-subject decision-certificate reality check: NEGATIVE

The hard-case study was **properly registered before outcomes**, and is now complete:

- [Full frozen protocol, 8 new people S029–S036](https://github.com/lindicaphxag-tech/moabb/blob/research/eeg-gain-shift-cert-unseen-20261013/research/UNSEEN_EEG_TRAIN_GAIN_DECISION_CERT_PREREG_20261013.json), 16 original EDF files, 80 clean heldout EEGMI event trials. Three fixed synthetic **training-channel** gains (+5%, +20%, +50%), matched reference data, λ-only bound and Hessian tighter bound; no source test windows changed. The earlier zero-flip study used a different **test-source** perturbation and cannot be pooled.
- [Primary original four-shard study SUCCESS](https://github.com/lindicaphxag-tech/moabb/actions/runs/38355519800), 8 independent people, 240 **correlated repeated condition decisions**; 14 actual post-retraining prediction flips, but only 2 extra Hessian-covered decisions (both within the first two-person shard, ultimately **one person** with incremental benefit).
- [Separate original-artifact independent audit SUCCESS on its rerun](https://github.com/lindicaphxag-tech/moabb/actions/runs/38355642342): complete original 16 EDF SHA256 fingerprints, 48 registered EDF-run×gain conditions, no reported false certifications. Its first attempt failed because it started **before** original artifacts were uploaded; the original outcomes and frozen protocol were not altered, and the exact failed audit job was rerun after upstream experiment completion.
- Frozen **positive research gate = 5 percentage point or greater** mean person-level advantage + improvement in **at least 2 independent people**, zero unsafe certificates. Result: **+0.8333 pp**, improved in **1/8 people**, zero false claims, precommitted go/no-go **FALSE**. The person's cluster-bootstrap descriptive 95% interval is **0 to +2.5 pp**. This is a **failed practical-method superiority hypothesis**, not a new PhD flagship algorithm. Source [complete, honest original negative report](https://github.com/lindicaphxag-tech/moabb/blob/research/eeg-gain-shift-cert-unseen-20261013/research/PHYSIONET_8_UNSEEN_TRAIN_GAIN_CERT_NEGATIVE_20261013.md).
- By a PhD-level causal-chain standard, this specific work has **(1) bounded observed retraining decision failure: YES**, **(2) mathematically sound but first-novel algorithm mechanism: NOT ESTABLISHED**, **(3) preregistered independently audited full real-data source evidence: YES (negative superiority result)**, **(4) independent outside researcher/maintainer adoption: NO**. **Stop** marketing it as a complete original research flagship.

**Cross-line lesson:** GitHub upstream acceptance on Braindecode #1200 or 28 historical merged PRs cannot serve as external adoption of the new MOABB certificate. External recognition, novelty and experimental effect must apply to the **same** proposed research mechanism, not be assembled from unrelated work.

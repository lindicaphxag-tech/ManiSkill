# PhD-level independent-review gate: external upstream engineering × algorithm originality × publishable research

**Frozen external-review standard, 2026-10-13.** This is a research *review rubric and prospective go/no-go*, not a claim of official university admission ranking, a doctoral degree, original proof priority, or acceptance by an external reviewer.

## Executive verdict on actual checked evidence

- **28 real external upstream merged PRs** by `lindicaphxag-tech`; notably Braindecode EEG-CLIP #1200 / NeuroRVQ #1218 / tokenizer #1223 / DDP EMA #1319, MOABB #1207/#1208/#1209, JAX and Ray. Strong, inspectable research-software engineering.
- [Braindecode #1320](https://github.com/braindecode/braindecode/pull/1320) global-negative DDP + valid 0-local/5-remote empty-rank gradient equivalence: own 3-OS Gloo test passes, latest official style/docs/acceptance green, full official test in progress at last read; PR **OPEN, NOT MERGED** and no maintainer Approval.
- [Original 4-person EEG signal transfer and independent raw-EDF audit](https://github.com/lindicaphxag-tech/moabb/actions/runs/38337809594) passed. [20 genuinely unseen people](https://github.com/lindicaphxag-tech/moabb/actions/runs/38341544307) retained 40 EDF and 200 clean heldout events with **0/200** class-prediction flips from the registered *synthetic* polarity-flip. [Independent 20-subject artifact audit](https://github.com/lindicaphxag-tech/moabb/actions/runs/38342691099) successful. **No evidence for a material downstream accuracy/label-leakage harm or a benefit from purge method in this regime.**
- [New S025–S028, 4 additional individuals and 40 heldout events](https://github.com/lindicaphxag-tech/moabb/actions/runs/38351450509): original whole-record true EDF experiment on *different explicitly fully regularized logistic objective* certified 40/40 decisions as stable to a specified synthetic raw-test-only perturbation; zero observed flips. [Independent source artifact audit](https://github.com/lindicaphxag-tech/moabb/actions/runs/38353240808) successful. **This does not certify the sklearn unregularized-bias classifier in the earlier 20-person experiment.**
- [Curvature-refined strong-convexity parameter radius](https://github.com/lindicaphxag-tech/moabb/actions/runs/38353387922): 3/3 OS synthetic exact-refit / near-margin test PASS. **No real EEG advantage:** simpler λ-only certificate already covered 40/40 new-person test events. Theory is established convex optimization, not an original mathematical theorem.
- [ManiSkill 64-train + 320 fresh native PhysX SO(3) tests](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38335458988), [independent artifact audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38335861213): source-history method and properly command-aware reset-relative strong baseline are **identical 32/32** on both morphologies; 0/4 positive-seed gates, official PickCube success **0**. Mathematical analytic right-invariance explains equivalence. **No scientific novelty win**.

## Non-negotiable PhD review checklist — all four gates independently necessary

### Gate A: research novelty and problem ownership

1. A carefully limited claim, not a buzzword: one *falsifiable* proposition and its precise scope.
2. 15–25 directly relevant *primary* articles and official upstream implementations, including strongest negative/provable competitors, DOI/date and related work/prior art matrix. Novelty must survive the best comparator, not selected weakest baseline.
3. Distinguish a new *problem formulation*, new mechanism, new general theorem, and new **system implementation of existing theory**; never conflate them.
4. A stated "what empirical or mathematical result would force withdrawal of the headline claim?" before seeing new test data.
5. External community has **not** accepted a novelty claim merely because source-code maintainer accepted a correctness fix.

### Gate B: mathematical/algorithmic validity

1. State all assumptions, domain, quantifiers, decision costs and exactly what data are accessible; if a certificate is conditional on ONE known perturbation, do not call it universal or adversarial all-attack robustness.
2. Separate exact-real arithmetic inequalities from floating implementation. Numeric soundness for high-stakes safety claims needs **verified interval bounds / outward rounding / formal proof**, not 1e-10 heuristic slacks.
3. Independent implementation/refit, exhaustive edge-case tests where tractable, counterexample search, and transparent failure modes.
4. All components need meaningful **module isolation**: replacing a new step with equally informed analytic reset-centering, Bayesian tracking, source-transformation or standard certificate must reduce something real; otherwise drop the novelty claim.
5. Compare computational complexity, memory and tuning/sample budget, not accuracy alone.

### Gate C: valid empirical science

1. Freeze primary endpoint, datasets, heldout people/environments, statistical unit, missing-case rule, negative-control and exclusion criteria **before** inspection.
2. Use truly unseen *independent data units*. Repeated trials, windows, action histories and conditions nested within one person/reset are correlated. Subject/reset-cluster bootstrap or hierarchical mixed models; report paired confidence intervals and effect sizes, not only p-values.
3. At least two fundamentally different data-generating environments or public source cohorts if the target claim is general; same PhysioNet EEGBCI files with different subjects establish *within-source* reproducibility, **not cross-dataset generalization**.
4. Strong comparisons: equal source information, equal budgets, equal hyperparameter tuning, standard Bayesian/AGT/analytical/production baselines, positive + deliberately hard negative cases, meaningful end-task outputs.
5. Never report desired uplift as actually observed. Failure to beat controls => transparent **negative** result and redefine/stop the mechanism.
6. Report wall-clock runtime, CPU/GPU memory, maintenance burden, seed/participant variance, model calibration, abstention/false intervention, raw sources and complete independent reproduction.

### Gate D: external scrutiny and adoption

1. Official up-to-date maintainer review plus MERGED status for claimed upstream contribution. Draft and fork-only results are marked as such.
2. Independent researcher reproduces results from files/code they did not author (preferably separate team). "Independent CI artifact audit written by the same author" is **independent program**, not independent research group.
3. A first-author full scientific preprint or journal/conference manuscript with real causal/conditional evidence, datasets/license and sufficient ablations.
4. Claims about first theorem/new method require dated literature proof and external technical referee feedback. A high-profile GitHub merge is not mathematically equivalent to Clay, Lean or longstanding open theorem resolution.

## Track-by-track PhD verdict and falsifiable next decision

### P0 — EEG-CLIP production-level upstream flagship
- Claim permitted now: a working integrated EEG dual encoder; new distributed global-negative computation with correct gradients and synchronized collective error contracts demonstrated on actual Gloo ranks.
- No claim of new CLIP/contrastive theory, new EEG foundation model architecture superiority, or Merge of #1320 yet.
- **Acceptance bar:** current full official upstream CI PASS + maintainer Approval + Merge; demonstrable epoch throughput/memory overhead; independent users can reproduce on CPU and GPU. Engineer an API acceptable to external maintainers; do not broaden before they review.
- Stop/cut: maintainer rejects public API after legitimate discussion; extract isolated minimal core and return clean measurements rather than piling features.

### P0 — EEG preprocessing-to-decision research flagship
- Actual observation: real SOS source transfer is nonzero, but 24 independent observed public human subjects/240 actual original test events have zero discrete label flips. Strongly regularized 4 **additional** fresh subjects/40 tests have λ-only certificate 40/40.
- **Hard doctoral-level falsifier:** a claimed new filter guard or certifying method must outperform full fold-isolated preprocessing, feature-margin baseline, λ-only gradient certificate, Hessian-bound refinement, and **AGT (JMLR 2026)** or another strong robustness baseline *on nonvacuous changed-decision or abstention risk under a new blind cohort*. Simply reproducing 40/40 with a stronger bound is not a publishable improvement.
- Primary endpoint recommendation: **subject-level fraction of actually changed class decisions or certified nonflip** at an explicitly calibrated intervention budget; secondary: false refusal, retained valid training epochs, runtime/memory, calibration.
- **Important design:** no arbitrary test-data labels in optimizer; no per-test-cluster tuning or retrospective hard-case selection. Include at least 2 public EEG cohorts, not just more EEGBCI persons. Run multiple physically interpretable interference magnitudes; separate synthetic sensitivity from naturally observed label leakage.
- **Stop/cut:** if baseline covers all cases with equal compute/decisions, publish original negative diagnosis and redirect to another effect (e.g. calibration/provenance under actual distribution shift). No inflated "large gain."

### P0 — Embodied execution-authority / recovery research flagship
- Strict falsification already occurred: known-root/controller SO3 source goal and a command-aware analytical reset template are equivalent; Native PhysX variant-matched learned reset comparator ties; original PickCube task success 0.
- **Only admissible new novelty target:** uncertainty about the controller chart/actual executed action identity with externally verifiable observation limits, query/abstain cost and physical task outcomes, **not** a rotation coordinate change.
- Baselines required: truthful state/feedback when available, optimal or well-approximated Bayesian belief tracking, system-ID under same query/rollout budget, action-aware reset templates, published action-chunk/RTC recovery.
- New success measure: clean/full-task success across heldout tasks and morphologies, recoverable failure class sensitivity/specificity, task time, contacts/collisions and abnormal actuator commands; controlled reset clusters count as independent units, not 320 independent robots.
- **Stop/cut:** if source-aware policy equals Bayesian/command-aware comparator at equal observation budget, state as engineering integration, not frontier original research.

### P1 — Adjacent LLM / robotics correctness infrastructure
- Safely incubate Transformers cached-prefix continuation (original issue by another reporter) and LeRobot state/action contracts; avoid competing PRs where credible original fix authors already active. Own original failure analysis+full regression/CPU parity before any new upstream PR.
- The theme "actual executed state differs from software assumed state" may motivate a shared formal contract, but first show one **non-trivial cross-domain invariant** and two independent implementations; narrative similarity alone is not new theory.

### P2 — Medical CV geometry trust / MONAI
- C2P official reproduction is blocked by missing original code/weights referenced by README. Do not claim faithful official baseline or newly surpassed SOTA.
- Separate internal geometry self-consistency (already in C2P) from **genuinely independent external geometry evidence**. Patient-level external validation, heldout modality/protocol shift, DSC + HD95 + false suppression, OOD and 12-GB VRAM budget; strong geometry/uncertainty routing prior art.

## Paper decision as a critical anonymous reviewer today

| Track | Would accept a doctorate-level original-method paper today? | Why |
|---|---|---|
| EEG-CLIP merged models / open #1320 | **No, as an original math or original-ML-method claim** | High engineering merit ≠ demonstrated novel method gain; official review for #1320 pending |
| EEG source filter and decision certificate | **No — major scientific revision required** | Standard theory; currently nonvacuous realistic decision harm/benefit absent; no external dataset, no AGT hard comparison |
| ManiSkill SO3 hidden ACK | **No — original novelty hypothesis falsified** | Correct command-aware strong baseline ties; original task completion zero |
| Independent medical C2P new gate | **Not yet assessable** | Reproduction and full original source/weights missing |

This does NOT mean existing engineering contributions are trivial; rather doctoral research demands a complete novel inference and independent adoption.

## Prior art to check directly (nonexhaustive)

- Sosnin, Wicker, Collyer, Tsay. **Abstract Gradient Training: A Unified Certification Framework for Data Poisoning, Unlearning, and Differential Privacy.** JMLR 27(128), 2026: https://www.jmlr.org/papers/v27/25-2206.html
- Brookshire et al. **Data leakage in deep learning studies of translational EEG.** 2024: https://pmc.ncbi.nlm.nih.gov/articles/PMC11099244/
- **Best Practices in EEG Analysis: Preprocessing, Modeling, and Machine Learning.** preprint September 2026: https://arxiv.org/abs/2609.36609
- **Window leakage in clinical EEG machine learning: matched subject-independent evaluation across ADHD and Parkinson cohorts.** Frontiers 2026: https://www.frontiersin.org/journals/neuroinformatics/articles/10.3389/fninf.2026.1930795/full
- [Official Braindecode PR #1320](https://github.com/braindecode/braindecode/pull/1320) and [MOABB #1235](https://github.com/NeuroTechX/moabb/pull/1235) plus the public evidence ledger [FLAGSHIP_PUBLIC_EVIDENCE_20261013.md](FLAGSHIP_PUBLIC_EVIDENCE_20261013.md).

## Prioritization and explicit completion definition

**Do not claim 3 full L9/L10 flagships today.** These levels are informal aspiration tags, not official graduate admissions tiers.

A single PhD-grade flagship has: **(i)** original, literature-distinct problem or insight; **(ii)** derived algorithm with correctly stated proof/conditions; **(iii)** fully prospective reproducible strong-baseline wins on independent data/task, or a major novel negative scientific finding that changes accepted understanding; **(iv)** human external review or reproducible community adoption; **(v)** transparent full experimental and statistical records.

Aim for 1 complete validated flagship plus 2 incubators, not simultaneous unsupported "fully maximized" claims. This document is a **decision gate**, not its own proof that these accomplishments have occurred.

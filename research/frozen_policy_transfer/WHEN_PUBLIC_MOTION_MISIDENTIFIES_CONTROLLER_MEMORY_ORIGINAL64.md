# The information–authority frontier of stateful robot action histories

*A source-audited negative result and prospective research direction · 9 October 2026 · author-operated genuine ManiSkill CPU PhysX · NOT externally replicated or peer reviewed.*

## Primary result: 64 genuinely new task resets, 640 actually stepped controller worlds

The decisive observation is **not a task-success gain**. On two public pretrained, never-retrained PPO manipulation policies in ManiSkill (PullCube 32 / StackCube 32), both native unknown-ACK events at `t=2,3` are physically held/applied in all four balanced truth combinations per task. Ten actual native controller worlds are stepped for each original reset, with the same pre-decision physical `t2,t3` command prefix, measured achieved+target SE(3) and the same physically stepped known-delivered `t4` neutral probe. At `t5`, two algorithms receive exactly the same **two public achieved-XYZ observation events** and infer a complete target-history hypothesis, or charge one genuine privileged target read. The mandatory-read reference gets the same physical step but has no decision-visible public history input. The original third-party PPO weights, finite hypotheses, empirical response tolerances and 0.95 heuristic threshold were fixed before the first new outcome.

| Original 64 matched-native PhysX outcomes | Task successes | Privileged controller target reads | Public XYZ events (decision-visible) | Confident accepted histories | Confident *wrong* histories |
|---|---:|---:|---:|---:|---:|
| **A. Full set-membership unique-history-or-read** | **52/64** | **48** | **128** | **16** | **1** |
| B. Same-input normalized residual weighting at frozen 0.95 cutoff | 52/64 | 63 | 128 | 1 | 0 |
| C. Fixed t5 true target-memory read | 52/64 | 64 | 0 | n/a | n/a |

**Paired task-success identity:** `52` both succeed, `12` both fail, `0` exclusive successes for A versus C on all 64 original reset states. This is descriptive finite-cohort parity **not a non-inferiority conclusion**. A observes a `16/64=25%` reduction in privileged target getter calls versus C, and `15/63≈23.8%` fewer than B. A and B have the same public observation and physically stepped neutral probe cost. B's residual weights are an UNCALIBRATED heuristic and must NOT be described as a Bayesian posterior certified by data or as ActionShift's actual DualABI; C does not have the same *decision-visible* public XYZ observations.

## Counterexample the task-success metric conceals

**PullCube original reset seed `1760020`, physical `t2=APPLIED`, `t3=APPLIED`:** the complete-history set-membership selector confidently authorized controller-history candidate **index `0`**. The audit-only actual full target pose matches **candidate `3`**. The four original empirical public-response residuals (metres) were `[0.0039247453, 0.0121384608, 0.0245013757, 0.0092696410]`; the residual scoring method declined confident authorization and spent its target-memory query, as did C. **All three treatments nevertheless completed the task.** Hence observed binary task completion **does not certify correct hidden-controller-memory inference**.

The error is recorded verbatim in a SHA-256-pinned first-run original PhysX JSON. We do not retrospectively raise the old 2mm nonwinner margin, alter the empirical response model, drop the seed, or claim this one mistake is hardware danger. Nor does the new full-pose history selector deserve the label *safe* merely because the mistaken history did not cause visible task failure in this episode.

## Statistical calibration is still an open mechanism

Only **16/64** trials received confident public-history authorization from A; **1/16 (6.25%)** of those was wrong. If those selective authorizations were conditionally IID from a stable future test population, the exact one-sided **95% upper confidence bound on the incorrect-history rate is about 26.4%**. The IID/unchanged contact and controller-response assumptions are especially weak in robotics, so even this limited statistical bound is **not** a physical guarantee, and there is no per-task/per-fault reliability proof. B had **0 mistakes on only 1 authorization**; this is not evidence of a superior calibrated detector.

Admissible next mechanism (NOT yet a validated improvement): a target-history *authority supervisor* with three distinct refusal triggers: (i) trusted native action-chart/float32 transport representation and finite hypothesis completeness, (ii) out-of-model public response evidence / empirical calibration invalidity, and (iii) a prospective acceptance-risk threshold set on new state-cluster-disjoint calibration data. Only the first is covered by an established deterministic geometric contract; the second/third require new physical measurement, uncertainty assumptions and genuine held-out task-level effect tests. A speculative new confidence rule tuned on `1760020` may illustrate an idea but **must not be scored on these same 64 states as proof**.

## Comparable information cost, not a disguised performance ranking

Relative to C, A saves **16 privileged target-memory getters** but consumes **128 decision-visible public XYZ sample events**. If each additional XYZ sample costs `c` private-target-getter equivalents, the *read-only* cost advantage disappears for `c ≥ 16/128 = 0.125`. For B the break-even is `c ≥ 1/128 = 0.0078125`. These are algebraic thresholds, **not** measured hardware latency, joules, safety costs or sensor invocation overhead; all arms physically execute the same neutral probe. Differing public samples versus privileged controller target state are not identical sensor privileges, which must be separately priced in a future matched-resource deployment.

## Eight originally prespecified joint-truth strata (each n=8)

| Frozen task / native physical t2→t3 | A successes | A private reads | A confident admissions | Wrong A histories |
|---|---:|---:|---:|---:|
| PullCube HELD→HELD | 8 | 7 | 1 | 0 |
| PullCube HELD→APPLIED | 8 | 5 | 3 | 0 |
| PullCube APPLIED→HELD | 8 | 4 | 4 | 0 |
| PullCube APPLIED→APPLIED | 7 | 5 | 3 | **1** |
| StackCube HELD→HELD | 4 | 8 | 0 | 0 |
| StackCube HELD→APPLIED | 6 | 8 | 0 | 0 |
| StackCube APPLIED→HELD | 4 | 4 | 4 | 0 |
| StackCube APPLIED→APPLIED | 7 | 7 | 1 | 0 |

The StackCube held-first truths and the single PullCube wrong admission show the need for *phase-conditional model falsification*, not simply more confident authorization. No claim of state-independent gains follows from these small fault cells.

## Source, audit and falsification

- **Original full first-run genuine PhysX source and all eight task shards:** [GitHub Actions #37924192162](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924192162). Exact execution head `d378e51006fc44626ab5a651ca1ad2dad5a312e0`, original attempt `1`, all original run jobs successful.
- **Immutable preregistration before this physical outcome:** `research/MATCHED_PUBLIC_BAYES_NEW64_PREOUTCOME_V1.json`, Git object `9c758954f28cd0f3a99480f43828ab2a024c805a`; original unchanged method blob `6e039af56006827fc2fe063b541cfa3dcd1ddc89`.
- **Separate independent zero-GPU source auditor:** [review_matched_public_bayes64_original.py](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/reviewer-bayes64-risk-certificate-20261009/research/review_matched_public_bayes64_original.py) verifies all eight original SHA-256 identities, native model + seed/truth matrix, 64 original physical task results, matched SE(3) prefix, decision-visible public measurement, private read charge and the one wrong confident full history.
- **Two-Python adversarial original source audit CI:** [review original 640 controller worlds](https://github.com/lindicaphxag-tech/ManiSkill/actions/workflows/review-matched-public-bayes64-original.yml). This is a source readback, NOT rerunning the 640 worlds in an independent lab.

**Scientific scope:** one Panda controller family, two public frozen PPOs, known controller chart, simulated native applied/held command fault rather than real lost packet acknowledgements; the artificial known-delivered neutral probe occupies a physical control step. No current general control/safety guarantee, calibrated risk guarantee, official ActionShift DualABI head-to-head, independent external study or top-tier acceptance.

## The next ONE experiment worth funding

Freeze a new state- and task-disjoint train/calibration/test population; fit a transparent public-response model-validity witness using *only calibration physical responses*; preregister an accepted-history mistake-rate upper limit and maximum authorized read cost, then compare (1) the original unchanged 64-state source method, (2) confidence-gated abstention, (3) same-information residual/Bayesian and (4) adapted official DualABI active task-regret protocol. Match the physical probe count, public observations, target-read privilege and true ACK applied/held combinations. A failed calibration coverage test or all-abstain policy **fails the claim** instead of being scored as improved safety. The research contribution would then be a verified **error-vs-observation-cost frontier for latent controller memory authorization**, not rebranding a known SO(3) midpoint theorem.

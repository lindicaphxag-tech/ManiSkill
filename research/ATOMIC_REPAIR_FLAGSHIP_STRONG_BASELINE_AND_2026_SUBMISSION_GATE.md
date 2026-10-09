# Atomic repair commit and accepted-paper comparison: pre-submission adversarial audit

**2026-10-10 research branch. Reviewer-grade STATUS, not an accepted publication.**

## A concrete new TOCTOU defect and its repair

Earlier `FencedAuthority.next()` could return `{request: authorize, repair: ...}` after a fresh state read, but the resulting unreserved repair command could be dispatched **later**. A controller mutation between decision and dispatch invalidates the evidence. The previous command-epoch guard checked the read event, not actual repair publication.

The new [atomic_repair_handoff.py](atomic_repair_handoff.py) binds the conditional repair to a session, model digest, correct decision and exact controller command epoch, then invokes a **single indivisible compare-and-dispatch primitive**. It closes the MODEL LOCAL post-check/pre-publication race when all writes use the trusted versioned backend. Reusing a reservation, tampering with the repair token, a conflicting mutation, and an intervening untracked action all cause refusal.

**Crucial fairness test:** the code contains a deliberately incorrect 'precheck then unconditional send' baseline AND a competent *strong atomic compare-and-swap baseline*. The full deterministic 512-interleaving test has 256 no-interference and 256 injected-interference cases. Both the new wrapper and a proper atomic CAS successfully publish all 256 safe commands and refuse all 256 stale commands; **there is ZERO measured superiority over proper CAS**. The weak precheck commits 256 stale commands. These are not actual robot tasks nor independently sampled sensor faults.

**Actual CI:** https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38004761447. Ubuntu, macOS and Windows × Python 3.11, 3.13 (6/6 jobs), each executes 10 new CAS tests, 11 prior epoch tests and 10 finite-model proof tests, all green. The tests run a TEST-DOUBLE memory controller, not a physical actuator, network or ROS node. The local backend cannot prove genuine device-provided monotonically increasing epochs or trusted delivery receipts.

## Reviewer comparators that set the real bar

| Independent high-impact result | Established achievement | Our current deficit |
|---|---|---|
| [Kim et al., L4DC 2025, *Realizable Continuous-Space Shields for Safe Reinforcement Learning*](https://proceedings.mlr.press/v283/kim25c.html) | Formal guarantees for realizability of continuous-state/action shields, plus actual navigation/multi-agent empirical examples | Only finite symbolic state contract; no continuous robust realizability or physical-task evidence |
| [Tao et al., RSS 2025, *Demonstrating GPU Parallelized Robot Simulation and Rendering for Generalizable Embodied AI with ManiSkill3*](https://www.roboticsproceedings.org/rss21/p021.html) | A complete released ecosystem with diverse manipulation tasks, demonstrations, trained control baselines and measured simulator performance | Only a research fork and scripted controller repairs; no method accepted upstream or used in a new independent group |
| [FlashAttention official original work](https://github.com/Dao-AILab/flash-attention) | Original papers, new practical kernels and independent ecosystem integration | Our wrapper matches a competent CAS baseline; no new end-to-end performance benefit over established methods |

**No officially defined L7/L8/L9 people grades exist.** The labels are planning shorthand. Recognizable L8-style achievement requires a *differentiated method + unbiased benefits on new cases + genuinely independent reproduction*. L9-style impact requires broad independent follow-on work and long-term ownership; test counts and merged-PR counts do not substitute.

## Specific experiment that CAN change the manuscript claim

1. Require trusted actual actuator command epoch counters and evidence about atomic dispatch, prove whether any outside action can bypass the versioned controller wrapper. Without that, software timing guarantees remain conditional.
2. Run a frozen learned manipulation policy or a well-grounded recovery task, with truly ambiguous hidden ACK histories and a mixture of delayed/reordered/missing reads and unobserved controller updates. Frozen experiment registries before new results.
3. Include the **competent CAS baseline**, correct deterministic SE3 analytic compensation, mandatory fresh authoritative read, strong tuned 0.60 passive history scorer, equivalent-actuation static probe and a separately implemented published shielding/adaptation method. Never compare only against the intentionally unsafe precheck ablation.
4. Report task completion, wrong confident repair, true target SE3 error, getter counts, public read cost, wall-clock/controller latency, collision/contact, unmatched source cases and per-independent-reset uncertainty intervals. A publication-quality **positive** effect requires materially better task-level tradeoffs than the competent strong baselines, not just more test cases.
5. Let a non-author run truly independent new seeds/hardware interface and publish their observations. No claim of external acceptance or public paper publication until actually documented.

## 2026 Nov–Dec economical journal submission track (DO NOT claim dates are accepted dates)

**2026-10-10 status:** no independently audited complete Default Regularisation, Two Laws or Rank Budget full manuscript/source package is identified in this GitHub research branch. Paper readiness for EEG is conditional on original files and raw cohort/seed provenance; prior numbers are preliminary, not freshly verified in this round.

| Distinct non-overlapping paper | Preferred first submission target if READY | External category information (not interchangeable) | First reasonable submission window | Hard gate |
|---|---|---|---|---|
| Default Regularisation / EEG regularization mismatch | Biomedical Signal Processing and Control | CAS **2025 original table medicine major category 2** per secondary index; no documented CCF A/B/C listing | 2026-11 if frozen subject-disjoint cohort & calibrated modern baselines revalidate, else 2026-12 or later | Release cohort splits, multi-seed EEG LOSO, leakage and multiple-comparison controls, independent strongest covariance shrinkage/tuning baselines |
| Two Laws / BCI calibration | Journal of Neural Engineering | CAS **2025 original major category 3** per secondary index; **2026 independent 'Xinrui' major category 2 is not the same scheme** | 2026-11/12 if genuinely independent multiple EEG cohort laws stable, otherwise later | Independent cohort law replication, theorem assumptions, stop/calibration cost and subject selection control; official JNE warns that small public dataset classifier gains alone are insufficient |
| Rank Budget / subspace saturation | Neurocomputing | **CCF C** in 2026 AI recommended journals; CAS 2025 major category 2 per secondary index | 2026-12 if subspace claims and out-of-cohort oracle baselines can be verified | Proof and rank-budget calculation, cross-domain target relevance, compare source-vs-domain mixtures |
| Proof-Carrying Patch Review | Empirical Software Engineering | **CCF B** in official recommended software journal list; CAS **2025 major category 2**, 2026 independently defined Xinrui major category 3 (NOT CAS downgrade) | 2027-01+ unless true across-repo method effectiveness/independent acceptance already exists | Real repositories, human study/reviewer labels, false accept/reject, fair modern code review agents, independent validity of proof claims |
| Original robot recovery & contracts merged flagship | Robotics and Autonomous Systems / IEEE RA-L only after proven robot-task benefit | Verify current CAS list at submission; neither venue is an automatic high-acceptance route | NOT a realistic accepted-paper expectation for Nov/Dec 2026 | Public real policy-level control success, correct CAS baseline, cross-controller tests and external replica |

**Timing warning:** At 10 Oct 2026, 2026-11 / -12 dates are credible *submission targets*, NOT assured *acceptance* dates. IOP's JNE journal page quotes median post-peer-review FIRST decision ≈52 days, which is not acceptance. Elsevier's publishing support says editorial metrics vary by journal and are historical; first decision is NOT publication. We must also verify the target university's officially adopted CAS year and verify 2026 CCF directory from the CCF source. Do not turn an uncertain third-party CAS query into a definitive user credential.

References for journal categories / guidance:

- [CCF 2026 seventh official international journals directory](https://www.ccf.org.cn/Academic_Evaluation/By_category/)
- [CCF AI journal list, Neurocomputing](https://www.ccf.org.cn/Academic_Evaluation/AI/)
- [CCF Empirical Software Engineering official category B](https://www.ccf.org.cn/Academic_Evaluation/TCSE_SS_PDL/zgjsjxhtjgjxskw/bl/2017-03-15/587238.shtml)
- [IOP Journal of Neural Engineering metrics](https://doi.org/10.1088/issn.1741-2552)
- [IOP JNE aims and screening criteria](https://publishingsupport.iopscience.iop.org/journals/journal-of-neural-engineering/about-journal-neural-engineering/)
- [Elsevier publication timing definitions and interpretation](https://www.elsevier.support/publishing/answer/when-can-i-expect-a-decision-from-the-editor)
- [Third-party CAS 2025 and separate Xinrui 2026 BSPC](https://www.ablesci.com/journal/detail?id=ZD4KE5), [JNE](https://www.ablesci.com/journal/detail?id=5gbzRp), [ESE](https://www.ablesci.com/journal/detail?id=pLax25), [Neurocomputing](https://www.ablesci.com/journal/detail?id=5mNKeD). Validate official institutional adopted edition before claiming a zone.

## What will cause us NOT to submit

- Any statistically unsupported performance gain or result from reusing development seeds as heldout.
- No independent cohort file or subject-isolation evidence.
- Novelty only from reimplementing standard CAS, finite POMDP dynamic programming or correct SE3 inverse.
- Negative results suppressed or promoted as statistically significant.
- Shared experiments split into overlap-heavy manuscripts, or simultaneous submission of the same paper to multiple venues.

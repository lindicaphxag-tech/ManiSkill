# When Robot Actions Leave No Trace — prospective stronger-control adjudication

**Author-operated, real ManiSkill CPU PhysX, 10 October 2026. FIRST fully source-audited run; new independent reset IDs. Not a peer-reviewed main-conference acceptance, hardware experiment, external-lab replication, or proof of task/safety superiority.**

## Primary claim and pre-outcome identification

The original public-motion full-history rule A appeared to save 20 privileged reads versus a frozen 0.95 residual-weight comparison on 32 reset clusters/128 correlated actual 2×2 ACK cells. But an explicit *retrospective* same-public 0.60 threshold challenge on those **previous** observations showed A 26 admissions/102 reads versus counterfactual B0.60 25 admissions/103 projected reads: hardly a substantial advantage.

To test **truly physically executed** B0.60 rather than extrapolate that offline replay to task success, we committed [the separate pre-outcome register](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/prospective-strong060-128-20261010/research/STRONG060_PROSPECTIVE128_PREOUTCOME_V1.json) and a source-derived runner before any new-seed outcomes. Frozen old PPO checkpoint source, empirical response envelope, candidate-history logic, command chart and matched neutral known-delivered action are unchanged. The only method change relative to the previously frozen physical runner is **B's decision threshold from 0.95 to 0.60**; the same-reset truth control and protocol reference change too. This B threshold was selected with sight of *prior* 301/302 cohort results and is thus prospective on the **311/312 fresh cohort**, not independent of all historical model selection.

The first attempt of the GitHub workflow [#37961672448](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37961672448) **failed its provenance/preflight stage** because the new workflow imported the OLD seed checker; **no physics executed**. This was repaired before observing the new 311/312 outcomes. Second/factual original run [#37961696443](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37961696443) — preflight PASS, four physical simulation shards PASS, independent source/paired-prefix audit PASS, run attempt 1. **All early failures are retained.**

## Factual same-initial-state, 2×2 ACK-physical first-run data

**32 actual independent initial reset IDs**: PullCube 3110001–3110016 and StackCube 3120001–3120016. Each repeated across all four t2/t3 held/applied physical execution truth patterns; each condition actually stepped **ten** native frozen-PPO/controller arms = 128 task/ACK conditions, 1,280 genuine author-operated simulator worlds. The same initial public state SHA, physically applied native t2/t3 commands, achieved EE pose, hidden commanded-target full SE(3) and physical t4 neutral probe are checked **BEFORE** the t5 information choice for A/B/C. Audit-only target reads are excluded from decision-input privileges.

| Actually stepped method | Same-condition official task successes | Real privileged target getters | Extra decision-visible public XYZ samples | Correctly admitted full target histories | Observed wrong labels |
|---|---:|---:|---:|---:|---:|
| A: full-history public set-membership or getter | **109/128** | **94** | 256 | 34 | 0 |
| B: same-public residual score **0.60** or getter | **109/128** | **98** | 256 | 30 | 0 |
| C: fixed true target getter | **110/128** | **128** | 0 | n/a | n/a |

**A and B succeeded on exactly the same 109 actual task/ACK conditions** (and both failed the same 19). Fixed C rescued **one extra StackCube condition**, not an A-vs-B method difference. Task family stratification:

| Task | A success/reads | B success/reads | C success/reads |
|---|---|---|---|
| PullCube, 64 correlated cells / 16 resets | 62 / 43 | 62 / 47 | 62 / 64 |
| StackCube, 64 correlated cells / 16 resets | 47 / 51 | 47 / 51 | 48 / 64 |

**Strong comparator result is unfavorable to a breakthrough-superiority claim.** With identical probe and public-sensing budgets, A saves **4 actual getter calls** versus B across 128 fault conditions. Pairwise history authority: **28 both authorize, 6 A-only, 2 B-only, 92 neither**. Whole-reset task-stratified bootstrap of the 32 independent reset clusters gives a **descriptive 95% interval of [-1, 9] total A-over-B getter calls**, and two-sided exact **whole-reset sign-flip p=0.2890625 (exploratory)**. A’s observed four-read advantage is **not statistically persuasive** in this sample. Strong B was not a calibrated probabilistic posterior or official ActionShift DualABI.

A saved 34 actual private getters relative to C, but at a cost of 256 extra decision-visible public XYZ measurements. In *hypothetical target-read-equivalent units*, if each additional XYZ event costs >34/256=**0.1328125** target-getter equivalents, the reported gross read advantage disappears (not counting any other potentially unequal costs). No actual measured latency, contact risk, energy or real hardware utility ratio is available.

## Non-IID risk and restricted identifiability

A admitted 34 actual conditions from **22 separate task/reset clusters** (Pull 14, Stack 8); B admitted 30 from **21 separate reset clusters** (Pull 12, Stack 9). No wrong confident histories were observed. Under a restrictive cluster-IID/exchangeable accepted-resets model, the **one-sided 95% Clopper–Pearson upper** for *at least one wrong authorization across four ACK truths of a fresh admitting reset* is **~12.73%** for A (0/22) and **~13.29%** for B (0/21). This is NOT the per-authorized-event error rate or real-robot safety bound. Treating 34 or 30 accepted events as IID would be invalid.

A *separate* genuine PhysX study had three factual paired public-XYZ-and-neutral-probe observation collisions with different native commanded target full poses. That is a constructive non-identifiability witness **for the specific stated public observation/neutral probe only**; it does not rule out a better nonzero probe, added sensing or a privileged getter.

## Evidence hierarchy / reproducibility

1. [**Complete, permanent first-run raw archive**](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/prospective-strong060-128-20261010/research/frozen_policy_transfer/evidence/strong060_prospective_original128_first_3110001_3120016) — 16 original eight-reset PhysX JSONs, 16 shard audits, four same-reset truth ledgers, four full terminal logs, environment freeze, byte-preserving SHA256 and recomputed aggregate; permanence independently [confirmed by archival CI #37962665869](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37962665869).
2. [Original truly physical 1280-world prospective run #37961696443](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37961696443) — all four physical tasks and full audit passed. It is AUTHOR-operated despite the internal module name “independent source audit.”
3. [**Cross-platform original-source statistical audit #37963099003**](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37963099003) — Python 3.11/3.13 on Linux, Windows, macOS. The audit recomputes full original raw SHA and prefix gates; tests risk units, grouped four-truth outcomes, paired decisions, wrong-authority integrity and exact 32-reset inference. This re-verifies existing data only; **not third-party independently run physics**.
4. [Reviewer-facing original-source code and tests](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/reviewer-audit-strong060-20261010/research) — `review_strong060_cluster_risk.py` and [adversarial tests](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/reviewer-audit-strong060-20261010/tests/test_strong060_source_cluster_risk.py).

The earlier 301/302 physical run has a **different 0.95 actual comparator** and a posthoc 0.60 offline reanalysis. They must remain separate cohorts and should **not** be naively pooled as equivalent pre-registered A/B0.60 trials.

## Publication and external-adoption gates

**Current support:** a narrow controller-memory observational collision/falsifier; source-audited original public-information/state-getter trade-off; fully physical matched strong-scoring controls, explicit negative and counterevidence. Novelty *of a generally dominant active controller adaptation method* is **not established**.

**Missing to reach a credible main-conference method claim:**

1. A distinctly **nonzero action-conditioned probe** under precisely matched public sensing and physical actuation costs, with a response-model uncertainty guarantee calibrated on disjoint **actual native PhysX** data; track realized task regret and contact/unsafe motion.
2. Strong same-information active and passive baselines, including an honestly ported ActionShift-compatible comparison if its intervention/info assumptions can be reconciled, not a relabeled normalized-weight heuristic.
3. A second task-competent learned policy/robot-controller family, genuinely distinct from Panda-source frozen PPO, with proper action-frame semantics rather than a claimed unverified VLA transfer.
4. Unaffiliated external operator-run fresh native source and limitations/counterexamples, not simply consuming the author's GitHub Actions logs.
5. Adequate error-risk power: even 0/22 admitting reset clusters leaves ~12.7% one-sided 95% upper bound on the restricted group-level conditional risk. Claims of <5% would require a substantially larger, appropriately selected independent population and a genuine frozen evaluation design.

**Decision:** continue as a research flagship, but **do not claim L8/L9 external adoption, top-conference acceptance, statistically significant four-read superiority, or hardware-safety certification** on this evidence alone. Freeze and preserve the negative result rather than tune until favorable.

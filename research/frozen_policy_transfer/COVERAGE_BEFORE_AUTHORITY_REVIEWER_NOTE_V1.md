# Why a unique execution history is not a safety certificate
## Coverage before authority: a falsifiable mathematical boundary and real PhysX counterexample

**9 October 2026 · reviewer note · no new originality claim for set membership or split conformal coverage.**

This is a mathematical interpretation of **original PhysX sources**, and a design constraint for the separately preregistered 64-case posthoc-trained dual-criterion experiment. It is not a theorem that the current empirical controller is safe.

### 1. Define the question correctly

Let H be the unknown *actual* native commanded-target history from an ambiguous ACK sequence. Let Y be the publicly observed achieved-pose/motion evidence after a physically stepped neutral action. Define an observation-feasible set

\[
C_\epsilon(Y)=\{h\in\mathcal H:r_h(Y)\le \epsilon\}
\]

with task-frozen achieved-XYZ segment residual r_h. This residual is defined with an unknown scalar response gain alpha in [0,1]; no claim is made that the actual robot physics obeys the model under contact or controller shift. A unique-history selector accepts only if |C_\epsilon(Y)|=1 and nonwinners exceed the independently fixed two-millimeter gap.

**Set uniqueness is about predictions conditional on the model. Validity asks whether the model admits the true physical state.** These are logically distinct conditions.

### 2. Elementary coverage-to-wrong-authority implication

Let A be the selector's event "authorize a unique candidate", and W the event "the selected history is not the actual one". Every wrong authorization necessarily excluded the true history from the feasible set:

\[
W\cap A\subseteq\{H\notin C_\epsilon(Y)\}.
\]

Thus, under a population distribution for which one has a genuine marginal coverage statement

\[
P(H\in C_\epsilon(Y))\ge 1-\delta,
\]

one obtains **only** the unconditional bound

\[
P(W\cap A)\le \delta.
\]

The conditional wrong-authority probability obeys the weaker inequality

\[
P(W\mid A)\le\min\{1,\delta/P(A)\},
\]

provided P(A)>0. A nominal 95% *marginal coverage* statement and P(A)=0.25 therefore permit a conditional error rate as large as 20% under this bound. This is not a safety certificate on the admitted 25%.

If the response model lacks justified future-sample coverage, even the first inequality's numerical delta cannot be asserted.

### 3. Physical falsifier that task success alone conceals

[Actually executed source, all task/fault failures and original SHA256](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/matched-public-bayes-native16-20261009/research/frozen_policy_transfer/evidence/matched_same_public_bayes_original64_1760001_1770032) and [source-only immutable 1760020 verification CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37925148881):

- Frozen released PullCube PPO, original reset seed 1760020, t2 applied AND t3 applied. Same physical controller command/achieved SE(3) prefix in the full-history, fixed-read and same-public score comparator.
- Public unique-history selector admitted history index 0; audit-only actual commanded-target register identified index 3 as true. The wrong target was 0.06763037 m / 0.05358308 rad away from actual.
- Wrong candidate segment residual 0.0039247453 m was inside frozen epsilon 0.0069442626 m; true candidate residual 0.0092696410 m was outside that tolerance. Thus C_epsilon(Y) held the wrong candidate and excluded the physical truth.
- Official actual frozen PPO task success was TRUE for the wrong-authority arm AND for the private-reading arms. Official task success is not sufficient to verify latent control-state correctness.

The 64-state experiment had 16 public unique full histories and **one observed wrong confidence**, or 1/16=6.25% on these selected author-run simulations. No iid independence, hardware deployment shift or confident-error probability guarantee is inferred from that proportion.

### 4. Why a calibration-only fix remained inconclusive

A [separately source-precommitted real 64-state, 640-PhysX-world coverage-calibration study](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924240294) enlarged StackCube's response tolerance using an old independent target-residual calibration sample of n=32. Compared with the prior narrow tolerance on new seeds, the widened tolerance achieved 58/64 identical official successes, 53 rather than 51 private reads, 11 rather than 13 public authorizations; both versions saw zero confidently incorrect history identities in that new study.

For an independent exchangeable n=32 calibration residual sample, a maximal order statistic has nominal next-example marginal coverage of 32/33, **not a conditional-on-acceptance safety guarantee**. Pooling tasks, stateful control phases or shifted domains destroys even that exchangeability condition. At n=8 per each joint ACK stratum, the corresponding maximal-order coverage is only 8/9 conditional on a genuinely exchangeable stratum.

A calibrated epsilon by itself cannot distinguish an off-model future observation that deceptively fits an incorrect target and excludes the true one. The new sample contained no erroneous permissions in *either* variant, so it did not demonstrate a reliability improvement.

### 5. Current 0.65 dual-criterion experiment: honest status

The [new untouched 64-state before-outcome protocol](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/dual-evidence-public-authority-new64-20261009/research/DUAL_EVIDENCE_ACK_NEW64_PREOUTCOME_V1.json) declares a **posthoc development-chosen** threshold: exact unique feasible complete history AND normalized historical residual-score weight at least 0.65. Source training diagnostics on the **OLD 176/177 reset cohort** found 10/16 previous admitted candidates above this floor with zero old wrong labels; this threshold was chosen **after seeing** the wrong 1760020 evidence. Those old outcomes are not a prospective test and must be reported as model development, not validation.

The two criteria are **correlated functions of the same public XYZ samples and the same empirical motion model**. This is *not* an independent physical evidence sensor, calibrated posterior or correctness certificate. At best a completely disjoint 182/183 prospective source trial can test an empirical authorization-risk/query-cost tradeoff, retaining all task failures and confident wrong identities. A truly substantial reliability improvement would need independent, out-of-domain, explicitly calibrated motion validity evidence or a genuinely informative extra sensor/probe, with total resource costs audited.

### 6. Research acceptance conditions

Do not publish this as "safe controller recovery" unless a real prospective validation supports a declared target error-risk notion and its assumptions. The source data currently support a deeper negative problem: **a robot can achieve its assigned task while the adapter has confidently installed the wrong hidden native controller target, because the true physical response is outside the model's feasible set**.

External ActionShift/DualABI and older active identification literature should be acknowledged rather than rebranded as a newly invented belief principle. Third-party replication, a second actual robot-controller family, actual transport faults and a faithful matched-resource baseline remain mandatory external-validity gates.

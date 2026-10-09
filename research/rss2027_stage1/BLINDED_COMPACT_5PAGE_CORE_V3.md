# Observability Is Not Authority:
## Falsifying Hidden Command-History Recovery in Stateful Robot Controllers

**Anonymous RSS 2027 Stage-1 scientific body — compact 5-page-layout candidate v3. Not a typeset/submitted PDF. Do not include author identities, links or supplementary evidence.**

### Abstract

A robot may know its requested action but not whether a stateful controller executed it. With two missing acknowledgements, four complete commanded-target histories can remain possible despite a known action interface. We ask when a public motion response warrants authorizing one hidden history rather than reading the controller's private target. Using frozen published manipulation policies and genuine native PhysX control, we demonstrate selective read economy under a matched physical prefix and common downstream compiler. Yet a tuned same-public-information competitor eliminates almost all of the apparent advantage, and a robot may complete its task while confidently misidentifying the controller's target memory. A new fully crossed 16-seed/four-fault experiment controls initial public policy observations and illustrates both promising task outcomes and their statistical uncertainty. Additional physical tests show that reweighting the same residual and validating response dynamics at an earlier time fail to establish trustworthy present-time authority. We specify a prospective, **regime-conditional decision-critical probe** that selects bounded actions for their actual ability to separate full target histories and queries whenever response-model support is insufficient. Its task benefits remain unverified. The scientific distinction is between a history that appears observable *under a model* and a history that is sufficiently supported to control the robot.

### 1. Failure mode and research question

A frozen robot policy often emits an end-effector delta while a deployed target-relative controller accumulates displacements from its *previous commanded target*, not the achieved end-effector pose. An executed command whose acknowledgement is lost modifies this hidden memory; a held command does not. The policy can therefore resume from the wrong target state even when the native action tensor remains well typed.

The key issue is not merely poor task success. Our physics experiments contain a confident wrong execution-history identification in an episode that nevertheless satisfies the official manipulation success predicate. Reward cannot validate hidden-controller-state truth. Equally, observed query reduction relative to mandatory readback is not evidence of method superiority when a stronger, previously tuned classifier receives the same public observations.

Prior work on action-contract adaptation, notably ActionShift [1], already develops structured belief and active probing. We do not claim invention of those ideas. We isolate an orthogonal mechanism: **the action chart is verified, but the actual executed/held history under missing acknowledgements is not**. The hypothesis is that reliable authorization requires *both* candidate separation *and* evidence that the response model is valid at the decision time. Neither is guaranteed by a softmax confidence number.

### 2. Complete target histories and distinguishability

Let \(M_t\in SE(3)\) be the private last *commanded* target; \(X_t\in SE(3)\) the publicly achieved pose; \(u_t\) the requested native action under a verified chart \(F\); and \(z_t\in\{0,1\}\) the hidden applied/held truth:

\[
M_{t+1}=\begin{cases}
F(M_t,u_t) & z_t=1,\\ M_t & z_t=0.
\end{cases}
\tag{1}
\]

After two missing acknowledgements the belief contains at most four complete SE(3) histories, preserving original orientation and physical delivery sequence together. It is invalid to replace target \(M_t\) with achieved pose \(X_t\), or to combine position and rotation taken from incompatible histories.

An adapter may observe a bounded known-delivered public probe, uniquely select one candidate, read the authoritative target, or abstain. Its information ledger records each public sensor sample, physical probe, private controller read, elapsed delay and refusal separately. The evaluator alone sees injected physical truth. Given two equally likely latent histories with public transcript distributions \(P_0,P_1\), a classic two-point testing argument yields

\[
P(\widehat H\ne H,\widehat H\ne\bot)+\tfrac12P(\widehat H=\bot)
\geq\tfrac12[1-\operatorname{TV}(P_0,P_1)].
\tag{2}
\]

This is established statistical theory, not a new robotic safety theorem. It establishes the limit: when public observation laws overlap, correct identification without a state read cannot be universally assured. More critically, nonoverlap of *estimated* response tubes does not imply nonoverlap of the actual dynamics after contact or controller-gain shifts.

### 3. Existing physically executed controls

We use two published frozen pretrained PPO policies on actual ManiSkill CPU PhysX [2] PullCube and StackCube tasks, with physically applied or zero-held native target-controller actions at two known fault instants. Native task success and every command/read/failure are retained, with no policy training.

**Table 1 — distinct physical cohorts (never pooled). Each “64” is 64 task/reset conditions, not 64 × controller arms as independent test cases.**

| Source-registered physically stepped experiment | Official task successes | Private controller-target reads |
|---|---|---|
| Same predecision native physical prefix **and same postdecision compiler**: complete-history evidence/query | **53/64** | **48** |
| Same original fixed-target-reader comparator | **53/64** | 64 |
| Strong *same-XYZ* prospective source: complete-history evidence/query | **59/64** | **52** |
| Same real public samples: previously tuned 0.60 residual-score-only/query | **59/64** | 53 |
| **Serial same-initial-input 2×2 ACK factorial**: complete-history evidence/query | **57/64** | **47** |
| Exactly same 64 seed/fault cells: task-conditioned strong comparator | **54/64** | 61 |

The most rigorous new factorial executes every held/held, applied/held, held/applied and applied/applied truth on **16 original source-seed clusters**, with 576 actual PhysX controller worlds. The four physically simulated truths for each source seed are run serially in the same task process, with declared RNG reinitialization. An independent full-population auditor finds **16/16 source clusters with exactly identical initial frozen-PPO observation SHA256**. Across 64 cells, the paired outcomes comprise 53 jointly successful, four public-only, one strong-only and six jointly failed tasks. Task successes are **57/64 versus 54/64**, but a 16-seed-cluster sign-swap sensitivity test gives \(p=0.25\): **no established statistically significant task-success superiority**. The public method performs 47 private reads versus 61 for the strong comparator; extra public XYZ observations have not been converted to an equivalent privileged-read price. Input identity is not a proof of equality of every unobserved simulator state.

This changed experimental protocol is necessary. An earlier same-integer-seed factorial physically executed 128 source/fault cells and 1,152 controller worlds, but **7/32 StackCube seed groups produced different initial public policy-observation hashes across fault truths**. That original full matched-causal gate failed; its original task outcomes were retained and not rebranded as exact source-matched counterfactual evidence. The new serial-source result is a *separate* prospective study.

### 4. Falsifiers: the apparent history is not necessarily true

The first falsifier is **incorrect latent authority despite task completion**. A distinct equal-public-sensor study recorded at least one confidently wrong target history for the original set-membership method; another real study confirmed that the false belief need not prevent a successful manipulation. Consequently, a one-bit official success rate cannot replace an independent false-authority metric.

Second, a “second confidence score” computed deterministically from exactly the same public XYZ residuals is **not another physical observation**: for \(W=g(R)\), \(I(H;R,W)=I(H;R)\). In a separate 64-reset, 640-world prospective comparison, adding a previously frozen 0.65 residual-score gate preserved official task success at 54/64 and observed false-authority at zero for both arms, but increased controller reads **41→45**. Two original early-terminated episodes did not obtain complete public probes; their task outcomes stayed in the full 64-trial denominator. The extra gate has no measured benefit in that original population.

Third, response validation is **not temporally transferable without assumptions**. In genuine Panda joint-drive-shift physics, an earlier known-delivered action's response-model support test missed four of eight later invalid response states and falsely flagged 30 of 56 valid cases. The resulting observer requested more private reads without improving task success. Likewise, simply repeating a correlated neutral public observation failed to improve official task success in another source-registered cohort.

These negative results narrow the scientific target: we must obtain *decision-time physical evidence* whose information is not merely a deterministic re-expression of already observed position residuals.

### 5. Prospective regime-conditional authority

We propose **Regime-Conditional Authority (RCA)** to select a known-delivered, chart-verified bounded probe only when its expected public response can separate the competing *complete pose histories* under the current set of plausible response regimes. Let \(\widehat Y_{h,r}(v)\) and \(U_{h,r}(v)\) denote a frozen predicted public response and a response uncertainty set for history \(h\), physical regime \(r\) and allowed native probe \(v\). Candidate selection maximizes the worst-case pairwise separation across histories *and* plausible regimes, penalizing measured public/actuation costs:

\[
D(v)=\min_{h\ne h',\,r,r'}\!
\left[d(\widehat Y_{h,r}(v),\widehat Y_{h',r'}(v))
-\operatorname{rad}U_{h,r}(v)-\operatorname{rad}U_{h',r'}(v)\right].
\tag{3}
\]

A probe is admissible only if its original native chart and target-setpoint bounds hold across all histories. At actual execution, it must be confirmed as delivered, fresh, and supported by the frozen *current-regime* model. Public achieved SO(3), temporal motion and contact information may be added only if genuinely measured and charged. If no probe can separate candidates, or if the actual observation fits zero/multiple candidate histories, RCA performs a counted private read rather than making an unsupported latent claim.

A source-only implementation verifies these logic invariants, including SO(3) quaternion double-cover, unknown response regime overlap, unsupported dynamics, stale data, unconfirmed delivery and missing public measurements. **This is software correctness evidence only**: the public-response tubes have not been shown calibrated for the proposed shifted real-physics task settings, and neither task recovery advantage nor hardware force/collision safety has been demonstrated.

**Registered falsification conditions for Stage 2.** Freeze true-history calibration on independent physically stepped seeds; prospectively run new source-verified four-truth native fault clusters and changed contact/gain settings; compare RCA to the previously tuned same-public score, public set membership, fixed/private and an actually equal-budget active probe. Report selective wrong-authority risk *and* nontrivial per-task authorization coverage with valid confidence bounds. The test fails if actual public SO(3)/temporal evidence adds no useful separability, if the response regime cannot be validated at decision time, or if abstention/read costs erase the benefit. The study also requires original-source-hash repeatability and an outside investigator choosing new reset states, neither of which can be replaced by author-controlled CI.

**Scope.** These studies are simulated Panda task-level PPO experiments, not real packet loss or physical hardware safety tests. A genuine task-tuned frozen VLA separately closes the loop on original LIBERO MuJoCo tasks, but its achieved-pose-relative robosuite controller does not instantiate the same accumulated-target recurrence; no VLA target-history recovery is asserted. The contribution sought is a falsifiable **observability-versus-authority boundary**, with task-level algorithmic promotion dependent on the prospective physical tests above.

---

## References — place on the separate Stage-1 reference page

[1] K. Attri, *ActionShift: A Benchmark for Hidden Compositional Action-Interface Adaptation in Manipulation*, preprint, DOI 10.31224/7688 (2026).

[2] S. Tao, F. Xiang, A. Shukla, Y. Qin, et al., *ManiSkill3: GPU Parallelized Robotics Simulation and Rendering for Generalizable Embodied AI*, arXiv:2410.00425 (2024).

[3] A. N. Angelopoulos and S. Bates, *Conformal Prediction: A Gentle Introduction*, Foundations and Trends in Machine Learning 16(4), 494–591 (2023), DOI 10.1561/2200000101.

[4] A. van der Vaart, *Asymptotic Statistics*, Cambridge University Press (1998).

**Editorial status:** Scientific content is blinded and source-grounded, but this Markdown is not the official RSS 2027 LaTeX template or a verified six-page PDF. RSS 2027 Stage 1 permits up to five pages of scientific content plus one page of references (deadline December 4, 2026 AoE). The official template must be used without modifying its style; final pages, fonts, references, anonymization and the actual PDF have not yet been checked or submitted.

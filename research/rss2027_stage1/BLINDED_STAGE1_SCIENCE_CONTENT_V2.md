# Observability Is Not Authority:
## Identifying Hidden Command Histories in Stateful Robot Controllers

**RSS 2027 Stage-1 extended-abstract CONTENT v2. Authors omitted.**  
**IMPORTANT:** This Markdown file is NOT yet an RSS-template PDF and has NOT been verified to fit exactly five pages of content plus one page of references. This blinded draft deliberately contains **no GitHub links, lab identity, authorship, acknowledgments, or identifiable source paths**. Submission-ready page limits, embedded fonts and anonymity must be separately validated using the official template.

### Abstract

After a robot control command loses its execution acknowledgement, a frozen manipulation policy may know what it requested but not whether a stateful controller changed its hidden target memory. This creates uncertainty in *execution history*, even when the controller's action convention is known. We ask a more specific question than whether the robot completes its task: **when does public motion evidence justify selecting one particular hidden command history, rather than requesting an authoritative controller-state read?** We formalize a complete SE(3) target-history belief and a selective public-evidence-or-query decision. Real frozen-policy ManiSkill PhysX studies establish this question experimentally. In a prospective, genuinely same-initial-input four-truth design (16 seed clusters, 64 executed fault conditions, 576 native controller worlds), the public-history method completes 57/64 tasks with 47 private reads versus 54/64 and 61 for a task-aware comparator; the observed task gap is not statistically significant at seed-cluster level. A separate identical-prefix/common-compiler comparison yields 53/64 versus 53/64 tasks with 48 versus 64 reads. However, an equally public-sensed, previously tuned score competitor closes almost the entire read-cost gap (52 versus 53 reads, 59/64 task successes each), and separate studies exhibit confidently incorrect target-state identification despite successful task completion. A physically altered controller-response experiment further shows that an earlier valid-response witness cannot establish the validity of a later observation model. We propose a testable **decision-critical, regime-aware probing** protocol that attempts to distinguish both candidate histories and model misspecification, while abstaining if this is physically impossible. Its reliability and task-level gains are hypotheses for prospective evaluation, not current experimental results. Our central finding is that **public observability under an assumed model is not evidence that the model is trustworthy enough to authorize action**.

### 1. Introduction: the robot can finish and still be wrong

A manipulation policy outputs a motion command, but the actual controller often retains a previous commanded goal. The physically achieved end-effector pose can lag behind that goal. Consequently, if a command is executed but its acknowledgement is lost, the policy and controller can disagree about the controller's memory without any syntax error or change in the action-vector dimensions. A second unacknowledged command compounds this ambiguity.

The immediate temptation is to treat the robot's measured end-effector motion as an observation of hidden controller memory. Our original real-physics controls refute the unrestricted version of this idea. A robot can finish a manipulation task while its adapter confidently selects the wrong hidden target history. A method can also reduce privileged controller reads in a comparison to mandatory readback, then lose virtually all of that advantage against an independently tuned same-public-information classifier.

These two facts suggest a more challenging research question: **What information makes a hidden command history legitimately actionable?** A useful method must distinguish (i) plausible target histories under the assumed model, (ii) whether the model still explains the present physical response, and (iii) whether a choice is permitted under the controller's actual action and safety constraints. We deliberately do not equate success on one task with correctness of a latent state, and do not call geometrically bounded target commands a collision- or force-safe system.

ActionShift [1] already studies unknown hidden action-interface contracts and active probing with structured beliefs. Online dynamics identification also has substantial prior art. Our problem does not attempt to relearn an unknown action frame, permutation or scale. We restrict attention to a verified stateful target-relative native action chart and uncertain *executed-versus-held* command events. The distinctions are the causal source of hidden memory, the observability of complete histories, and the cost of safely spending authoritative state reads when the public response model may not apply.

**Contributions established or proposed are separated.** The established empirical contribution is a source-authenticated, physically stepped, falsification-oriented study of execution-history observability and false confident authorizations on fixed pretrained manipulation policies. The theoretical statement is an application of classical indistinguishability and selective-abstention principles, not a new mathematical bound. The proposed algorithmic contribution—regime-aware decision-critical probing—is a hypothesis to be verified under registered source and shift conditions.

### 2. Problem: two ambiguous receipts, four complete target histories

Let \(u_t\) be a native action expressed under an independently verified chart \(F\), \(M_t\in SE(3)\) the controller's hidden **last commanded target**, \(X_t\in SE(3)\) the publicly achieved tool pose, and \(z_t\in\{0,1\}\) the actual executed/held command event. The native target evolves as

\[
M_{t+1} =
\begin{cases}
F(M_t,u_t), & z_t=1,\\
M_t, & z_t=0.
\end{cases}
\tag{1}
\]

An absent ACK does not reveal \(z_t\); the policy observes only its intended command and available physical measurements. Two consecutive missing ACKs induce up to four **complete** latent target histories \(\mathcal H_t\). A candidate stores the complete position, orientation, causal delivery sequence and verified controller-chart provenance. Neither substituting \(X_t\) for \(M_t\) nor independently mixing coordinates from different candidates is permissible.

At the decision point the adapter may (a) choose a history from its belief, (b) perform a known-delivered publicly observable native probe that consumes physical action and sensing budget, (c) read the actual private controller target, or (d) refuse. We distinguish *query count*, *public sensor samples*, *native extra probe steps*, *additional physical displacement/delay*, *task success*, *wrong confident latent history* and *no authorization/abstention*. The evaluator alone has access to injected execution truths and native controller targets for auditing.

For two possible histories \(h_0,h_1\) with equal priors, let their public-response distributions under a specified probing strategy be \(P_0,P_1\). The classical binary-testing bound, after converting abstention to a random guess, gives

\[
P(\widehat H\neq H,\widehat H\neq\bot)
+\frac{1}{2}P(\widehat H=\bot)
\geq \frac{1-\operatorname{TV}(P_0,P_1)}{2}.
\tag{2}
\]

This does not invent a new bound. It clarifies the correct question: if distinct actual histories induce overlapping publicly observable responses, any deterministic no-query identification rule must trade false admission against abstention. With an *estimated* response model, apparent nonoverlap does not certify physical identifiability if the response model itself is invalid.

### 3. Baseline system and authentic physical evidence

The test bed uses two publicly released frozen PPO manipulation checkpoints, PullCube and StackCube, in actual ManiSkill CPU PhysX [2]. The source policy weights are not updated. Each destination controller is configured to use known target-relative native actions. At two specific steps, the intended native arm command is either actually applied or physically replaced by a zero-hold action while the adapter receives the same ambiguous ACK. All cases retain official task-success signals, actual native action records, early refusal and explicit private-read accounting.

**Table 1. Separate physically executed source cohorts. The 64 cases within one cohort are task/reset trials; physically stepped simulator worlds are not independent learning test samples. Do not pool independent experiments into a single success rate.**

| Study: methods and physical comparison | Official successes | Privileged target reads | What is established |
|---|---|---|---|
| **Serial same-initial-input four ACK truths; 16 new seed clusters × 4**: public history | **57/64** | **47** | Same observed initial PPO input under all 4 true executions; task advantage statistically unproven |
| Matched physical factorial task-aware comparator | **54/64** | **61** | Comparator in precisely the same 64 seed-truth conditions |
| Matched command prefix **and common post-query compiler**: public complete-history-or-read | 53/64 | 48 | Conditional query savings |
| Same physical comparator: mandatory native target read | 53/64 | 64 | Strong equal-controller source baseline |
| Newly held-out **strong same-XYZ**: public full-history-or-read | 59/64 | 52 | No large advantage remains |
| Exact same public XYZ/matched physics: prior-data-tuned residual score only | 59/64 | 53 | Stronger challenger, one-read difference |
| Same source cohort's mandatory target reader | 59/64 | 64 | Upper-information but unequal-budget comparator |

**More rigorous original four-condition evidence.** An earlier prospective 32-seed/128-condition experiment executed all 1,152 PhysX controller worlds but failed its preregistered physical initialization audit: 7 of the 32 same-number StackCube seed blocks produced differing exact initial policy-observation hashes across the four physical ACK executions. This failed paired claim was preserved and audited; none of its mismatched blocks was silently classified as causal evidence. A redesigned 16-seed study then executed all four actual conditions **serially within each task process**, with explicit RNG reinitialization, actual t2/t3 native dispatch and the same frozen PPO/controller source. The independent raw-source auditor verified **16/16 exactly matched initial policy-observation hashes**, all 64 original fault conditions and 576 actually stepped control worlds. Whole-history selection completed **57/64** tasks with **47** counted private reads, versus task-conditioned comparator **54/64** tasks and **61** reads, with 53 both successes, 4 public-only and 1 comparator-only. All 64 public episodes physically encountered both command events; 128 original public XYZ sampling events were charged. No wrong confident history was observed *within this cohort*. The exploratory two-sided 16-seed-cluster swap test is **p=0.25**, and its cluster bootstrap includes zero; it does not establish a task-success advantage. Exact matching of the observed initial PPO tensor is a necessary source integrity check, but cannot alone certify equality of all unobserved simulator state.

A separate genuine new 64-trial comparison against an ACK-specific probabilistic-shaped score recorded **one wrong confident hidden history** for the original public rule and one lower task completion, despite materially fewer private reads. In another authentic trial a robot **succeeded while the selected hidden target history was wrong**. Therefore official manipulation completion cannot substitute for native hidden-state correctness.

Two seemingly reasonable reliability patches also fail prospective physical tests. Reusing the same XYZ response through an extra frozen confidence weight is deterministic postprocessing, not independent corroboration: in one fully preserved 64-reset, 640-world experiment, the additional 0.65 rule yielded 54/64 tasks with 45 reads versus 54/64 tasks with 41 reads using the original rule; no wrong admission was observed in either arm on that particular population. Two early-terminated task trials never obtained the required full public probe transcript; both remain in the 64-trial intention-to-treat denominator. A second correlated passive probe also provided no task-success gain and consumed additional private reads in another cohort.

Under truly altered Panda joint-drive gains, a preceding *known-delivered* command's public response was not an adequate certificate for subsequent response-model validity. The prospective original physics showed missed current-model failures alongside many false alarms. A rule that validates the model at time \(t_1\) cannot silently assume that its calibration remains valid at \(t_4\).

### 4. Proposed method: a decision-critical public witness

We propose **Regime-Conditional Authority (RCA)** as a *prospective* next method, rather than relabeling existing results as proof of an untested algorithm. The core difference from a static residual threshold is that the adapter asks *which physically feasible probe would actually separate the remaining hypotheses under the current plausible response regimes?*

Given a candidate known-delivered, bounded native probe \(v\), let \(\widehat Y_{h,r}(v)\) be the expected **public** response under complete history \(h\) and response regime \(r\) (e.g., contact/free-motion and tested controller gain), and \(U_{h,r}(v)\) an uncertainty set calibrated on physically separate source states. Unlike the current position-only selector, the response transcript may include measured \(SE(3)\) tool orientation, temporal motion and measured contact cues, if actually available and charged. Define a conservative separation criterion

\[
D(v)=\min_{\substack{h\ne h'\\r,r'\in\mathcal R_t}}
\operatorname{dist}\!\left(
\widehat Y_{h,r}(v),\widehat Y_{h',r'}(v)
\right)
-\operatorname{rad}(U_{h,r}(v))
-\operatorname{rad}(U_{h',r'}(v)).
\tag{3}
\]

This is an optimization criterion, **not a proof of physical separation** unless the uncertainty sets are genuinely valid for the current regimes. Feasible \(v\) must satisfy an explicit command-setpoint bound for *every* currently plausible complete history and a separately logged actuation budget. The adapter may choose a low-cost \(v\) that improves conservative separation; if no suitable action exists, it immediately reads the controller state or refuses rather than manufacture certainty.

The corresponding **model-support test** must be evaluated on post-fault, contemporaneous public evidence. Calibration data and test data must be disjoint. The current-mode response must lie inside a support region validated under matching physical regimes before a unique candidate can be authorized. If any candidate remains ambiguous, the response is unsupported, the model's current regime cannot be established, or a controller command would leave the verified native action chart, the adapter abstains and performs a counted authoritative read. This fail-closed behavior is not necessarily efficient; it must be evaluated jointly with task performance and real information cost.

For a fixed exchangeable calibration population, a standard split-conformal candidate set with unique-set authorization gives a *marginal* bound on wrong **and** authorized events, not on error **conditioned on authorization**. Task-stratified selective risk and nontrivial minimum authorization coverage therefore require a separate risk–coverage protocol. A classifier that always queries and hence observes zero false confident admissions cannot be declared successful. None of the stated probabilistic guarantees automatically holds under unmeasured response-regime shift; none certifies contact forces or hardware safety.

### 5. Registered evaluation, decisive falsifiers and implications

**Prospective task/condition design.** Use never-inspected frozen-policy reset states and actually execute all four (held/held, applied/held, held/applied, applied/applied) physical ACK truths **on a demonstrably matched initial physical state**, not merely on the same integer seed. Original full-population source audit must verify the initial raw state/observation identity, or report failure rather than silently excluding mismatched clusters. Analyse by original source-seed cluster rather than treating four counterfactual conditions as four independent samples. Preserve task-level successes/failures even if a fault or probe is not reached; report physical exposure separately.

**Calibration and model validity.** Identify source-regime calibration examples with authoritative *audit-only* true histories; freeze uncertainty scores, current-regime support tests, action budget, fallback policy and evaluation thresholds before observing test outcomes. At test time the adapter must not consult oracle histories or native target reads except when that information access is explicitly charged. Evaluate held-out changes in controller gain, contact and measurement noise, plus histories with identical XYZ but potentially different rotation. A causal test must show which *additional physically measured* information changes false authorization; softmax reweighting of the same residual is a necessary negative control.

**Essential matched-budget baselines.** Compare always-read and never-read floors, the original whole-history set selector, a properly tuned same-XYZ residual-score competitor, the same public evidence with no model-support test, a random/fixed probe using the same native actuation budget, and a relevant active-belief observer within **identical** public channels and controller-target permissions. ActionShift's DualABI [1] is related prior work, not automatically a comparable implementation of the execution-ACK fault: either port the true ACK dimension and run a genuine equal-budget comparator or label the comparison precisely as a task-specific custom method.

**Primary promotion criterion.** On independent new physical test conditions, lower false confident *complete-history* authorization at a prespecified task-stratified selective-risk confidence target while maintaining nonzero useful authorization coverage and a defensible task-success/read/sensing/actuation frontier against the tuned same-public-information competitor. Report number of accepted histories, wrong admissions, all forced reads, timed refusals, official success, sensor/actuation/delay and any pre-fault missing exposure by task and true physical condition. Include an exact counterexample if RCA fails. This proposal is falsified if the new sensor channel adds no history information, if model validity cannot be established in the shifted regime, or if the resulting fallback rate makes RCA no better than the strong private-reader baseline.

**Scope.** Current results involve an author-operated simulated Panda stateful target-relative controller and two externally trained frozen PPO task policies. Additional target-memory tests on other arms do not establish frozen-policy task transfer. Genuine pretrained SmolVLA has completed original native LIBERO tasks, but that robosuite controller updates its position goal from the achieved pose; its action-chart mechanism is therefore not equivalent to the one studied here. No VLA fault-recovery or hardware safety result is claimed. Independent outside-investigator seed selection, raw-source execution and a scientifically meaningful additional controller/task setting remain necessary extensions.

The central proposition for the two-stage review is deliberately falsifiable: **more public motion data is not equivalent to justified action authority; the relevant missing capability is to test whether physical history hypotheses are distinguishable *under a response model still valid at decision time*.** A negative result that exposes a principled observability boundary is informative, but successful methodological claims require the stronger prospective controls above.

---

## References (intended for the separate Stage-1 reference page; formatting not finalized)

[1] K. Attri. *ActionShift: A Benchmark for Hidden Compositional Action-Interface Adaptation in Manipulation.* Preprint (2026), DOI: 10.31224/7688.

[2] S. Tao, F. Xiang, A. Shukla, Y. Qin, et al. *ManiSkill3: GPU Parallelized Robotics Simulation and Rendering for Generalizable Embodied AI.* arXiv:2410.00425 (2024).

[3] A. N. Angelopoulos and S. Bates. *Conformal Prediction: A Gentle Introduction.* Foundations and Trends in Machine Learning, 16(4), 494–591 (2023), DOI: 10.1561/2200000101.

[4] A. van der Vaart. *Asymptotic Statistics.* Cambridge University Press (1998). Classical two-point hypothesis testing and total variation are invoked as prior mathematical foundations, not claimed new.

**Stage-1 compliance and review note:** RSS 2027 explicitly restricts Stage 1 to **at most five pages of content plus one page of references**, with no reviewed supplementary evidence or external websites. A separate PDF layout pass is mandatory before submission. The December 4, 2026 deadline and two-stage shepherding format should be checked against the official live CFP at the time of actual upload. This file has NOT been submitted.

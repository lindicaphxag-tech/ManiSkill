# When Motion Lies: Execution-History Identification under Ambiguous Robot Command Acknowledgements

**Research manuscript v1.6 · 9 October 2026 · prospective failure included; NOT peer reviewed, accepted or third-party replicated**

**Zhibo Zhang** · Hangzhou Dianzi University, China · 24061721@hdu.edu.cn

*Contributor authorship, collaborators and disclosures must be confirmed before formal submission.*

## Abstract

A frozen manipulation policy may issue semantically invalid actions after a robot controller accumulates commands relative to its previous target rather than the achieved end-effector pose. When an execution acknowledgement is missing, the robot's internal commanded target becomes a latent discrete history, rather than a known value. We study when ordinary achieved motion can identify a complete target-pose history without obtaining privileged controller memory. The adapter maintains up to four acknowledged/held native-command histories and uses empirically calibrated public-motion response sets to admit exactly one complete history or to request an explicit target-state read. In an earlier new-seed, two-fault experiment with a balanced first command execution truth but a held second command, the method preserved 58/64 frozen PPO task successes with 31 privileged reads versus 58/64 with 58 reads for a task-selected strong comparator. However, that setup fixed the second acknowledgement truth. We therefore prospectively registered four actual joint applied/held combinations of two uncertain commands, executed 64 distinct PullCube/StackCube states across 576 genuine ManiSkill PhysX policy-controller worlds, and forced one common known-delivered neutral probe before deciding. The original simulator outputs, retrospectively rechecked by an **independent source-only audit** after a technical in-job audit error, show 58/64 actual task successes and 46 privileged reads versus 57/64 and 62 reads for the strong task-selected baseline. Critically, **2 of 18 publicly authorized complete histories were wrong**. Both failures occurred in StackCube's held-then-applied cohort: the true native target's observed public-motion residual exceeded the historical response tolerance while a different latent history fit. Thus observed task success and query reduction **did not imply evidence reliability**. We formalize that limitation and pre-register, without claiming an outcome yet, an unchanged-policy two-consecutive-known-probe test on genuinely new seeds. The work supports a falsifiable target-history/evidence-authorization problem, not a universal zero-error observer, noninferiority claim or hardware safety guarantee.

**Keywords:** robot learning; controller memory; latent execution history; public proprioception; model misspecification; ambiguous acknowledgement; selective state query; falsifiable experiment.

---

## 1. What is actually uncertain?

An achieved-relative policy action and a remembered-target-relative controller command are not semantically interchangeable. Let \(M_t\) be the controller's native commanded target (full SE(3)), \(u_t\) a legal native command and \(z_t\in\{0,1\}\) the unobserved fact of physical command execution. With known native chart \(F\),

\[
M_{t+1} =
\begin{cases}
F(M_t,u_t), & z_t=1,\\
M_t, & z_t=0.
\end{cases}
\]

Two uncertain acknowledgements create up to four complete candidate histories. The source frozen PPO never retrains; it needs actions translated and authorized in the destination controller's native frame and rotational action constraints. An unknown receipt is **not** proof of execution or non-execution, and a successful task is **not** proof that the adapter inferred the correct hidden target.

The research question is narrower than discovering an unknown action interface: if the destination ABI is known but execution events are uncertain, when may low-cost public achieved motion replace the expensive hidden target-state getter?

## 2. Observation-set rule and its nontrivial assumption

For a known delivered neutral target-delta probe, let \(x\) and \(y\) be public achieved end-effector XYZ immediately before and after the physical action. Given candidate complete native target \(M_i\), the previously calibrated response model predicts

\[
y = x + \alpha(M_i^{xyz}-x)+e,\qquad
\alpha\in[0,1],\quad \|e\|_2\le\epsilon_\mathrm{task}.
\]

For each history, calculate the residual \(r_i\) to its predicted public XYZ segment. Authorize its complete SE(3) pose only if there is exactly one candidate \(i^*\) with \(r_{i^*}\le\epsilon\), and all others have residual strictly greater than \(\epsilon+0.002\)m. Unlike an unsound all-rotations-identical criterion, this is selection of a **discrete full-pose hypothesis** by its distinguishing public position evidence; it does not estimate unconstrained orientation from XYZ. If positions are observationally aliased, the method must read the authoritative target or refuse.

These finite set-membership conditions are standard. Their use on robot-commanded target histories is the engineering object studied; **they provide no safety certificate unless the response envelope is a genuine bound on the physical system**. Here the envelope is empirical, from other simulation states, not independently attested. An unmodeled robot/contact response can make the true history appear incompatible with the sensor evidence.

The source tolerances were fixed at PullCube \(\epsilon=0.0069443\)m and StackCube \(\epsilon=0.0071909\)m. No newly observed test residual was used to change these bounds.

## 3. Experiment A: authentic mixed first ACK, held second ACK

A pre-outcome study on PullCube seeds 860001–860032 and StackCube 870001–870032 physically applied the first unknown command for half the states and held it for half. The second fault remained a forced native target hold, used directly as the observed response step. In 576 paired real PhysX control worlds (64 resets × nine different actual controllers), full-history public identification recovered **58/64** official frozen-PPO task successes with **31 private target reads**. The preselected task-labelled selective/fixed read controller completed **58/64** with **58 reads**. A trivial zero-read always-assume-held controller managed **43/64**, dropping to **1/16** on StackCube states with a physically applied first fault. Public evidence authorized 33 histories with no observed wrong labels.

These results are [fully archived, with negative trials and original byte digests](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/mixed-ack-truth-frozenppo-new64-20261009/research/frozen_policy_transfer/evidence/mixed_ack_truth_frozen_ppo_original64_860001_870032). Pairwise private-read source deltas were positive for the public method on 30 states, negative on three and tied on 31, with an exploratory unadjusted exact sign p≈1.4e-6. This is **not** a formal multi-task guarantee, and no task-success noninferiority margin was preregistered.

**Crucial missing intervention:** the second actual fault was always held. A method optimized for that physics regime may not handle both true execution events.

## 4. Experiment B: genuinely four joint execution truths, known-delivered probe

The [pre-outcome joint-truth protocol](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/all-four-ack-truths-active-probe-20261009/research/ALL_FOUR_ACK_JOINT_TRUTH_PPO_NEW64_PREOUTCOME_V1.json) froze all new PullCube states 880001–880032 and StackCube states 890001–890032 before execution. Actual t2 and t3 ACK truths were determined solely by predeclared seed moduli, yielding exactly eight of AA, AH, HA and HH per task. Both receipts stayed unknown to the adapter. At t4 an additional **known-delivered** physically stepped native zero-delta was applied to every *still-active* controller, with an explicit two-public-XYZ-sample cost for the public observer. This is NOT the same intervention/cost as Experiment A, so numbers must not be pooled.

Each reset instantiated nine separately stepped native-policy controller environments: original source, privately informed oracle, optimistic ACK guess, exact/refuse, bounded no-query, selective bound/query, fixed target readback after probe, zero-read always-held history and empirical public-history identify/query. The original frozen released third-party PPO checkpoints were SHA verified. The study covers one Panda controller family in genuine ManiSkill CPU PhysX, NOT network packet loss or robot hardware.

The [FIRST original physical run](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37917629944) **failed its own audit after recording eight complete eight-state physical source JSONs** because an erroneous auditor required a strict controller that refused at t3 to keep running until t4. The originals were NOT replaced with a favorable re-run. A [separate successful source-only audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37918333602) collected all eight unmodified original physical shards from distinct artifacts, checked all 64 original seed/truth combinations, allowed documented early refusals without fabricating t4 steps, and permanently archived [every raw source JSON, whole-population audit and SHA256SUMS](../evidence/four_joint_truths_first_physx64_880001_890032/).

### Original physically stepped outcome, all trials retained

| Physically realized 2-ACK truth | Public method task success | Preselected strong task-aware query |
|---|---:|---:|
| AA: both native commands applied (16) | 16 | 14 |
| AH: first applied, second held (16) | 15 | 15 |
| HA: first held, second applied (16) | 15 | 16 |
| HH: both held (16) | 12 | 12 |
| **All registered 64** | **58** | **57** |

Original private decision reads were **46 vs 62**, respectively. Fixed t5 readback completed **57/64** with 64 reads; zero-read always-held succeeded in **36/64**. The main measured tradeoff therefore remained plausible, but it is conditional on the fitted observation model.

**The serious counterexample:** Only 18 original physically stepped states were publicly uniquely classified; **two of these classifications selected the WRONG complete native target history**. Both cases were pre-outcome StackCube **890005 and 890017** (HA: first held, second applied). The target-history audit getter was used exclusively after real physical probe execution, not as the online classifier's input.

- Seed 890005: true history candidate index 2 had residual **0.0095276m**, exceeding the frozen StackCube threshold 0.0071909m; incorrect candidate 3 had residual **0.0057471m** and was uniquely accepted. The final task was nevertheless marked successful, illustrating why task success cannot validate state inference.
- Seed 890017: true candidate 2 residual **0.0106125m**; incorrect candidate 3 residual **0.0069776m** was uniquely accepted. In this state the public method failed the final task while the strong target-read comparator succeeded.

Both errors violate the assumption that the TRUE history always lies in the empirical observation set. Increasing statistical coverage without modeling contact, actuation phase and observation noise cannot turn an empirical envelope into a deterministic controller target certificate. Conversely, choosing a larger threshold only after seeing these failures would constitute test-set overfitting.

### Audit interpretation

The 64 source states do not constitute 64 independent policies or robot systems. The original physical CI status is **failure**, the independent recovered source-only audit is **success**, and the byte-identical original physical result is **neither a second experiment nor independently operated scientific replication**. Early-refuse controls did not execute extra neutral steps and were never credited for missing steps.

The experiment provides useful negative evidence: as the realized execution truth becomes more diverse, simply demanding one compatible motion segment risks **false confidence under response-model misspecification**.

## 5. Experiment C: independently precommitted temporal evidence — prospective, outcome NOT reported yet

The [new two-probe protocol](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/sequential-two-probe-full-joint-20261009/research/SEQUENTIAL_TWO_PUBLIC_PROBES_NEW64_PREOUTCOME_V1.json) was frozen **after** observing the two error cases, on *different* initial states: PullCube 900001–900032 and StackCube 910001–910032. Both actual ACKs again span AA/AH/HA/HH. Every still-active comparator receives two actual known-delivered neutral native actions at **t4 and t5**, not one. Original source and published PPOs remain unchanged; only evidence timing and model combination differ. Strong task-preselected query and separately physically stepped first-probe-only witnesses receive the same additional two-step actuation schedule. The single-probe method uses two extra public XYZ samples; the joint-probe method explicitly consumes **four** (two independent before/after pairs).

For each candidate complete target history \(i\), let \(r_{i,4}\) and \(r_{i,5}\) be its residual under the same previous task-specific response model to the two physical public-motion steps. The new rule selects \(i^*\) only if it is compatible in **both** intervals and every other history violates the frozen exclusion margin in at least one interval:

\[
r_{i^*,4}\le\epsilon,\quad r_{i^*,5}\le\epsilon,
\qquad
\forall j\neq i^*: r_{j,4}>\epsilon+0.002\ \lor\ r_{j,5}>\epsilon+0.002.
\]

Otherwise, make exactly one authoritative target getter read at t6 or refuse if unavailable. This does not prove conditional independence of errors: two correlated wrong predictions can still be consistently wrong. The goal is to **try to falsify** the hypothesis that a second public observation reduces confidently incorrect target-history identification at an acceptable information and actuation cost, on data not used to choose this rule.

The [new original test workflow](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37919075616) is intended to run **64 untouched reset states × 10 real PhysX controllers = 640 native controller worlds**, including an actually stepped first-only controller. It MUST complete its original whole-population source audit before any claim of efficacy, superiority or lower wrong-confidence rate can be made.

## 6. Novelty, comparison and reviewer challenges

This study does not invent belief propagation, set-membership identification, observation-selection or calibrated abstention. Related [ActionShift](https://github.com/Archerkattri/actionshift) and [ActionABI](https://github.com/Archerkattri/actionabi) work already explores active action-interface probing and honest refusal. The empirically separable research object is **latent realized command execution under otherwise known native target-memory semantics**, including the exact point where a public evidence source can and cannot justify native control. Novelty at top-conference level will require comparisons under **matched public sensing, probe actuation and privileged reads**, independent reproduction and evidence across controller/robot embodiments, not merely a larger number of self-owned merged PRs.

Critical reviewer questions answered incompletely here include whether the t4/t5 neutral probes reduce actual robot success by consuming control time, whether correlated model errors survive sequential probes, whether prior task-specific gain envelopes generalize across contact regimes, and whether a stronger history-aware policy could infer as much with fewer sensor samples. Real hardware torque/collision/contact safety, unknown native action charts, VLA policies, actual delayed or lost network acknowledgements and independent outside-lab adoption are outside the current evidence.

**Scientific conclusion at v1.6:** demonstrated task-level information-cost reductions from public-motion target-history inference are real in these source-audited PhysX cohorts, but diverse actual ACK execution truths expose nonzero confidently wrong actions. The stronger flagship contribution is the precisely testable problem of *evidence authorization under model misspecification*, not an unconditional low-query or certified-safe adaptation claim.

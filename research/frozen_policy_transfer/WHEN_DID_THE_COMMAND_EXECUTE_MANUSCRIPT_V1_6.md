# When Did the Command Execute?
## When Public Motion Can—and Cannot—Authorize Latent Target Histories in Frozen Robot Policies

**Manuscript v1.6 — 9 October 2026 — original, unreviewed research draft; includes both positive and negative actual native PhysX tests**

**Zhibo Zhang**  
Hangzhou Dianzi University, Hangzhou, China  
Correspondence: 24061721@hdu.edu.cn

*This manuscript is not peer-reviewed, not accepted, and not a statement of independently verified hardware safety. Confirm coauthors and permissions before public submission.*

### Abstract

A frozen robot policy's end-effector deltas can become semantically invalid when the destination controller composes native commands from its *last commanded target* rather than from the achieved pose. Two missing execution acknowledgements induce up to four plausible target memories, even when the interface chart is documented. We examine whether publicly achieved motion, rather than a privileged native target getter, can uniquely identify an entire six-dimensional controller-target history. A finite-history adapter propagates all physically admissible execution branches and accepts a public response witness only if exactly one complete history matches a previously calibrated empirical motion model; otherwise it performs one counted target read. In a prospectively registered first-mixed-ACK, second-held ManiSkill/PhysX cohort, two unchanged third-party frozen PPOs completed **58/64 tasks with 31 privileged target reads**, compared with **58/64 and 58 reads** for a precommitted task-dependent query rule; an actually stepped zero-read always-held shortcut completed **43/64**. We then prospectively randomized BOTH physical ACK truths (AA/AH/HA/HH), revealing an essential failure: **2 incorrect confident full-history authorizations among 18 public selections**, despite **58/64 observed task successes and 46 private reads**. Two consecutive neutral public-motion probes were subsequently tested on an entirely NEW 64-state cohort, with the same two additional native actions for both one- and two-observation policies. **Both completed 48/64 actual tasks; the two-probe gate made 21 public authorizations and 43 private reads versus 23 and 41 for the one-probe gate, and neither exhibited an incorrect confident authorization on this new bank.** The paired negative result shows that repeating a correlated empirical sensor model does not, by itself, demonstrate more reliable execution-state recovery. These physically stepped findings narrow the engineering claim to **conditional information efficiency under a known controller interface and a potentially fallible response model**. They do not establish model-validity certification, task noninferiority, genuine lost-network-packet handling, robot safety, outside-laboratory adoption, or a learned VLA.

**Keywords:** frozen robot policy; unknown acknowledgement; controller target memory; selective authoritative readback; model misspecification; finite-hypothesis observation; PhysX; calibration reliability.

---

### 1. Introduction

A policy trained to command end-effector deltas relative to the *achieved* pose may be deployed into a controller that instead accumulates deltas relative to the *previous commanded target*. The policy receives a plausible action space and observations, but the meaning of an action depends on controller memory invisible to the source model. A missed or ambiguous execution acknowledgement compounds this mismatch: the adapter knows what it requested, yet cannot assume the request modified native controller memory.

The relevant state is neither simply the policy observation nor the issued action. Let x_t denote the achieved pose, M_t the native controller's remembered target pose, u_t a native command, and z_t an unobserved binary execution indicator. For a documented target-transition operator F,

- M_(t+1) = F(M_t,u_t) when z_t = 1 (applied);
- M_(t+1) = M_t when z_t = 0 (held).

A missing receipt is not evidence for either outcome. After two unknown receipts, there can be up to four distinct target histories. The challenge is to obtain sufficient evidence to select a legally representable native action without requiring complete continuous access to a privileged target getter.

**Research question.** Given a documented controller chart, a known initial target, two ambiguous executions, and ordinary public achieved motion, when can a frozen policy resume from a uniquely supported complete target-history hypothesis rather than performing an authoritative read?

We deliberately separate three claims: (i) native action admission (typed frame, BOX translation, SO(3) rotation unit BALL), (ii) latent *commanded-target* history identification, and (iii) official task completion. None of them implies collision avoidance, motor safety, contact-force guarantees, or another claim without separate evidence.

#### Contributions and boundary of originality

The contributions are an explicit execution-history inference-and-readback contract embedded in true frozen-policy control; a task-level experimental study of the cost of hidden state evidence; and a prospective adversarial evaluation that invalidates the trivial "all ACKs were held" shortcut. Finite set-membership reasoning, abstention, and active system identification are pre-existing concepts. Related projects including [ActionShift](https://github.com/Archerkattri/actionshift) and [ActionABI](https://github.com/Archerkattri/actionabi) study hidden action-interface contracts and their identification; our narrower object is the *realized execution event* under an otherwise known interface. No general first-use or SOTA claim is made.

### 2. Method

#### 2.1. Target-memory belief

At each uncertain ACK, propagate all physically admissible outcomes through the documented native target recurrence, retaining a set H_t = {M_t^(1), …, M_t^(K)} of **complete SE(3) target-pose hypotheses**. Every candidate contains the target XYZ and quaternion produced by an explicit previous action/ACK history. An unobserved ACK never collapses the belief; identical histories may be deduplicated only under declared numerical tolerance. The two-fault experiments generate up to four candidate target poses.

The source frozen PPO continues to produce achieved-relative actions. The adapter translates them into legal normalized native target-delta actions only when a complete target is selected or the same bounded command can be admitted across the candidate set. The native controller mapping is assumed documented: the work does **not** learn an arbitrary new action chart.

#### 2.2. Public response evidence

At the second prescribed native target-hold event, the native arm action is zero while the physical controller continues toward its remembered target. Let x and y be measured public achieved end-effector XYZ before and after this genuine simulator step. Under a previously calibrated—but **not independently certified**—response model, candidate i predicts

    y = x + alpha (M_i^xyz - x) + e,
    alpha in [0,1], ||e||_2 <= epsilon_task.

For each complete candidate i, calculate r_i, the minimum Euclidean residual to the segment spanned by its predicted public response under alpha in [0,1]. The historical tolerances used for all reported new trials were frozen at epsilon_Pull = 0.0069442626 m and epsilon_Stack = 0.0071908797 m, based on older, disjoint calibration states. We do not re-estimate them from any new cohort.

The authorization rule is:

- Exactly one candidate i has r_i <= epsilon_task;
- For every competing candidate j, r_j > epsilon_task + 0.002 m;
- The known native action chart and the complete history-provenance preconditions remain valid.

Crucially, this selects **one entire SE(3) target-history candidate**; it does not require all competing histories to have the same quaternion. Public XYZ is not being used to estimate an arbitrary orientation continuously. The target orientation is retrieved *from the unique discrete history hypothesis* when the position response distinguishes that history. If two distinct full-pose histories produce indistinguishable XYZ response sets, unique identification is impossible under the declared measurement model.

A unique fit is therefore a **conditional compatibility witness**, not an externally certified physical target guarantee. If multiple histories fit, none fits, or the model/chart preconditions fail, the adapter makes an explicitly counted authoritative target-state read at the predefined step four and resets its target-history belief. The controller's hidden target is *never* read as a decision input in a publicly identified case; all post-step getters used to judge inference correctness are marked audit-only.

#### 2.3. Information and action costs

The proposed method consumes two extra *public achieved XYZ samples* per tested episode at the existing second-fault time; it adds no additional actuated probe step. A strong comparator can instead read the controller's private remembered target explicitly. Hence our reported efficiency benefit concerns **privileged target-state reads**, not all sensor access, full computational latency, total bandwidth or probe-displacement Pareto optimality.

### 3. Experimental design and integrity

We use two released, unchanged third-party PPO backbones for ManiSkill PullCube-v1 and StackCube-v1. The source action interface is achieved-relative pd_ee_delta_pose, while the destination Panda arm controller is persistent-target-relative pd_ee_target_delta_pose. Models, training seeds, original policy checkpoints and source identities are frozen. Original action translation follows the verified destination translation BOX and native SO(3) rotation constraints. All task outcomes are actual official simulator success flags, not success inferred from commanded-target reconstruction.

**Primary mixed-truth trial:** [pre-outcome protocol](../MIXED_ACK_TRUTH_PPO_NEW64_PREOUTCOME_V1.json), immutable original protocol Git blob 039868da753f6fc37217036ed632bf6dca953228. Before execution, the protocol fixed 32 fresh PullCube states 860001–860032 and 32 fresh StackCube states 870001–870032. At step two, an even-numbered source seed physically executes the intended native arm action; an odd-numbered seed physically replaces it with a zero action. Thus each task has 16 physically applied and 16 physically held first actions. The adapter does **not** receive the seed-parity truth. The second nominal unknown ACK is held in all worlds, providing the same native zero-delta public response sample for comparison; this is not a full four-combination intervention.

Nine controller-policy methods are independently stepped from each original seed: the unchanged source reference, continuous privileged oracle, optimistic assume-applied, strict exact-or-refuse, bounded no-query, geometric selective read, fixed authoritative t4 read, the new public identify-or-read method, and a deliberate zero-read **always-assume-held** target-history observer. Nine actual worlds per seed times 64 original states yielded 576 real SAPIEN/PhysX controller episodes, all source-audited and preserved, not 576 independently learned robots.

The strong *task-preselected* comparator was frozen before any primary trial: the previously developed bounded/query policy for PullCube, and fixed early target readback for StackCube. Its candidate whole-world trajectories were actually executed from the same seeds; no counterfactual outcome splicing or after-result best-of selection was used. All outcomes, wrong confident history selections, refusals, physical delivery truths, target-read counts and failure-to-inject cases remain in the source denominator.

**Physical provenance:** [original 10-job real PhysX execution + independent source audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37915263314). [Original 17-file SHA256-bound source archive](./evidence/mixed_ack_truth_frozen_ppo_original64_860001_870032/). The separate [cryptographically checked archival workflow](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37916032672) verifies the original-producing commit, untouched artifact ZIP digest and recomputed full-population results.

### 4. Results

#### 4.1. Main original mixed-truth task-level outcome

| Independently physically executed comparator | Official task successes /64 | Decision-time private target-state reads |
| --- | ---: | ---: |
| **Full-history public identify-or-one-read** | **58** | **31** |
| **Task-preselected strong selective/fixed query** | **58** | **58** |
| Fixed authoritative target read at step four | 59 | 64 |
| Geometric selective query | 56 | 48 |
| **Always assume both ACKs were held (zero reads)** | **43** | **0** |
| Bounded no-read history-robust policy | 11 | 0 |

Relative to the strong task-aware opponent, the new method made **27 fewer private target reads out of 58** (46.6% fewer), with the **same aggregate task-success count**. The true paired episode table is **57 both-success, 5 neither, 1 new-only and 1 strong-only**; thus the experiment does not show task-success superiority or statistical noninferiority. Fixed readback completed one more task (59 versus 58) using 33 additional privileged reads. The result is an observed information-cost tradeoff, not a free performance improvement on every metric.

The public method identified **33 of 64** candidate complete target histories from ordinary achieved XYZ and issued one counted private read in the remaining 31. No incorrect confident identification was observed among the 33 authorizations, as checked exclusively against *post-physical-step, audit-only* native target truth. A zero observed error count on 33 accepted states must not be interpreted as a certified zero-error probability.

#### 4.2. Disaggregated actual execution truth

| Task and physically realized first ACK | New method: successes | Task-selected strong: successes | Zero-read always-held: successes | New reads | Strong reads |
| --- | ---: | ---: | ---: | ---: | ---: |
| PullCube · APPLIED (16 states) | 16 | 15 | 15 | 4 | 12 |
| PullCube · HELD (16) | 16 | 16 | 16 | 10 | 14 |
| StackCube · APPLIED (16) | 15 | 15 | **1** | 9 | 16 |
| StackCube · HELD (16) | 11 | 12 | 11 | 8 | 16 |
| **All 64** | **58** | **58** | **43** | **31** | **58** |

The zero-read always-held shortcut fails sharply in the StackCube physically-applied stratum (1/16), while the public-or-query method completes 15/16. This *controlled subgroup observation* is an important explanation for how the mixed-truth experiment differs from the previous deterministic all-held injection—not a separately powered statistical superiority claim.

Publicly unique full-history selections were 12/16 (Pull applied), 6/16 (Pull held), 7/16 (Stack applied) and 8/16 (Stack held). No confident wrong index was observed in any stratum. All 64 new-controller trials reached their intended two nominal ACK events, and the actual first applied/held actuator commands and the second physical hold were checked in the original source.

#### 4.3. Why the negative evidence matters

Two earlier independent cohorts constrain interpretation, rather than being pooled into this result:

1. In a prospective **32-state** double-ACK frozen PPO experiment, a mistakenly over-restrictive rule also demanded that all hypothetical target orientations agree before public XYZ could select a history. It authorized **0/32** public histories, completing **24/32** tasks using **32 reads**, while the task-preselected comparator attained **24/32 using 26 reads**. The original negative source and all failed trials remain archived: [old32 evidence](./evidence/public_fourhistory_frozen_ppo_original32_780001_790016/).
2. After a retrospective, *outcome-exposed* diagnostic of those first 32 states indicated that 12 complete-hypothesis indexes could have been uniquely selected (without actually re-executing a repaired controller), a **different prospectively registered 64-state** experiment established the new rule on the fully HELD/HELD fault pattern. It completed **58/64 using 39 reads** versus a strong task-aware baseline **58/64 using 57**, but was susceptible to the always-held generator shortcut: [prior new64 full source](./evidence/discrete_hypothesis_ppo_original64_840001_850032/).
3. The **new 64-state mixed-truth study** above was frozen only after recognizing that shortcut and before implementing/testing the additional always-held native controller arm. It is independently seeded relative to the two previous cohorts and is the main result, not a disguised retune of their test states.

#### 4.4. Physically mixing BOTH unknown ACK truths exposes false evidential authority

The earlier 64-state *first-mixed, second-held* study had a possible generator shortcut: the second execution was always HELD, and a zero-action probe was assumed known. We next preregistered a genuinely distinct 64-state real PhysX cohort with **both** native commands at steps 2 and 3 independently physically either APPLIED or HELD under a deterministic balanced seed mapping. Each task received eight new resets in every combination (AA/AH/HA/HH). All still-active policy controllers physically executed a separate **known-delivered neutral t4 arm action** and only then considered public evidence or explicit privileged target read at t5. This has a distinct motion and opportunity cost from the earlier mixed-first study.

The [original run](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37917629944) **was reported by GitHub Actions as FAILED** after the native PhysX episode sources had been generated, because the original in-shard auditor incorrectly demanded a t4 probe from the strict-exact comparator that had legitimately refused at t3. We preserved that failed producer state and performed a [successful independent source-only re-audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37918333602) without rerunning, replacing or relabeling the physical episodes. The full source with every failed comparator was permanently frozen with individual SHA-256 hashes: [genuine original 4-combination evidence](../evidence/four_joint_truths_first_physx64_880001_890032/).

| Genuine four-execution-truth source cohort | Real task successes | Private state reads |
| --- | ---: | ---: |
| Single public full-history witness or authoritative query | **58/64** | **46** |
| Preregistered task-ID-selected strong query | 57/64 | 62 |
| Fixed authoritative target read | 57/64 | 64 |
| Always-assume-held (zero-read shortcut) | 36/64 | 0 |

The source independent auditor counted **18/64** confident empirical full-history authorizations, but **two were demonstrably WRONG** against the private native target read **after** actual physical execution. They occurred for *StackCube HA* at seeds **890005 and 890017**. The true history was candidate index 2, yet the empirical public model incorrectly selected candidate 3. In both cases the actual history's residual fell **outside** the frozen empirical response envelope while a false hypothesis fell inside. One incorrect confident label accompanied a task failure; the other still reached official task success. Thus observing task completion cannot validate the correctness of a proposed latent execution state or any implicit physical safety certificate.

This is evidence for *distribution-dependent dynamics-model miscoverage*, not a proof that the entire class of public observers is impossible. We make no claim that the empirically fitted ε values were externally mechanically calibrated upper error bounds.

#### 4.5. Prospective two-probe repair hypothesis FAILS to improve frozen PPO results

In response to those **outcome-exposed** errors, we preregistered a *new* 64-reset bank (PullCube 900001–900032; StackCube 910001–910032) and compared the same frozen policy under ten separately actually stepped controllers per reset, **640 original native PhysX controller worlds**. Both the single-observation and double-observation variants executed the exact same two *known-delivered native zero target-delta steps* at t4 and t5; single used only the first public XYZ displacement for an empirical candidate witness, double required both consecutive motions to jointly support the **same complete history** before skipping an authoritative t6 readback. The second public measurement is an explicitly charged extra sensing cost and arises along a correlated trajectory. No outcome-informed retuning was allowed.

The [full original source-producing workflow and independent all64 audit succeeded](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37921282989), and the [original 17-file source/sha256 archive](../evidence/dual_probe_vs_single_physx_original64_900001_910032/) is independently reverified by [permanent archival CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37922026474).

| Prospective SAME seed, SAME native actuation cost | Single public t4 | Double public t4+t5 |
| --- | ---: | ---: |
| Actual frozen PPO official task successes | **48/64** | **48/64** |
| Privileged native target reads | **41** | 43 |
| Public complete-history authorizations | **23** | 21 |
| Public achieved XYZ samples | **128** | 256 |
| Confidently wrong native history labels | 0 | 0 |

The success/failure labels for the two methods were identical on all 64 states (48 both successful; 16 both unsuccessful). The two-probe witness consumed **two more** private state reads and **128 extra** achieved XYZ measurements than the single-probe witness without increasing task success. It must be reported as a **negative method comparison**. Zero observed wrong-confident labels in this new cohort is not a demonstration of lower error probability because *both methods* had zero. The new task bank's overall success is also not directly comparable to previous cohorts: the actual reset seeds differ and each original frozen policy incurred TWO mandatory additional neutral steps.

The most informative scientific interpretation is **evidence-authority calibration**: no finite set of observations from an *unvalidated empirical response envelope* can be treated as a guaranteed safety certificate, even when a selective information-cost policy performs well on a given task population. The next legitimate advance needs a separately established model-validity check across changes in contact phase, robot/controller dynamics or sensor behavior—and a prospective heldout test of whether that check rejects false public authorizations before they affect the policy.

### 5. Statistical interpretation and threats to validity

The comparison is **paired** by original reset seed and true fault timing. There are only two PPOs, two manipulation tasks and one destination Panda controller family in one PhysX engine. Sixty-four states are not 64 independent robot embodiments or policies, and two task strata do not establish broad distributional transfer. With one novel-method-only and one strong-only success, the binary outcome comparison gives no meaningful evidence of a success-rate advantage. A formal noninferiority claim would require an a priori margin and adequate statistical power that this research did not pre-register.

The measured cost is the number of target-state getter accesses **for decisions**, not post-run audit getters, public XYZ samples, total sensor bandwidth or computation. The empirical response-envelope bounds come from a small, distinct previous calibration population; they are neither independent mechanical contracts nor tested under arbitrary contact loads, unmodeled delays, sensor noise, true ROS transport failure, physical collisions or hardware. **The first receipt's physical execution truth was balanced; the second still had a fixed held truth.** No conclusion is made for four mixed APPLIED/HELD joint histories, unknown native action semantics, unconstrained SO(3) tracking uncertainty, or true packet loss.

The new task controller uses the public achieved XYZ from simulation, not camera-only vision or a learned VLA; its evidence and readback policy could potentially wrap a VLA, but no VLA policy was evaluated here. No other investigator's independent new-seed fork execution or upstream maintainer adoption of this algorithm has been documented. These experiments are author-owned source contributions rather than an official ManiSkill method merge.

### 6. Reproduction and external review

All following resources expose their exact original execution states; none should be represented as outside-laboratory confirmation:

- [Primary source-preregistered mixed-truth protocol](../MIXED_ACK_TRUTH_PPO_NEW64_PREOUTCOME_V1.json), [native PhysX execution](../frozen_ppo_mixed_ack_truth_physx.py) and [full 64-trial independent auditor](../audit_mixed_ack_truth_new64.py).
- [Original successful 576-world PhysX Actions](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37915263314) and [17 exact original JSON / SHA256 files](./evidence/mixed_ack_truth_frozen_ppo_original64_860001_870032/).
- [Independent source-hash archival verification](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37916032672).
- [One-click genuinely external investigator-owned fork entry](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/mixed-ack-truth-frozenppo-new64-20261009/.github/workflows/outside-fork-mixed-ack-physx.yml), allowing a researcher to choose new fixed seeds *before* computing any results, with original actor, commit, dependency freeze and failed episode preservation. This workflow alone does NOT count as independent external replication.

### 7. Conclusion

**Updated conclusion following the adversarial full-ACK and sequential-probe trials:** The task-level information savings on the earlier first-mixed, second-held cohort remain real within that cohort. However, a physically realized four-combination ACK study revealed 2/18 incorrect confident history guesses, and a new prospective, fully matched two-probe experiment failed to reduce information cost or establish any reliability improvement. Therefore the current method is an **empirically useful but noncertifying controller-memory observer**, and the flagship open research question is how to establish/monitor the validity of an external response model before granting authority to act. Neither top-tier acceptance nor safe real-robot deployment follows from these findings.


A missing robot command acknowledgement creates uncertainty about the destination controller's *remembered target*, even if the action interface is already fully specified. In controlled, source-auditable PhysX manipulation tasks with a physically mixed first execution event, identifying a *complete discrete controller target history* from public motion can reduce explicit privileged target reads while maintaining observed aggregate task outcomes versus a strong pre-registered task-dependent query policy. A zero-read fault-pattern assumption no longer explains the mixed-truth result, especially on StackCube trials whose first command actually executed. The evidence supports a **narrow conditional engineering mechanism and cost tradeoff**, not a universal optimal-information policy, a new set-membership theorem, an externally adopted top-tier robotics system, or an assurance of real robot safety.

**Next scientific gate:** reproduce with an outside investigator's fork and genuinely unused seeds; then randomize *both* acknowledgement outcomes and compare against an ActionShift-style matched-information active-probing controller that receives exactly the same public samples, actuator opportunities and privileged read budget. Preserve all unsupported-model failures and newly incorrect confident decisions. Do not claim L8/L9 research standing or publication recognition by fiat.

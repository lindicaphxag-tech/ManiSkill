# When Did My Robot Command Execute?
### Execution-History Observability and Selective Controller-State Readback for Frozen Manipulation Policies

**Main-conference technical research core v4.0 | 9 October 2026 | Author-operated preprint draft: NOT reviewed or accepted**

**Status.** All results below are author-operated, source-frozen ManiSkill CPU PhysX simulations or genuine public-model LIBERO MuJoCo pilots. We distinguish original physical simulation, independent *source auditing*, and genuinely independent *outside-investigator execution*. The third is still missing.

## Abstract

A frozen robot policy can fail when transplanted from achieved-pose-relative actions to a controller that accumulates motion from its last *commanded* target. After two commands with uncertain execution acknowledgements, the controller's hidden target may correspond to four distinct complete pose histories. We study whether public end-effector motion can eliminate these histories and reduce authoritative controller-state reads without modifying the original manipulation policy. Our method maintains a finite set of typed SE(3) target histories and admits one history only when a previously calibrated physical-response model separates it from all alternatives; otherwise it explicitly reads the controller's target memory. A source-locked experiment on 64 new PullCube and StackCube initial states executes 576 native PhysX controller worlds, with independently verified identical predecision command/pose prefixes and the **same postdecision belief and action compiler** for public-evidence and fixed-read treatments. Both complete 53/64 tasks; the public-evidence treatment uses 48 rather than 64 private target reads and makes 16 public history admissions with no observed confident errors in this cohort. Separately executed true nonzero double-ACK experiments yield 49/64 identical task outcomes and 33 versus 51 private reads against a task-aware comparator. Importantly, an additional 640-world matched-public-information comparison exposes a confidently wrong history and one fewer task success for our method. Enlarging empirical response thresholds or repeating correlated public probes does not resolve this weakness in further prospective physical cohorts. A newly completed 64-task/640-world same-XYZ reweighting experiment further establishes that a 0.65 residual-derived confidence gate admits 17 instead of 21 histories, keeps task outcomes fixed at 54/64, and incurs 45 rather than 41 private reads, with two original missing-probe episodes retained and zero observed wrong admissions for both policies. These findings support **conditional query economy**, while placing a falsifiable reliability boundary on motion-based hidden-history inference; they do not establish hardware safety, statistical noninferiority, or general VLA fault recovery.

**Keywords:** robot learning; frozen policy transfer; execution ambiguity; controller target memory; partial observability; selective sensing; source-authenticated simulation.

## 1. Problem: three states that must not be conflated

A source policy produces an action `a_t = π(o_t)` based on public sensor observations `o_t`. The destination controller has a last commanded target `M_t ∈ SE(3)`, while the robot is actually at achieved end-effector pose `X_t ∈ SE(3)`. They differ whenever physical response lags, clips, contacts an object or is otherwise disturbed.

For a **verified target-relative** native action chart `F` and unknown binary execution `z_t ∈ {0,1}`, the hidden target recurrence is

```text
M[t+1] = F(M[t], u[t])    if z[t] = 1 (native command physically executed)
M[t+1] = M[t]             if z[t] = 0 (native command physically held)
```

The policy's intended `u_t`, the message transport's acknowledgement, the actual execution truth `z_t`, the achieved pose `X_t`, and the controller's commanded goal `M_t` are distinct variables. Missing ACK cannot be repaired by assuming the observed achieved pose equals the hidden commanded target. Two unknown commands can induce up to `2² = 4` complete target-history hypotheses `H_t`; some may coincide, but that is not guaranteed.

**Scope restriction.** We study uncertainty in *execution history under an already verified native action chart*. General hidden action frame, gain, latency and wiring identification are broader problems already studied by related work including ActionShift and ActionABI. This work does not claim invention of active probing or belief-state control.

## 2. Method: history-preserving control and evidence-or-read authority

**State:** maintain full hypothesis records `h = (history, target_position, target_quaternion, native_chart_provenance)`, never a position-only target implicitly married to an invented orientation. Each unknown-ACK action branches histories for applied versus held. The original frozen PPO remains unchanged.

**Bounded action:** for the known native controller chart, a candidate common command is authorized only when its target-error budget holds for every remaining complete-history hypothesis. A failure results in an explicit controlled read or refusal. These budgets concern *commanded setpoint geometry*, not contact force, collision probability or physically guaranteed safe exploration.

**Public motion witness:** for a predeclared, known-delivered neutral native command, observe actual achieved XYZ before and after physical stepping. For each candidate complete history, calculate its distance to the frozen empirical gain/noise response envelope. Accept candidate `i` only if it is the **sole compatible complete target history** and every competing candidate fails the prespecified separation margin; else spend one counted authoritative target-memory read at the decision point. If the response model itself is unsupported, the observation does **not** become privileged truth.

```text
unknown executed/held ACK × 2
    -> enumerate complete SE(3) target histories (up to 4)
    -> physically step the registered neutral probe
    -> observe public achieved end-effector XYZ
    -> test complete-history compatibility under PREVIOUSLY FIXED response tube
       -> exactly one uniquely compatible, separated history: select its intact full target
       -> zero/multiple/not trustworthy: explicitly read actual native controller target
    -> run the SAME downstream belief/action compiler as the mandatory-read comparator
    -> report physical manipulation completion and every private read
```

### Identifiability boundary

Let `Y_h` be the set of possible public probe-response observations under history `h` **if a trusted physical observation model were correct**. If `Y_h ∩ Y_g ≠ ∅` for two different target histories `h ≠ g`, a deterministic decision rule using only that public observation cannot always distinguish the two histories: the overlapping observation is compatible with either physical world. It must accept the possibility of a wrong history or abstain/query. This elementary indistinguishability property motivates rejection under ambiguity; it is **not** a new probabilistic safety theorem.

The experimental `Y_h` is approximated using an empirical previously calibrated response envelope. Its coverage may fail under contact or dynamics shift. Hence even disjoint **estimated** response tubes do *not* certify physical identifiability. The recorded false-confidence cases are direct counterexamples to turning the approximation into a deterministic guarantee.

## 3. Experimental protocol and evidentiary integrity

Two public frozen pretrained PPO manipulation policies control PullCube and StackCube. Native ManiSkill CPU PhysX actually steps separate controller worlds; the fault is a physically applied native intended action versus a genuinely held zero arm action, while the adapter does not receive the ground-truth execution bit. Four `(t2,t3)` true applied/held fault patterns are balanced across initial states in each task. An actually stepped known-delivered neutral native action is charged as additional actuation, not silently inferred from a mathematical example.

**Primary causal cohort:** distinct, precommitted PullCube reset IDs 1480001–1480032 and StackCube 1490001–1490032, nine physically executed controller conditions per seed (576 actual native worlds). The public-history and mandatory-private-reader arms are verified to have identical physically executed native t2/t3 command prefixes, matching achieved and private target SE(3) before t5, and exactly the same downstream `UncertainDeliveryBelief` and native action compiler after t5. Only whether history is publicly admitted or read authoritatively differs in the intended causal comparison. Every source row, early refusal, initial-state identity, failure and independent per-shard audit is preserved.

**Evidence:** [unaltered genuine real PhysX 10-job run](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37925044658) · [permanent 19-file original, byte-checked audit and SHA256 archive](https://github.com/lindicaphxag-tech/ManiSkill/tree/evidence/shared-compiler-causal-original64-20261009/research/frozen_policy_transfer/evidence/shared_compiler_postquery_causal_original64_1480001_1490032) · [source-only original archiver](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37925911620).

First implementation/source-identity attempts failed *before complete physics* due to an action-resynchronization ordering problem. The successful implementation was then fixed to Git SHA `12b0156be54222e4a3ecf573898ab337c046426e`. This provenance is part of the method record. We do not relabel implementation failures as negative treatment outcomes.

## 4. Results: do not pool physically different experiments

| Separate source-authenticated native PhysX cohort | Public-history official task success | Public private reads | Comparator actually executed | Comparator success / private reads | What the cohort tests |
|---|---:|---:|---|---:|---|
| **Same physical prefix + same downstream compiler** · 64 resets/576 worlds | **53/64** | **48** | Mandatory fixed target read | **53/64 / 64** | Isolates decision information source under matched compiler |
| True **nonzero** t3, full executed/held 2×2 · 64 resets/576 worlds | **49/64** | **33** | Precommitted task-aware read route | **49/64 / 51** | Physically real second-ACK target-change stress |
| Matched public-XYZ Bayesian comparator · 64 resets/640 worlds | **53/64** | **48** | Same-public-information Bayes-style posterior / fixed read | **54/64 / 62; 54/64 / 64** | Alternative posterior gating and false confidence |
| Empirical model-validity recalibration · 64 resets/640 worlds | **58/64** | **51** | Conservative widened response envelope | **58/64 / 53** | Does naive empirical coverage widening resolve reliability? |
| Two physically stepped public response segments · 64 resets/640 worlds | **48/64** | **41** | Stricter two-segment compatibility | **48/64 / 43** | Does repeated correlated public observation help? |
| New original same-XYZ residual 0.65 confidence gate · 64 resets/640 worlds | **54/64** | **41** | Deterministic same-residual 0.65 extra gate / fixed read | **54/64 / 45; 55/64 / 62** | Does a reweighted version of the same public evidence reduce wrong authority? **NO observed benefit**; 2 early-censored trials retained |

The rows represent separate actual source populations, not five replications from a common IID test distribution. Their task results must not be added together to manufacture a general success rate.

### 4.1 Main physical-prefix and compiler-controlled causal result

Public-history and fixed-private treatment succeed on **exactly the same 53 original task/reset identities** and both fail on the remaining 11, with **48 vs 64** actual decision-time target reads. The 16/64 (25%) reduction is a descriptive reduction in *privileged target-memory reads* on this source cohort, not total information economy or verified task-success noninferiority. The public arm authorizes 16 complete histories and no wrong confident history was observed here. Its extra public measurements still have information, latency and energy costs not accounted for by this one metric.

The separately stepped task-aware strong route finishes 50/64 tasks at 60 private reads in the same overall study, but it is **not automatically a physically identical-prefix comparison**. Do not apply the primary causal identification statement to that row.

### 4.2 Physically nonzero second-ACK stress

In another completely distinct frozen 64-task source population, the second unknown native ACK action is a predeclared **nonzero** command, not an always-held neutral action. Source audit shows public-history 49/64 with 33 reads versus a physically executed task-aware competitor 49/64 with 51 reads; their **49 successes and 15 failures occur on the same identities**. Paired original per-episode reads: 24 public fewer, 6 public more, 34 equal; exact exploratory two-sided sign-test `p = 0.0014309`. This is read-count evidence under that original fault generator, not statistically proved total-sensing superiority. The hardest **held/held** condition has zero public identifications; on PullCube it consumes more target reads than the task-aware comparator.

Evidence: [genuine native PhysX #37921809790](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37921809790) · [original complete source and SHA256](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/two-by-two-real-nonzero-ack-physx-20261009/research/frozen_policy_transfer/evidence/true_two_by_two_nonzero_ack64_1340001_1350032) · [independent paired statistic audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924333984).

### 4.3 Main negative finding: the empirical model is sometimes wrong

A newly frozen **same-public-XYZ** physically executed 64-state/640-world comparison recorded **one confidently WRONG whole history** and one fewer successful task for the public method (53/64, 48 reads) compared with a separately source-precommitted ACK-specific Gaussian posterior comparator (54/64, 62 reads, no wrong). A mandatory reader completes 54/64 using 64 reads. The posterior comparator gets the same public before/after XYZ, rather than a hidden target oracle, but it is not a full original ActionShift/DualABI replication. [Actual original source-and-audit run](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924335444).

Other original physically executed tests found previously too-narrow empirical motion envelopes, including two confidently wrong histories in an earlier fully mixed-ACK cohort. Increasing a frozen StackCube envelope using 32 previous physically observed true-history residuals made new-cohort authority *more conservative* (53 vs 51 private reads) while both strategies completed 58/64 and both had zero wrong in that new population. This is **no demonstrated reliability advantage**. [Independent 64-source physical test](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924240294).

A second correlated public neutral-response observation also gave no new-cohort task benefit: both 48/64, with 43 rather than 41 private reads under the stricter two-evidence authorization. [Independent 640-world physical test](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37921282989).

**Additional fully original negative test (different prospective sample).** A 0.65 normalized residual weight gate was selected **after observing an older development false-authority case**, and then frozen for a disjoint original task cohort. Its 64 new frozen PPO reset identities and ten physically stepped worlds per reset were retained, including **two cases without complete t4 public-probe exposure**. We corrected only a post-run auditor that originally treated those absent public frames as impossible; the original physical inference algorithm, controller, thresholds, checkpoint and precommitted seeds remain byte-identical. Its successful complete-source audit establishes:

| Exactly 64 original task resets | Official completed tasks | Private reads | Accepted histories | Wrong confident in this cohort | Public XYZ events actually received |
|---|---:|---:|---:|---:|---:|
| Original public complete-history set-membership | **54** | **41** | 21 | 0 | 124 |
| Same public residuals + *deterministic* additional 0.65 score gate | **54** | 45 | 17 | 0 | 124 |
| Mandatory trusted private target read | **55** | 62 | — | — | 0 extra |

The 0.65 gate is **strictly observed-Pareto-dominated** by the original rule on this original sample's task success, private reads and observed confident errors: exactly the same 54 successes/failures, **four original per-trial extra reads, no observed safety gain**. Both source methods physically share the same 124 achieved-XYZ sample events across 62 fully observable original trials; the other two task episodes remain in the entire intent-to-treat denominator. Zero observed wrong in this specific source **does not establish reliable gate improvement**; the earlier separate matched-public experiment includes one genuinely wrong original rule. These are not pooled IIDs.

[Original physically executed and unmodified-method source replay](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37928191282) · [all 19 archived genuine original-source JSON and SHA256](https://github.com/lindicaphxag-tech/ManiSkill/tree/evidence/dual065-negative-native64-20261009/research/frozen_policy_transfer/evidence/dual065_observer_negative_original64_1820001_1830032) · [byte-identical original full64 re-audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37928979702) · [strict 64-pair dominance source test](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37929323479).

### 4.4 Three rigorous information limits (standard theory, NOT claimed invented)

- **Indistinguishability bound.** If two possible native histories induce exactly the same distribution of any allowed public probing transcript, a method that abstains with probability \(q\) and misidentifies with probability \(e\), under equal prior histories, satisfies \(e + q/2 \ge 1/2\). More generally, the total-variation lower bound is \(e+q/2 \ge (1-\mathrm{TV}(P_0,P_1))/2\). If the sensing channel cannot physically distinguish those histories, no extra threshold tuning can overcome this bound.
- **No additional information from deterministic reweighting.** For original residual vector \(R\) and normalized pseudo-posterior score \(W=g(R)\), \(I(H;R,W)=I(H;R)\). The 0.65 weight computed from the exact same XYZ residuals is a **rejection heuristic**, not a new independent physical witness or calibrated probability.
- **Split-conformal marginal authority bound, only under explicit assumptions.** With an exchangeable independent calibration set of true-history motion nonconformity scores, a frozen \(1-\alpha\) prediction set \(C(Z)\), complete true-history candidate coverage, and unique-history authorization only when \(|C|=1\), \(P(\mathrm{wrong\;and\;authorized})\le\alpha\). This does **not** bound conditional error among authorized cases, handle distribution shift without assumptions, imply task success, or certify collision/force safety. With only 32 calibration cases, choosing \(\alpha<1/33\) requires an infinite split-conformal quantile and can force all ambiguous cases to query.

Complete careful statements, proofs, assumptions and references: [Reviewer Theory Appendix v4](https://github.com/lindicaphxag-tech/ManiSkill/blob/evidence/shared-compiler-causal-original64-20261009/research/frozen_policy_transfer/REVIEWER_IDENTIFIABILITY_CONFORMAL_ABSTENTION_V4.md).

**Implication.** The next method should detect *when its empirical observation model is unsupported* before trusting apparently unique pose histories. Naively requesting more observations or loosening/tightening one global threshold is not sufficient evidence of that ability. Our current 0.65 same-residual heuristic should be reported as a **negative baseline**, not promoted to the proposed contribution.

## 5. A separate native VLA capability gate (not evidence of this method)

A publicly released, genuinely task-tuned frozen SmolVLA checkpoint was executed through original LeRobot preprocessing and native LIBERO MuJoCo control on original fixed initial states. With the published one-step flow-denoising setting, genuine official results were:

| Original native LIBERO Spatial task | Official completion |
|---|---:|
| Task 0 | **1/4** (false, false, false, true) |
| Task 1 | **4/4** (true, true, true, true) |

These are exploratory small cohorts, one task/init-state overlaps an earlier pilot, and no execution-ACK faults or BeliefBridge recovery were tested. The exact original official `eval_info.json`, checkpoint identity, source commit and independent original result audit are preserved at [permanent SmolVLA 4+4 evidence archive](https://github.com/lindicaphxag-tech/ManiSkill/tree/evidence/smolvla-libero-4plus4-original-20261009/research/vla_beliefbridge/evidence/authentic_smolvla_libero_four_inits_per_task_20261009), originally executed in [GitHub Actions #37924054645](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924054645).

Crucially, direct inspection of the **actually loaded** original robosuite 1.4.0 native controller on a reset MuJoCo robot shows `self.goal_pos = set_goal_position(..., self.ee_pos, ...)` under a delta action. Its position target is **achieved-pose-relative**, not a persistent commanded-target-relative recurrence of the sort tested in ManiSkill. [Version/source AST native ABI evidence](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924496336). Therefore the ManiSkill controller target-memory claim cannot be directly carried to this LIBERO VLA setup. No general VLA manipulation recovery gain is reported.

## 6. Threats to validity and decisive work for external acceptance

**Information-cost accounting that should accompany every significant result.** For public observations \(S\), privileged native controller reads \(Q\), genuine additional neutral probe actuation \(A\), and elapsed wall-clock or control delay \(T\), compare methods over explicitly stated nonnegative cost weights, \(C = c_S S + c_Q Q + c_A A + c_T T\). Do not invent measured coefficients or add freely observed frames to the privilege column. Prefer plotting the empirical 4D Pareto surface and reporting task success and false-authority/abstention separately. If weights are not measured, present a sensitivity region, **not** a one-number "total efficiency" percentage. In particular, a private target read reduction is an important but partial metric.

**First, cost parity.** The primary results measure privileged controller-memory read counts; they do not normalize public XYZ measurements, actuation, observation bandwidth, delay or force. A truly matched sensor/actuation/latency-budget competing active identification strategy is missing. Any superiority claim against generic ActionShift needs a faithfully executed, same-latent-variable, same-information-budget adaptation—not a renamed generic entropy heuristic.

**Second, empirical reliability.** Zero wrong-confident labels in individual cohorts is not a bound on error probability, and a different authentic cohort already contains one wrong-confident example. The performance gain must survive a pre-registered new fault regime with model-support or distribution-shift detection and every error retained.

**Third, causal coverage.** Four execution truths are balanced across distinct reset identities, not every four counterfactual outcomes for each individual reset. The main public vs fixed causal test keeps the *observed prefix and compiler* fixed, but it remains simulator-based and not a randomized real-world hardware packet-delivery experiment.

**Fourth, embodiments.** Existing Panda/xArm6 native target-restoration mechanism experiments elsewhere in this fork do not show published task-level PPO transfer to a different robot with a verified matching checkpoint. LIBERO's achieved-relative controller does not satisfy the target-relative hypothesis.

**Fifth, outside authorship.** A [source-locked one-click investigator-owned true-2×2 nonzero-ACK PhysX challenge](https://github.com/lindicaphxag-tech/ManiSkill/actions/workflows/outside-true-2x2-nonzero-ack-physx.yml) exists. But author-operated fork CI—even with twice independently derived source audits—is **not an outside laboratory reproduction**. A reviewer must select unused source resets and publish their actual independently executed original artifacts. No maintainer merge or peer review acceptance is claimed.

## 7. Reproduction and evidence availability

- Core source and same-compiler verified original protocol SHA: `12b0156be54222e4a3ecf573898ab337c046426e`.
- [Actual 576-world source run and original auditable CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37925044658).
- [Permanently committed unmodified 16 PhysX shard originals + original full independent audit and SHA256](https://github.com/lindicaphxag-tech/ManiSkill/tree/evidence/shared-compiler-causal-original64-20261009/research/frozen_policy_transfer/evidence/shared_compiler_postquery_causal_original64_1480001_1490032).
- Original independent audit contains three Python `Infinity` numeric diagnostics for unbounded rotation in **negative-control refusals**. The original files are not rewritten. A [portable standards-compliant derivative](https://github.com/lindicaphxag-tech/ManiSkill/blob/evidence/shared-compiler-causal-original64-20261009/research/frozen_policy_transfer/derived/shared_compiler_causal64_strict_json.json) tags these as explicit `positive_infinity` objects, and [stdlib integrity CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37926589737) proves the derived semantic tree exactly matches the SHA-checked original after an explicit tagged conversion.
- [Separate immutable SmolVLA 8 original native task episodes](https://github.com/lindicaphxag-tech/ManiSkill/tree/evidence/smolvla-libero-4plus4-original-20261009/research/vla_beliefbridge/evidence/authentic_smolvla_libero_four_inits_per_task_20261009).

## 8. What would need to be true for an excellent main-conference acceptance?

This manuscript's present evidence supports a targeted original **failure-mechanism** finding; it is not yet a superior, trustworthy recovery **algorithm**. An uncompromising main-conference reviewer can reject it for each of: (i) no experimentally validated independent model-validity gate, (ii) no hardware or learned-policy cross-controller task transfer, (iii) no real external investigator replay, and (iv) no fully information/latency-matched active-identification competitor. These are substantive missing contributions, not typesetting errors.

The next algorithmic claim should be preregistered before any results on untouched fault regimes. A fully admissible candidate must reduce wrong confident authorizations or improve the task/read/sensing frontier against **same-public-observation** baselines without retuning the model on any previous test fault. Failure to pass this gate must be explicitly reported as a negative result.

A compact main-paper figure sequence would show: (1) failed ACK execution DAG and complete controller target histories (distinct achieved pose), (2) source-verified real paired native control protocol, (3) per-task and four-ACK-truth 64-state error/read/task frontier with all failures, (4) one true wrong-confidence physical counterexample and the dual-score negative, (5) OOD reliability and full sensing/latency budget. Existing SVG figures should be generated from original source results only, not artistic robot performance mockups.

For anonymous CoRL/RSS/ICRA submission, do **not** include author-identifying direct fork links in the actual double-blind submission if policy prohibits them; this linked GitHub research manuscript is an **open research archive** with provenance, not an anonymity-compliant camera-ready PDF. Use only verified scholarly references and official format. Publication decisions are made by real reviewers.

### Publication claim ceiling

The supported present contribution is a **falsifiable, source-auditable execution-history observability study** showing query reduction under a verified target-relative native controller, plus demonstrated empirical false-confidence failure conditions and genuine native VLA *task capability* evidence on a semantically different controller. Without a validated model-reliability method, genuinely information-matched active baseline, independent outside execution and peer review, this is **not** a proven generally safe robot recovery system or a demonstrated high-performing VLA fault-recovery algorithm.

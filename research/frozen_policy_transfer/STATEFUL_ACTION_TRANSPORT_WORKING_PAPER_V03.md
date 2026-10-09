# Evidence-Gated Stateful Action Transport under Ambiguous Command Acknowledgements

*Working-paper manuscript v0.3 · 9 October 2026 · Not peer reviewed, not submitted, and not independently reproduced.*

## Abstract

Numerically compatible robot manipulation actions can encode different physical targets when a frozen source policy expresses displacement from the achieved end-effector pose, but a target controller accumulates commands relative to its previous commanded target. Missing execution acknowledgements make this hidden target history set-valued. Rather than assuming delivery, unconditionally stopping, or always reading privileged controller state, we test two complementary conditional information-acquisition mechanisms on unchanged publicly released third-party PPOs. First, a two-history commanded-target compiler authorizes a common native control only when its computed position/rotation discrepancies satisfy prespecified budgets, querying the true target only when the certificate refuses. In a preregistered owner-run ManiSkill PhysX comparison on 64 new PullCube/StackCube task states, this achieved 60/64 successes with 15 additional target reads, versus 57/64 and 64 reads with compulsory target readback; paired success was not significantly higher (exact p=0.453). In a separate prospective 64-NEW-state timing comparison, evidence-triggered reading yielded 58/64 successes with 17 reads, versus 47/64 with a state-independent preregistered 16-read schedule (12 selective-only versus 1 scheduled-only paired success; unadjusted exploratory exact p=0.00342). Second, an empirically fitted public achieved-motion response gate is permitted to select an execution history only when one uniquely fits its **pre-outcome-frozen** task-specific response envelope; ambiguous or model-falsifying observations trigger one privileged read. On a prospectively disjoint 32-condition dual-execution-truth native PhysX study, this sensor-gated hybrid completed 27/32 tasks using 11 privileged reads versus the mandatory-read comparator's 27/32 using 32, with 21/32 public-only accepted histories and no observed wrong accepted labels. Both task success and label coverage are conditional on one Panda controller family, two pretrained PPO/task families, and narrow artificial missing-ACK fault interventions. The geometric Chebyshev/SO(3) midpoint is established mathematics, empirical response envelopes do not guarantee coverage, near-matched query counts are not equal spending, and observed paired parity is not a noninferiority certificate. We release precommitted protocols, immutable source-verified full-denominator evidence, adversarial failed-history counterexamples, and CPU-only audits; authenticated real-robot control, prospective matched-info ActionShift baseline comparisons and independent external research reproduction remain outstanding.
## 1. Problem: identical action numbers, different hidden controller histories

Let a frozen task policy `pi(o_t)` output a canonical achieved-pose-relative action. Its decoded, intended end-effector goal is `D_t=(d_t,R_d,t)`. The target controller instead uses the **previous commanded target** `M_t=(m_t,R_m,t)` and accumulates a native command `u_t` into the next setpoint.

For the examined root-translation and root-left-rotation target controller,

```text
m_{t+1} = m_t + u_position
R_{m,t+1} = R_u R_{m,t}.
```

Successful use of `u_t` depends on a stored target that is not generally determined by the currently *achieved* pose. A lost or missing execution acknowledgement makes the target history set-valued. A policy-only instantaneous state estimator can remain unable to distinguish two internally valid controller histories even if the measured robot pose is identical.

**Indistinguishability witness.** Given two plausible previous Cartesian target states `m_A` and `m_B`, any single observation-only command `u` targeting `d` must incur

```text
max( ||m_A+u-d||_infinity, ||m_B+u-d||_infinity )
  >= ||m_A-m_B||_infinity / 2.
```

The triangle inequality supplies this lower bound. This statement concerns a commanded **setpoint**, not actual achieved motion, force, contact or collision risk. It does not preclude an estimator using additional history, a trustworthy target readback or informative new sensing.

## 2. Conditional method: bounded common action, selective query, refuse

At a control step, the adapter retains a candidate previous target-memory set `H_t`. The present implementation and proof apply to two known candidates, not an arbitrary multimodal set. This candidate completeness requirement is a substantial assumption: the simulator fault injector models either delivery or a zero-arm-delta hold, but a deployed system could experience additional unmodeled timing and actuator effects.

### 2.1 Native positional target bound

With certified Cartesian target intervals `[L_i,H_i]`, native physical positional command intervals `[a_i,b_i]`, and intended target `d_i`, the minimizing action and exact worst-case infinity setpoint discrepancy are:

```text
c_i = (L_i+H_i)/2
u*_i = clamp(d_i-c_i, a_i, b_i)
E*_position = max_i [ (H_i-L_i)/2 +
                       distance(d_i-c_i, [a_i,b_i]) ].
```

The closed form is standard interval optimization. The implementation refuses a command when its worst-case error plus numerical guard exceeds the declared position tolerance. It also refuses absent/expired evidence, an invalid frame/chart, or native-control bounds that do not match the true execution interface.

### 2.2 Two-history rotational target bound

For two plausible previous target rotations `R_A` and `R_B`, choose a shortest-geodesic midpoint

```text
R_mid = R_A Exp(0.5 Log(R_A^-1 R_B))
R_u = R_d R_mid^-1.
```

Under *left* multiplication by the same exactly representable `R_u`, the two commanded target rotations remain within half the `SO(3)` geodesic separation from `R_d`. The code verifies that the actual native Euler XYZ scaling represents this command **without clipping**; otherwise the authorization fails. The result does not carry over automatically to a right-multiplied chart, a quaternion-component clipper, three or more separated rotations, or joint/torque controllers.

### 2.3 Decision contract

```text
for each frozen-policy step:
    decode the intended source physical goal
    update the two controller target histories using known ACK events
    if all hypotheses are trusted, complete, fresh, and native chart verified:
        find one bounded action valid for both histories
        if the position and orientation setpoint bounds meet budgets:
            issue the exact native bounded action; continue
    if one authoritative readback is permitted and remains unused:
        read the REAL previous target, collapse the belief, compile, continue
    else:
        refuse action and record the failure
```

This is an **authority-aware interface strategy**, not a claim that author-owned hypothetical memories are authenticated by hardware. In the current simulator, boolean attestation is assigned by the experiment's known fault model; deployment requires a real source of truth and freshness guarantees.

## 3. Controlled experiments and preregistration

All headline policy trials use official ManiSkill PhysX CPU scenes and published third-party ActionShift PPO checkpoints, **unchanged weights**, for PullCube and StackCube. They use the Panda source `pd_ee_delta_pose` and destination `pd_ee_target_delta_pose` controller modes, with 50 native action steps per trial. At frozen zero-indexed step two, the test controller is advanced through physics but receives a zero arm target increment in place of the requested increment, while its gripper command is preserved. The adapter is not told which execution occurred. This is a controlled **target hold plus ambiguous ACK**, not a wire-level packet-loss simulator.

The initial 16-state method-discovery study used PullCube seeds 122001–122008 and StackCube 132001–132008. The method, released checkpoint revisions, native action bound, error budgets (0.05 m positional infinity norm and 0.05 rad geodesic orientation), original model identity, and a maximum of one target query were then frozen before testing a disjoint 64-state cohort: PullCube 142001–142032 and StackCube 152001–152032. Both task families passed their frozen source-competence gate.

Seven experimentally separated control arms included original no-fault PPO, continuously privileged target oracle, optimistic unknown-ACK delivery assumption, exact-common-action or refusal, bounded-common-action without queries, bounded-common-action with one selective query on certification refusal, and forced single-readback recovery. The oracle's continuing private memory is NOT counted as zero reads. Target-state reads used solely in **post-dispatch certificate auditing** are recorded separately and were not fed into online action decisions.

Source identity:

- [Original method pre-commit and 16-state report](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/frozen_policy_transfer/BOUNDED_QUERY_PHYSX_16_ORIGINAL_RESULT.md).
- [Frozen new64 method/seeds and full original results](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/frozen_policy_transfer/ROBUST_QUERY_NEW64_PROSPECTIVE_RESULTS.md).
- [Actual eight completed public PhysX task jobs](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37828426195).
- [Permanent SHA-256-verified eight-original-JSON archive](https://github.com/lindicaphxag-tech/ManiSkill/tree/main/research/frozen_policy_transfer/evidence/robust_query_new64_142001_152032).

## 4. Observed results (no post-hoc exclusion)

| Fault-treatment arm, 64 NEW states | PullCube /32 | StackCube /32 | All /64 | Extra privileged target queries |
|---|---:|---:|---:|---:|
| No-fault source PPO (competence reference) | 32 | 28 | 60 | 0 |
| Continuously privileged true-memory oracle | 32 | 26 | 58 | Continuous; not zero |
| Optimistic execution guess | 31 | 11 | 42 | 0 |
| Exact-common-action or refuse | 0 | 0 | 0 | 0 |
| Bounded-common-action only | 30 | 17 | 47 | 0 |
| **Bounded-common-action + selective query** | **32** | **28** | **60** | **15** |
| Always one target readback on fault | 32 | 25 | 57 | 64 |

The selective rule made 2 target reads on PullCube and 13 on StackCube, compared with 32+32 compulsory reads. The observed query reduction was `1 - 15/64 = 76.5625%`. The selective result matched the no-fault source's pooled success **count**; this is not within-trajectory equivalence, since different physical trajectories and failures occurred.

### 4.1 Paired uncertainty: an explicit limit on the positive story

Across 64 prespecified paired reset states, the selective arm succeeded where compulsory one-read failed on 5 states; the inverse occurred on 2. The observed paired risk difference is `(5-2)/64 = +0.046875`. A two-sided **exact discordant-pair conditional binomial (McNemar) test** yields `p=0.453125`, so the data do not establish better task success. A conservative Bonferroni-joint interval formed from two exact binomial confidence limits for the discordance-cell probabilities spans approximately `[-0.0994, +0.1850]` under iid sampling assumptions. It includes zero and should NOT be interpreted as evidence of noninferiority or equivalence. The task-family counts differ and only two separate released PPO/task families were tested; the 64 states are not 64 independent trained policies.

The observed fraction requiring a privileged decision read was `15/64 = 0.234375`. An exact binomial interval is approximately `[0.1375, 0.3569]` **only under justified iid trial sampling**. On the specified 64 trial states, the 15 calls and 76.56% reduction are literal, deterministic experimental counts and do not need that assumption.

[Exact, source-pinned Python statistical audit](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/frozen_policy_transfer/review/paired_query_stats.py) · [Cross-Python passing audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37832254107).

### 4.2 Failure witnesses are first-class evidence

In another previously completed, independently preregistered 32 task/truth-condition study, the actual execution of the earlier arm action was varied between **applied** and **zero-delta held**. The selective rule completed 28/32 conditions using 10 readbacks; compulsory one-read completed 29/32 using 32. This is a direct negative check against the claim that selective querying always preserves success across both ACK truths.

Notably, StackCube reset seed 152001 under the *actually applied* truth received 47 authorized bounded common target commands with no privileged read and **failed the task**, whereas the one-readback comparator succeeded. Therefore a mathematical controller-setpoint discrepancy certificate **does not** imply successful contact-manipulation outcomes. The action-space Lipschitz/contact margin needed for such a conclusion has not been validated and may fail at contact transitions.

## 5. Diagnostic evidence outside the task-success headline

Independent native Panda controller audits show the commanded-target translation and joint-position compiler agreements with official execution on preselected task/seed pairs. A native three-world replay creates identical joint configurations and achieved end-effector poses but different legitimate commanded-target histories through the official controller state API; a copied command produces roughly 2 cm commanded-target error, while full-memory inversions recover a common desired target. This is a **controlled counterfactual state replay**, not a claim that such hidden states are naturally frequent or indistinguishable when full target telemetry is supplied.

A distinct native joint-target audit on **Fetch (7 arm joints, 13 native action dimensions)** and **xArm6 Robotiq (6 arm joints, 7 native dimensions)** validates the conditional additive target-memory setpoint model on two other simulated embodiments. It is NOT a learned policy task-transfer result across those robot embodiments.

These auxiliary source-controlled studies establish some chart and observability assumptions of the proposed compiler. They do not measure actual force, collision clearance, unsafe stopping distance or hardware tracking.

## 4C. Stronger prospectively registered comparator: query *timing*, not query count

Comparing one selective query against mandatory querying in every fault trial leaves a central confound: is the positive result caused by observing *at the right time*, or merely by spending less/extra privileged information? We addressed this with another independent **pre-outcome-registered cohort of 64 NEW original seeds** (PullCube 260001–260032 and StackCube 270001–270032), leaving the existing PPO weights, original seven-arm compiler and physical fault mechanism unchanged. We added exactly one eighth arm: **at the first post-fault decision, read true controller target state if and only if `seed % 4 == 0`; never read it otherwise**. This 16-of-64 query schedule was frozen before observing any new task outputs. It does NOT condition on fault severity, the belief certificate or task reward; it is not a truly randomized allocation and is not allowed to choose better query seeds after the experiment.

| Prospectively locked method (64 NEW reset states) | PullCube /32 | StackCube /32 | Total /64 | Privileged target decision reads |
|---|---:|---:|---:|---:|
| **Evidence-gated common action, then query on failure of bounds** | **32** | **26** | **58** | **17** |
| Nonadaptive schedule: once iff seed modulo 4 equals zero | 30 | 17 | 47 | 16 |
| Always one truthful target read after fault | 32 | 28 | 60 | 64 |
| Bounded common action, no privileged read | 29 | 12 | 41 | 0 |
| Optimistic ACK assumption, no privileged read | 31 | 9 | 40 | 0 |
| No-fault source policy (competence context only) | 31 | 30 | 61 | 0 |

All **eight original 8-seed native PhysX jobs of the FIRST completed run** succeeded. From the untouched per-seed official `success` flags, the paired exclusive wins of adaptive versus scheduled were **12 versus 1**, with 46 both-success and 5 both-fail pairs. The observed within-cohort paired success difference was `11/64=17.1875 percentage points`. The conditional two-sided exact McNemar/binomial p-value is `0.00341796875`. This is a **prespecified comparison to the scheduled arm but the p-value has not been multiplicity-adjusted for the larger evolving study**, and its inferential generalization would require well-supported assumptions about the seed sample, independent physical dynamics and task-family heterogeneity. We therefore distinguish significant *within this conditional paired test* evidence from an externally replicated, population-level claim. The actual 17 versus 16 reads are **near** the committed budget, not exactly identical; never describe this as a strictly equal-budget benchmark. Query call count is not latency, bandwidth, energy or dollars.

**Single-extra-read robustness analysis (an assumption-dependent bound, NOT an observed 16-read rollout).** The new adaptive method spent 17 reads versus the scheduled comparator's 16. If the 64 seeded simulator episodes are independent of each other and removing exactly one adaptive query can change only that one episode's binary success, then replacing any one of the 17 queried episodes by a failure still leaves **at least 57/64** adaptive task successes against the unchanged **47/64** scheduled baseline. Exact paired discordance under the worst of all 17 such one-episode deletions is at most `p=0.012939453125` *before study-wise multiplicity adjustment* (and other deletions give still smaller conditional p values). This bound is a **sensitivity certificate over the original binary trial outcomes**, not a policy execution with exactly 16 online reads, nor proof that query removal can be performed without causing hidden cross-episode coupling. [Source-hash-gated standalone influence code](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/frozen_policy_transfer/review/one_extra_query_sensitivity.py). It is reported only to quantify whether the single-read numerical budget difference could plausibly explain the entire 11-task advantage, under explicitly independent trials; a true exactly-16-read adaptive policy would still require an additional precommitted simulator run.
This design is substantially stronger than a compulsory-read comparator because the fixed schedule uses almost the same **number** of privileged controller target observations and the exact same target-recovery operator. The result supports **evidence-dependent observation placement** under the artificial target-hold and unknown-ACK treatment, not superior active POMDP planning in general. The two physical simulators are not independent robot embodiments: both tasks run on Panda with different externally released PPO weights. ActionShift's original active probe and learned adapter baselines have **not** been reimplemented in this matched information-budget experiment.

**Original data integrity and no reselection:** the locked timing protocol is at [precommitted immutable original source](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/CERTIFY_QUERY_PERIODIC_PLACEBO_64_PREDECLARED_V1.json), with source file blob `fc6c52c227f68c351b4f5637069672eae62a2e62`. The original first completed genuine PhysX execution was [run 37833053629](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833053629) at head `e23909a43b8d9aeb4dba5b46e8f9c9845993cb57`; later identical-seed reruns must not be counted as independent additional cases. All eight raw 8-seed JSONs are [source-hashed permanently in Git](https://github.com/lindicaphxag-tech/ManiSkill/tree/main/research/frozen_policy_transfer/evidence/periodic_query_placebo_new64_260001_270032), with a [full-denominator stdlib-only auditor](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/audit_certify_query_periodic_placebo64.py). Source confidence includes no self-declared external independent reproduction.
## 5A. Prospective public-only evidence: a partial substitute for private target reads

The previous results demonstrated a query-cost tradeoff only when the interface was allowed to read the actual privileged controller target under ambiguity. A stronger claim—that the unknown ACK itself can be inferred confidently from *public achieved motion*—requires an independently calibrated response model, not just a simulator producing two counterfactual worlds with separable trajectories.

We therefore prospectively tested a **fixed, training-seed-separated** empirical public-proprioception classifier, with its error envelope and outcomes declared before testing any new source reset seeds. The estimator uses only pre/post common native zero-arm-delta probe achieved XYZ and the two action-history-derived candidate target XYZ points; it declares one history only when a fixed per-task model-response envelope fits exactly one candidate. When both fit, it abstains; when neither fits, it explicitly reports an empirical model falsification. No private controller target is read by this classifier during a decision. The response envelope was calibrated from only four *previous* training reset seeds per task and is **not a hardware-certified dynamic bound**.

| Native PhysX outcome, two fault truths, 32 fresh source conditions | Value |
|---|---:|
| Confident hypothesis decisions using public achieved XYZ | 24/32 |
| Confident decisions with wrong executed/held label | **0/24 observed** |
| Abstentions / refuse cases | 8/32 |
| Of those, true history excluded by fitted empirical motion envelope | **1 (StackCube, seed 170104, actually applied)** |
| Public-only classifier task successes | 22/32 |
| Privileged-once-after-probe task successes (unequal information) | 30/32 |
| Blind optimistic task successes | 24/32 |
| Blind pessimistic task successes | 25/32 |
| Original source no-fault reference task successes | 28/32 |

Both fault truths (actual arm action applied versus neutral arm delta physically executed without ACK) were tested on each of eight fresh PullCube and eight fresh StackCube reset seeds, yielding **32 task-truth conditions and only two frozen policies**. The original fixed empirical envelope came exclusively from historical seeds 140001–140004 (PullCube) and 150001–150004 (StackCube), while the new population used 160101–160108 and 170101–170108. The source manifest/analysis retained all eight original four-state groups and all simulator failures without exclusion.

**Confidence is conditional.** Zero wrong decisions on 24 *selected accepted* cases does not prove reliable delivery classification. If confident accepted trials were iid Bernoulli samples from a fixed distribution, a one-sided exact 95% upper limit on the unknown accepted-case error probability is `1-0.05^(1/24) ≈ 0.1173` (11.73%), and a two-sided 95% Clopper–Pearson upper limit is `1-0.025^(1/24) ≈ 0.1425` (14.25%). Seed/task clustering and the acceptance-selection mechanism weaken any across-task or real-world extrapolation. The one **excluded true hypothesis** is a direct empirical-model counterexample; its refusal is a measured benefit of failing closed, not proof that calibration guarantees include the truth.

**Scientific verdict:** the new sensor-only classifier is a viable **abstention-sensitive diagnostic** for this particular public-motion test and misses fewer hidden histories than the earlier naive nearest-target heuristic, but **it does not beat the optimistic or pessimistic no-private-read comparator in task completion and is markedly below the once-privileged comparator**. Combining it with the selective-bound decision policy is an *untested research hypothesis*, not a retrospective success that may be folded into the 60/64 task claim. It will need a new, source-frozen evaluation with explicit inclusion of all ambiguous and model-invalid inputs, not post-hoc tuning on these 32 outcomes.

- [Prospective fixed classifier and task/seed/calibration precommit](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/EMPIRICAL_RESPONSE_NEW32_FROZEN_BEFORE_RUN_V1.json).
- [All eight independent genuine PhysX new-condition jobs and full audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37832214332).
- [Production public-only classifier source](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/empirical_probe_response_classifier.py).
- [Complete source-fixed evidence and raw logs](https://github.com/lindicaphxag-tech/ManiSkill/tree/main/research/frozen_policy_transfer/evidence/public_response_empirical_prospective_new32).
## 5B. Public evidence *or* authority: second, independent frozen hybrid test

Because the pure public-motion classifier in Section 5A was missing eight labels and achieved 22/32 tasks versus 30/32 with a real target-state getter, treating accepted classifier labels as a complete replacement for authority would overstate task reliability. We therefore tested a fixed **PUBLIC-FIT-OR-ONE-READ** policy on a **separately preregistered** new cohort. This is *not a retrospective fix* of the previous 32 task×truth conditions: that negative first cohort was already partially observed when the hybrid mechanism was designed, so the protocol explicitly discloses that history. The subsequent 32 conditions are distinct new physical source seeds.

The selected control decision is: obtain the same single neutral native arm probe and public achieved XYZ response as the source-matched no-private-read controls; compare the observed achieved-motion segment against two candidate controller goals using the old training-only empirical response envelope. If **exactly one** controller history is empirically compatible, continue with it and record **zero** authority reads; if **both or neither** are compatible, spend exactly one privileged true target readback and resume the unchanged PPO/controller. Do not silently use the true execution label, assume the statistical envelope is physically attested, or claim target-position error guarantees over robot contacts.

**Pre-registered new task/truth cohort:** PullCube reset seeds 180101–180108 and StackCube 190101–190108, each under actual command-applied and actual zero-arm-delta-held faults with missing acknowledgement. Thus there are 16 distinct reset states × two correlated execution truths = **32 task×truth conditions** and two externally released PPO checkpoints. The frozen empirical envelope learned only from older Pull 140001–140004 and Stack 150001–150004 source states. Six separate matched actual `env.step` controller worlds are run per condition, including public-only optimistic/pessimistic, public classifier alone, hybrid public-plus-conditional getter and mandatory getter.

| Genuine new native PhysX result | Completed tasks /32 | Extra privileged target getter calls |
|---|---:|---:|
| Source policy with matched probe, no physical target fault | 26 | 0 |
| Blind optimistic executed-ACK assumption | 23 | 0 |
| Blind pessimistic held-ACK assumption | 20 | 0 |
| Public empirical evidence ONLY; refuse if ambiguous | 19 | 0 |
| **Public evidence OR one target-state readback** | **27** | **11** |
| Compulsory true target read after identical probe | **27** | **32** |

The public classifier returned **21/32** unique accepted histories with **zero observed wrong confident execution-history labels** on those 21 selected cases. All other 11 conditions required a clearly accounted true target-state read, reducing observed privileged decision getter use by **21/32 (65.625%)** relative to mandatory once-per-condition readback. Critically, the hybrid and mandatory arms had identical **per-condition binary task-success flags on all 32 conditions** (zero paired exclusive successes either way). This is *observed finite-cohort parity*, not statistical proof of equivalent performance or a safe-to-deploy zero-error actuator observer. The underlying classifier error envelope came from four calibration reset seeds per task and is not an attested physical dynamics tolerance.

**Limitations as positive scientific evidence:** although matched per-condition task outcomes strengthen the information-efficiency narrative, 21/21 correct accepted labels is too small to demonstrate a future zero-misclassification rate under iid or distribution shifts. The confidence selectively excludes 11 conditions; incorrectly confident future accepted histories remain plausible. A real network could delay or reorder execution, and the tested common neutral probe changes physical time, contact state and observation history, so comparisons must use the identical probe. This hybrid does **not** combine the bounded two-history command compiler of Section 4C with the empirical response classifier in one evaluated policy; presenting their best numbers together as a single method would be invalid.

**Primary immutable evidence:** [pre-outcome commit fa173507 and protocol](https://github.com/lindicaphxag-tech/ManiSkill/commit/fa17350711f6c2c7cffb4cfa2bb7f8289f3ee0c4) · [original eight successful PhysX task jobs with full 32-condition denominator](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37834088246) · [complete six-arm positive AND failed per-seed table](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/frozen_policy_transfer/PUBLIC_RESPONSE_OR_READ32_ORIGINAL_RESULTS.md) · [trusted original JSON/log SHA-256 archive](https://github.com/lindicaphxag-tech/ManiSkill/tree/main/research/frozen_policy_transfer/evidence/public_response_or_read_fresh32) · [source-only audit and true-label check](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/audit_public_response_or_read32.py). All original task failures are retained.

## 5C. New decisive experiment: a shared, rather than merely approximate, observation budget

The first timing comparison in Section 4C used 17 adaptive and 16 pre-scheduled authority observations. Merely proving post hoc that deleting one read would change no more than one task is not a physical counterfactual policy execution; moreover, adaptive reads occurred at different steps than pre-scheduled probes. A source-frozen nine-arm follow-up therefore fixes 64 completely new reset states (PullCube 360001–360032, StackCube 370001–370032), the existing PPO/controller and 0.05 m / 0.05 rad authorization bounds, and a **shared entitlement budget of two real target reads per ascending 8-seed batch**. The precommitted fixed schedule consumes exactly two reads in each batch (16 across eight); the evidence-triggered method consumes a token only on certifier refusal, otherwise continues with a legal bounded command, and must refuse rather than exceed two reads in its shard.

This new policy has a **strict maximum of 16 reads**, but may spend fewer. It is an identical allocated **budget cap**, NOT guaranteed identical realized cost; the per-shard budget is an artificial cross-episode experimental allocation, not one robot's local constraint. The prospective run and audit are described in [original frozen protocol and nine-arm implementation PR #96](https://github.com/lindicaphxag-tech/ManiSkill/pull/96). **No new performance number may be inserted into this subsection before all original eight native PhysX chunks and the full 64-state denominator audit complete.** Every negative outcome, unused read token, quota-induced stop and physical/controller mismatch must be retained.
## 6. Relation to prior work and novelty vetoes

ActionShift (Attri, 2026) already isolates hidden compositional action-interface contracts—permutation, sign, scale, reference frame, target convention, gripper mapping and lag—and implements belief/probe and learned adapter baselines. Its released PPO checkpoints are the *external task policies used in this study*, not inventions or retrained backbones of this paper. Its active probe methods have not been evaluated in a matched-information head-to-head under our exact ambiguous acknowledgement fault; accordingly no claim of superiority over ActionShift's belief adaptation can be made.

Online system identification and belief-space active sensing are established fields. Both the box-Chebyshev positional midpoint and two-orientation geodesic midpoint are existing geometry. SPACE (2026) studies learned online robot-specific action adaptation, and TAM (CoRL 2026) studies a reusable torque-level adapter. The distinctive testable component here is an explicitly **authority-bearing commanded-target history interface** that admits error-bounded common actions, conditional requests for target-state observations, and concrete fail-closed evidence checks. Its novelty relative to all prior history-aware controller/action-interface research remains open to external literature and maintainer review.

References:

- [Attri, *ActionShift: Hidden Compositional Action-Interface Adaptation*, open repository and current benchmark](https://github.com/Archerkattri/actionshift).
- [ActionShift public frozen PPO source checkpoints](https://huggingface.co/kattri15/actionshift-baselines).
- [SPACE, 2026](https://arxiv.org/abs/2606.24049).
- [TAM low-level torque adaptation, CoRL 2026](https://dongwon-son.github.io/tam-project-page/).
- [Jaulin, set-membership estimation, *Automatica* 2009](https://doi.org/10.1016/j.automatica.2008.06.013).
- [Hibbard et al., action/perception over finite beliefs, *Automatica* 2023](https://doi.org/10.1016/j.automatica.2023.111140).

## 7. Reproducibility, next tests and claim boundary

Any outside researcher can clone the public project and immediately inspect the actual original files, reproduce the query arithmetic and run the exact paired hypothesis test using **standard-library-only Python**:

```bash
git clone https://github.com/lindicaphxag-tech/ManiSkill.git
cd ManiSkill
python research/frozen_policy_transfer/review/verify_stateful_abi.py
python research/frozen_policy_transfer/review/paired_query_stats.py
```

These calls reproduce the **evidence audit**, not the simulator. An independently executable original-policy PhysX workflow with explicit model hashes, native source code, complete seed records and experimental constraints is documented in [the independent-replication guide](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/frozen_policy_transfer/INDEPENDENT_REPLICATION_QUICKSTART.md). No independent research group has yet reported successful reexecution or incorporated the adapter upstream.

Three decisive prepublication gates remain:

1. **Matched-information competitors:** implement or adapt ActionShift's own active-probe/belief methods to exactly the applied-vs-held native command fault, using equal policy checkpoints, task states, real actuator time and *the same* privileged target-read budget. Without this, comparative algorithmic novelty is weak.
2. **External memory evidence, not synthetic confidence:** replace the simulator-assumed complete two-history set with a measured asynchronous command-ack/target-state observation interface with message loss, delay, reorder, age bounds and fail-closed anti-replay guarantees. Record incomplete-set false authorizations, refusal rates and query response latency.
3. **Task-sensitive failure control:** test contact-phase deviations and a *precommitted* high-risk query rule on genuinely fresh seeds, distinguishing task failure due to acceptable bounded setpoint errors from lost ACK, downstream learned policy failure and native action saturation. Hard collision/force/actuator-tracking safety is not established.

### Exact present-tense claim

*An owner-run, preregistered ManiSkill study finds that under a specific unknown-execution/target-hold fault model, an evidence-gated bounded common native action with selective privileged target readback reduced decision-time target queries from 64 to 15 while attaining 60 versus 57 task successes across 64 distinct source-policy task seeds. The success-rate difference is not statistically established; a 32-condition counterexample shows selective readback may perform worse under another execution truth. The result concerns commanded setpoints in simulation, not authenticated physical safety or new underlying robust-optimization mathematics.*

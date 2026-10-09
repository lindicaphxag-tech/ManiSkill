# When Should a Frozen Robot Policy Read Hidden Controller State? Evidence-Gated Action Authority under Unknown Execution

*Working-paper manuscript v0.5 · 9 October 2026 · Not peer reviewed, not submitted, and not independently reproduced.*

## Abstract

A robot policy's apparently valid action vector may have a different physical meaning when one controller increments motion from the achieved end-effector pose but the destination accumulates commands from a hidden previous target. Missing delivery acknowledgements further make the controller history ambiguous. We investigate an evidence-gated action interface that chooses between authorizing a common bounded commanded-target action, obtaining authoritative target state, and refusing. For two candidate histories, native position and orientation authorization uses a bounded positional Chebyshev center and shortest-geodesic SO(3) midpoint, with explicit controller-chart representability checks; these optimizations are existing mathematics, not new theorems. We test unchanged externally released PPOs on genuine ManiSkill PhysX PullCube/StackCube tasks with a controlled target-hold and unknown-ACK intervention. In 64 preregistered original states, selective querying achieved 60/64 tasks using 15 privileged target reads compared with 57/64 tasks and 64 reads for compulsory querying (paired p=0.453). Another prospective 64-state comparison with a preregistered fixed 16-read schedule found 58/64 successes using 17 adaptive reads versus 47/64 with 16 fixed reads (12:1 exclusive paired successes; exploratory unadjusted exact p=0.00342); thus read *timing* can matter, but actual read spending was only approximately matched. A separate, preregistered hybrid combining public achieved-motion classification with a conditional authoritative read recovered 27/32 distinct fault-truth conditions using 11 reads versus the mandatory-readback comparator's 27/32 using 32. Its empirical dynamics envelope is not hardware-trusted and its 21 accepted public-history labels do not establish a zero-error guarantee. Finally, a completely new prospectively frozen 64-state nine-arm **strict shared read-budget** study made 50/64 tasks with 10 capped adaptive reads versus 44/64 with 16 fixed reads; **its preregistered hard fault-exposure gate FAILED** because one StackCube source state generated unrepresentable target rotation before any fault injection in seven comparison arms. The full denominator and refused actions were preserved; the exact paired 9:3 comparison (p=0.146 exploratory) is descriptive, not a confirmed superiority result. These positive and negative findings jointly motivate treating typed native-action admissibility, controller memory evidence and actual information-access cost as independently auditable control contracts. No claim is made of real hardware safety, novel robust-geometry mathematics, ActionShift active-probe superiority, external reexecution or paper acceptance.
### 2026-10-09 addendum — cross-embodiment public-response *calibration* portability

A separate original genuine CPU PhysX source cohort used **two native robot morphologies**, Panda and **real xArm6 Robotiq articulation**, with distinct maintained target controllers. [Original source and all 32 native-physical truth rows](./evidence/cross_robot_online_public_proprio_new32_480001_490008/) were prospectively acquired on 16 new reset seeds, each paired across actual `applied` and `held` physical ACK truths. Each public-only model corrected the native commanded target **POSITION** in 16/16 test cases per robot after robot-specific eight-seed-pair prior calibration, with zero observed confident ACK mistakes. These controls use **scripted native commands, not frozen PPO task-policy transfer, not restored full SO(3), not collision safety**.

To test the important hidden transfer assumption, we subsequently conducted a **RETROSPECTIVE source-hashed reanalysis**, not additional real PhysX execution. Applying the fully fitted Panda motion-response model unchanged to xArm6, and vice versa, produced **0/32** unique confident ACK labels (**32 refusals**) across the archived source-test data. The held/applied response prototype locations differed between robots by ~2.66 mm and ~4.90 mm respectively, large relative to the original ~2–2.5 mm per-class historical response radii. Re-centering the two prototypes with **ONE prior target-robot labelled reset seed pair** (that is **TWO known physical delivery-truth calibration executions**, not one unlabeled demonstration) yielded **32/32 correct** historical classifications, **zero wrong/confident mistakes in this observed data**. This is a low-variance, *fixed-amplitude*, post-hoc **sample-efficiency hypothesis**, not a prospective two-example adaptation guarantee. [Pure stdlib exact archived-source full-denominator auditor, Python 3.11 and 3.13 green](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37909589936) · [public source PR #118](https://github.com/lindicaphxag-tech/ManiSkill/pull/118).

**Necessary active falsifier of that promising-but-easy original result:** a truly new Pandora/xArm6 **action-amplitude OOD** native PhysX study with **32 originally precommitted robot×scale×seed×execution-truth conditions** has been registered [before simulator code or outcomes](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/cross-robot-action-scale-prospective-20261009/research/CROSS_ROBOT_ACTION_SCALE_32_PRECOMMIT_V1.json). It tests native known command amplitudes 0.6 and 1.35 times the original, two heldout robot seed cohorts 610001–610004 and 620001–620004, and six genuine controller-world comparators, including foreign-zero-shot, one-paired-seed fixed response, an **explicitly hypothesis-driven affine action-conditioned response model**, two blind histories, and one privileged read. [Actual-source CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37910505997). **Original new PhysX results, now FULLY COMPLETE AND SOURCE ARCHIVED:** [four genuine simulator shards and independent audit GREEN](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37910505997) · [all five BYTE-UNCHANGED original JSONs, original all32 audit and source SHA256 manifest](./evidence/cross_robot_action_scale_ood_new32_610001_620004/) · [source-locked method PR #122](https://github.com/lindicaphxag-tech/ManiSkill/pull/122) · [source-pinned permanent archival CI GREEN](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37911099681).

| SAME physically executed Panda/xArm6 true-controller scenarios, 32 source truth states | Commanded target XYZ restored within 0.0001 m | Wrong confident hidden-ACK decisions | Privileged decision reads |
| --- | ---: | ---: | ---: |
| Unchanged foreign-robot response model | 0/32 (32 refusals) | 0 | 0 |
| ONE target-robot paired calibration seed, FIXED action response | 16/32 (16 refusals) | 0 | 0 |
| **SAME paired calibration, ACTION-CONDITIONED response model** | **32/32** | **0 observed** | **0** |
| Blind optimistic assume-applied | 16/32 | 16 | 0 |
| Blind pessimistic assume-held | 16/32 | 16 | 0 |
| One privileged controller-target read after the identical native zero probe | 32/32 | 0 | 32 |

At the two prospectively frozen real physical command scales (0.6 and 1.35), heldout Panda seeds 610001–610004 and xArm6 Robotiq seeds 620001–620004, the rigid 1-paired-seed baseline refused 16 altered-amplitude commands. The *registered before outcome* affine, action-conditioned class response `mu_applied(scale)=mu_held+scale*(mu_applied(1)-mu_held)` made 32/32 source cases uniquely identifiable, and *actual post-PhysX native commanded target POSITION* was independently audited as restored within 0.0001m. This new cohort involved **8 genuinely new robot-reset states ×2 action scales ×2 actual physical command-truth conditions =32 source comparisons**. Its six comparator arms produced 192 separately stepped native simulator controller worlds, **not** 192 trained or independent PPO models. Each target robot's two historical labels were learned using exactly one earlier paired reset seed (two known execution-truth PhysX observations); this training supervision is NOT free.

**Crucial publication boundary:** these are **scripted PickCube native-controller COMMAND-TARGET POSITION outcomes** on two robot/controller implementations, not PickCube official manipulation task completion, frozen PPO cross-robot adaptation, SO(3) target restoration, contact-safe execution, or robust physical system identification under variable latency/controller gain. The prior calibration evidence and this cohort motivated a specific simple affine model; only two action amplitudes and four new reset states per robot were prospectively tested. Zero observed wrong confident labels does not imply safety on new command families or a new universal theorem. This experiment strengthens the controller-observability *mechanism*, but it cannot be pooled with PullCube/StackCube PPO task-success studies as an independent task-policy success count.

This contrast matters because evidence-gated action authority assumes not only an observable robot response but also a **valid action-conditioned observation model**. In a different robot or under changed command amplitude, a previously useful empirical probe can become **unidentifying**; refusing or spending trusted state-read budget is then appropriate. The original response classifiers are not learned VLA foundation models, and this experiment cannot be used to claim broad embodied generalization.

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

## 4.3. Query timing versus query count

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
## 5. Diagnostic evidence outside the task-success headline

Independent native Panda controller audits show the commanded-target translation and joint-position compiler agreements with official execution on preselected task/seed pairs. A native three-world replay creates identical joint configurations and achieved end-effector poses but different legitimate commanded-target histories through the official controller state API; a copied command produces roughly 2 cm commanded-target error, while full-memory inversions recover a common desired target. This is a **controlled counterfactual state replay**, not a claim that such hidden states are naturally frequent or indistinguishable when full target telemetry is supplied.

A distinct native joint-target audit on **Fetch (7 arm joints, 13 native action dimensions)** and **xArm6 Robotiq (6 arm joints, 7 native dimensions)** validates the conditional additive target-memory setpoint model on two other simulated embodiments. It is NOT a learned policy task-transfer result across those robot embodiments.

These auxiliary source-controlled studies establish some chart and observability assumptions of the proposed compiler. They do not measure actual force, collision clearance, unsafe stopping distance or hardware tracking.

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

**Primary immutable evidence:** [pre-outcome commit fa173507 and protocol](https://github.com/lindicaphxag-tech/ManiSkill/commit/fa17350711f6c2c7cffb4cfa2bb7f8289f3ee0c4) · [original eight successful PhysX task jobs with full 32-condition denominator](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37834088246) · [complete six-arm positive AND failed per-seed table](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/frozen_policy_transfer/PUBLIC_RESPONSE_OR_READ32_ORIGINAL_RESULTS.md) · [trusted original JSON/log SHA-256 archive](https://github.com/lindicaphxag-tech/ManiSkill/tree/main/research/frozen_policy_transfer/evidence/public_or_read_new32_180101_190108) · [source-only audit and true-label check](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/audit_public_response_or_read32.py). All original task failures are retained.

## 5C. New decisive experiment: a shared, rather than merely approximate, observation budget

The first timing comparison in Section 4C used 17 adaptive and 16 pre-scheduled authority observations. Merely proving post hoc that deleting one read would change no more than one task is not a physical counterfactual policy execution; moreover, adaptive reads occurred at different steps than pre-scheduled probes. A source-frozen nine-arm follow-up therefore fixes 64 completely new reset states (PullCube 360001–360032, StackCube 370001–370032), the existing PPO/controller and 0.05 m / 0.05 rad authorization bounds, and a **shared entitlement budget of two real target reads per ascending 8-seed batch**. The precommitted fixed schedule consumes exactly two reads in each batch (16 across eight); the evidence-triggered method consumes a token only on certifier refusal, otherwise continues with a legal bounded command, and must refuse rather than exceed two reads in its shard.

This new policy has a **strict maximum of 16 reads**, but may spend fewer. It is an identical allocated **budget cap**, NOT guaranteed identical realized cost; the per-shard budget is an artificial cross-episode experimental allocation, not one robot's local constraint. The prospective run and audit are described in [original frozen protocol and nine-arm implementation PR #96](https://github.com/lindicaphxag-tech/ManiSkill/pull/96). **No new performance number may be inserted into this subsection before all original eight native PhysX chunks and the full 64-state denominator audit complete.** Every negative outcome, unused read token, quota-induced stop and physical/controller mismatch must be retained.
## 5D. NEW negative original test: exact budget entitlement fails the pre-fault admissibility gate

The earlier timing study in Section 4C compared 17 adaptive reads against 16 source-state-independent reads. An additional *prospectively frozen* experiment gave both controllers a stricter, identical **two-read entitlement per predefined eight-trial block** (eight nonoverlapping blocks, at most 16 reads across 64 states). To prevent any post-outcome allocation, shard order was frozen ascending by seed, and the certificate-triggered policy spent a token only on a real target-bound rejection. The fixed schedule spent exactly two reads per block whenever its fault step was reached. New, disjoint task-state seeds were PullCube `360001–360032` and StackCube `370001–370032`; both frozen third-party PPO checkpoints and all original 0.05 m/0.05 rad target bounds were unchanged.

The frozen experimental contract was committed **before implementation**, in Git revision [`a47fb2b7`](https://github.com/lindicaphxag-tech/ManiSkill/commit/a47fb2b7eedcb90803bebe4845d47082b1a279da) (immutable protocol object `8394481a560ea3d0c538e9d2ebf46cc9c4949484`). Nine actual physical simulator arms were preselected. The original first attempt [37895572472](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37895572472) encountered an unhandled source/native rotation impossibility, **not** an ordinary clean fault-recovery result. An evaluator-only fail-closed patch captured and recorded that exact invalid action as a failure without altering source seeds, PPOs or tolerances. This patch was implemented AFTER that first failure, so the subsequent complete run cannot be described as an untouched, original confirmatory execution.

| Native experiment on all 64 original new reset states | Official task successes | True-target decision reads |
|---|---:|---:|
| Source frozen PPO, no injected target hold | 57/64 | 0 |
| Continuously privileged target-memory oracle | 61/64 | Repeated access, not free |
| Optimistic ACK assumption | 39/64 | 0 |
| Exact-common-action or refuse | 0/64 | 0 |
| Two-history bounded action, no queries | 41/64 | 0 |
| **New strict entitlement-capped evidence query** | **50/64** | **10 / allowed ≤16** |
| Fixed seed-modulo schedule | 44/64 | 16 |
| Uncapped evidence-triggered query | 56/64 | 19 |
| Once-per-fault privileged target read | 60/64 | 64 |

The capped-versus-fixed paired exclusives were **9 versus 3**, exploratory exact two-sided p=`0.14599609375`; even without the gate failure this does not establish a statistically significant task-success advantage. More importantly, **the prespecified complete fault-exposure gate was broken**. At StackCube seed **370029**, seven comparison arms generated a normalized rotational command which their strict action-history observer classified as **not representable** at `t=0`, BEFORE the prescribed physical fault at `t=2`; each arm **refused** instead of injecting the fault. Thus the relevant seven arms received only **63/64 intended physical fault exposures**, although ALL 64 reset states remain in the denominator and the comparison arms' failures are preserved in the original original raw rows.

This is an *important reproducible counterexample*, not a success result to hide. It exposes the distinction between componentwise normalized action bounds and a rotational joint ball (an admissible orientation control needs `||u_rot||₂≤1`, not simply `|u_rot,i|≤1`). Clipping an otherwise invalid command without recomputing both rotation setpoint error and accumulated controller memory can violate the assumed target-update contract. The new gate orders checks as `(i) evidence source and chart identification → (ii) complete valid native action representation → (iii) certified target-setpoint error → (iv) actual acknowledgement/physical step`; violation at stage (ii) cannot be credited as successful stage (iii) uncertainty recovery. This requirement is not itself a new theorem, and an independent head-to-head with existing ActionShift hard action masks is still missing.

**Numerical mechanism identified after the complete experiment.**
The seven StackCube failures share a recorded `float32` proposed
rotation-action norm of `1.0000009536743164`. The earlier source
conversion accepts a marginal `norm <= 1+1e-5` without performing
its radial normalization, while the history tracker evaluates the
transported coordinates in `float64` and rejects if
`norm > 1+1e-6`. An independently reproducible float32 three-vector
`[0.5773508548736572]*3` evaluates to precisely
`1.0000009536743164` in float32 but `1.0000010144344997`
after float64 promotion, straddling the gate. The historical
JSON stored the norm but not the three original coefficients,
so this is an exact *mechanism-level* reproducer, not proof of
identical unlogged source vector components.
The failure therefore implicates inconsistent numerical precision
and tolerance across converter/observer, not simply a missing
rotation-ball limit in the converter. A separately developed
[typed native-action admissibility prototype](https://github.com/lindicaphxag-tech/ManiSkill/pull/103)
tests the actual transported float32 radial ball, returns NONEXACT
for any explicitly projected action and recomputes resulting target
pose error for every history candidate before authorization.
It has no independent task-success evidence and was not used
to modify these original negative 64 trials.
**Statistical and accounting decision:** treat this new capped-budget study as **descriptive/negative** only. An exactly shared cap of 16 authorized observation tokens is NOT equal number of actual private reads (10 vs 16), and the invalidated full-fault gate vetoes a confirmatory study-wide efficacy claim. The original first failed CI and fixed-evaluator second completed CI must remain distinct sources; same-seed repeats must not inflate sample size.

[Original source and negative evaluator-veto results](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/frozen_policy_transfer/STRICT_BUDGET16_NEW64_NEGATIVE_RESULT.md) ·
[first, failed PhysX CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37895572472) ·
[completed, fully audited eight-shard PhysX CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37896670586) ·
[original full files, terminal logs and SHA-256 directory](https://github.com/lindicaphxag-tech/ManiSkill/tree/main/research/frozen_policy_transfer/evidence/strict_shared_16read_quota_new64_negative).

**Highest-leverage follow-up:** freeze new seeds and implement controller-typed joint/rotation chart feasibility in all online adapters BEFORE any command is sent; require prospective source competence and fault-exposure coverage, then compare certificate-triggered and genuinely strong active-belief/probe policies with both equal actual information consumption and matched physical probing time. A negative result against existing baselines is as important to publish as a win.
## 5E. Previously unseen 64-state double-ACK falsifier and the mandatory task-only baseline

The original two-history single-fault result should not automatically generalize to **two consecutive ambiguous native command deliveries**. Two sequential target-hold faults at `t=2,3` can create four legitimately possible commanded-controller target histories. The native common-action geometry may still authorize a small-error setpoint, yet the policy may fail a contact-rich task because **state uncertainty does not shrink under identical common actions**, and trajectories/grasp phase can differ from those of a one-read recovery.

### Original 64-state double-ACK evidence from a distinct, earlier cohort

In an earlier source-frozen seven-arm PhysX study with PullCube seeds `420001–420032` and StackCube `430001–430032`, the **fully reactive** K=4 bounded controller succeeded on **45/64 with 44 privileged target reads**, while a controller using **one true target read at a fixed early step** succeeded on **55/64 with 64 reads**. The paired failures favored EARLY readback by **13:3** on original reset states (exploratory two-sided exact McNemar `p=0.021270751953125`, not multiplicity adjusted or independent learned policies). A 0-read bounded controller succeeded on **11/64**. The original source logs and complete negative cases are archived in the [64 original-state strong-baseline analysis](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/frozen_policy_transfer/ORIGINAL_64_STRONG_QUERY_TIMING_BASELINE_AND_INVARIANT.md). The result is a significant **warning against** promising that geometric-certifier-driven read timing is generally task optimal; one early query can prevent late failure even when the setpoint error certificate has not refused.

Inspecting those previous outcomes led to a **deliberately simple posthoc DEVELOPMENT-only rule:** run the reactive controller on PullCube (where both strategies completed 32/32) and fixed early-read controller on StackCube (where fixed was better). The chosen rule was then publicly **frozen before execution** on an entirely disjoint 64-reset-state cohort: PullCube `520001–520032` and StackCube `530001–530032`. This prevents posthoc selection on the new target outcomes, but it does not make the initial development task choice independent of prior evidence.

### PRE-FROZEN NEW prospective eight-shard PhysX test of the simple baseline

| Seven actually PhysX-stepped control worlds (64 new task states) | PullCube | StackCube | Pooled successes | Privileged decision target reads |
|---|---:|---:|---:|---:|
| No-fault released PPO reference | — | — | **59/64** | 0 |
| Privileged continuous true-target oracle | — | — | **59/64** | Continuous private access, not zero |
| Optimistic assume both commands applied | — | — | **2/64** | 0 |
| Exact common action or refuse | — | — | **0/64** | 0 |
| Bounded K=4 common action, never query | — | — | **12/64** | 0 |
| Reactive bounded K=4, query only on certificate failure | **32/32** | **15/32** | **47/64** | **39** |
| Fixed early true target-state query for both tasks | **32/32** | **26/32** | **58/64** | **64** |
| **Pre-selected task-only route: reactive for Pull, fixed for Stack** | **32/32** | **26/32** | **58/64** | **56** |

**This simple task-based baseline is the scientific control our mechanism must beat.** It achieved the exact same 64 binary task success/failure outcomes as unconditional fixed early readback while spending eight fewer privileged reads (12.5% reduction). There are zero paired discordances in the original finite cohort. Zero discordance **cannot** prove noninferiority or clinical/robot safety equivalence without a precommitted effect margin and sufficient independent task instances. Further, task-specific routing is not a newly learned online decision policy: it selects a **whole actually executed comparator trajectory before reset**, based solely on task ID. Every one of the seven controller arms was separately stepped in real ManiSkill PhysX for each original state; an eighth fused physical controller was **not** secretly run and there are no within-episode causal trajectory splices. This is a legitimate validation of the restricted, task-preselected decision rule under shared per-episode resets, not broad unseen-task transfer.

The frozen new-state runner checks four credible target memories in relevant native fault worlds, two actual physical target-hold events, identical third-party pretrained PPO checkpoint hash/revision, the original controller and certifier source Git blobs, and the prior chosen task identity rule. The separate reviewer audit checks **all 64 exact original source rows across eight shards**, each source/raw SHA-256, actual target reads, no posthoc route changes, no fault omissions in operational arms and the entire per-seed task-success vector. Its adversarial unit suite rejects omitted failures, altered task routes, fake free oracle reads and missing second physical hold.

[Original pre-outcome task-only selection protocol](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/TASK_GATED_MULTI_ACK_FRESH64_V1.json) · [all eight successful genuine PhysX source jobs](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37904539256) · [original Git archive, SHA256 and independent full-denominator audit](https://github.com/lindicaphxag-tech/ManiSkill/tree/main/research/frozen_policy_transfer/evidence/task_gated_double_ack_64_520001_530032) · [two-Python no-GPU adversarial audit CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37905338100) · [trusted-main archival source CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37905586372).

### True external replication and prior-art gate

A reviewer can run **new, independently chosen eight state seeds** with all seven originally stepped native controller worlds on a separate organization-owned GitHub fork through [one-click K=4 frozen-policy workflow](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/.github/workflows/external-task-gated-k4-physx.yml). The runner is pinned to the EXACT earlier committed original-method Git blob even though unrelated main-branch experiments changed the mutable source afterward; native PPO checkpoint SHA is verified and complete input manifest, source, log, results, and hashes are emitted. The author-owned preflight has been tested, but **no third-party scientist has reported actual reproducibility yet**.

**ActionShift prior art matters:** the released source-Policy donor project's **DualABI** already actively selects bounded probes by task regret and stops before complete belief identification. It reports comparable task success with lower probe cost across its own benchmark. Those **probe steps/displacements are not the same cost unit as our privileged controller target-state reads**, and DualABI identifies a hidden compositional action *mapping* under its pool/likelihood assumptions rather than only the execution/ACK branch of an already known mapping. Neither the generic principle of task-relevant active information seeking nor the risk/entropy comparison is a new contribution of this study. [ActionShift original source](https://github.com/Archerkattri/actionshift) · [DualABI published active-regret controller](https://github.com/Archerkattri/actionshift/blob/master/src/actionshift/adaptation/dualabi_adapter.py).

**Unmet publication bar:** adapt DualABI (or its exact-belief and active probing class) to exactly our controller memory/ACK fault with the same public observations, physical probe duration, action bounds, query cost, both fault truths and native time horizon; compare on NEW unknown tasks/robots, not task IDs previously used to pick the rule. Without that, we cannot claim global state-aware information selection superiority or independent external adoption.
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

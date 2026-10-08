# Evidence-Gated Stateful Action Transport under Ambiguous Command Acknowledgements

*Working-paper manuscript v0.1 · 9 October 2026 · Not peer reviewed, not submitted, and not independently reproduced.*

## Abstract

A robot policy can emit geometrically valid actions that become semantically incorrect when transferred from an achieved-pose-relative controller to one that increments its previous commanded target. The mismatch is particularly problematic when an earlier action's execution is unknown: the achieved end-effector pose alone may be compatible with several controller target histories. We study a narrow alternative to either assuming that execution succeeded or always requesting privileged controller state. An interface-level observer retains two plausible previous target poses, decodes the frozen source policy's intended physical goal, and computes a single native action whose worst-case commanded-target position and orientation discrepancies remain below declared bounds. Unrepresentable actions or unsupported beliefs trigger one authoritative target-state query or refusal. The positional optimization reduces to box-constrained Chebyshev projection; the two-orientation construction uses a shortest-geodesic SO(3) midpoint. These geometric facts are not new theorems. In a preregistered, author-operated ManiSkill PhysX study using two independently released third-party frozen PPO checkpoints, 64 new PullCube/StackCube reset seeds and a controlled zero-arm-target-delta fault, selective querying completed 60/64 tasks using 15 privileged target reads, versus 57/64 tasks with 64 reads for mandatory single-read recovery. No-query bounded control completed 47/64, and an optimistic ACK assumption 42/64. The exact paired two-sided discordance test between selective and mandatory query gives p=0.453; the observed success difference does not establish superiority or noninferiority. Additional applied-versus-held-command fault tests identify a failure where certifiable setpoint error does not preserve contact-manipulation task success. We release full source-pinned per-state results, executable audits, and independent-reexecution instructions. The present evidence concerns simulated commanded targets and information use, not authenticated physical acknowledgements, real-robot safety, or cross-platform task-performance generalization.

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

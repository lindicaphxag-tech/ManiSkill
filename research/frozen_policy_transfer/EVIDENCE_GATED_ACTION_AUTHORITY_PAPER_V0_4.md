# When a Command Is Not a State: Evidence-Gated Authority for Frozen Manipulation Policies
## Manuscript v0.4 · original data and falsification-first revision · 9 October 2026

**Status.** Research draft, NOT submitted or peer reviewed. Original externally released frozen PPO checkpoints, native ManiSkill CPU PhysX tasks, contributor-operated experiments and public source-hashed artifacts. No real hardware, no outside laboratory replication and no official upstream-maintainer adoption. This version deliberately promotes new counterexamples into the central abstract rather than hiding them in an appendix.

## Abstract (196 words)

A manipulation policy may output the same action coordinates under two controller interfaces while producing different physical targets: some robot controllers accumulate commands relative to an internal target rather than the achieved end-effector pose. Unacknowledged commands further make that target history ambiguous. We study *evidence-gated authority*: maintaining explicit candidates for a controller's commanded target, authorizing a bounded shared action only with verified action-frame semantics, and using an authoritative target read when current evidence does not justify continued conversion. In two frozen third-party PPO tasks, an initial prospectively specified 32-condition PhysX study preserved all paired task outcomes of compulsory readback (27 successes each), using 11 rather than 32 privileged reads. Yet larger and harder prospective tests reveal an important limitation. With two consecutive unknown acknowledgments and four candidate target histories, geometry-triggered readback succeeded in 45 of 64 new reset states with 44 reads, whereas a fixed earlier read succeeded in 55 with 64 reads. Thirteen StackCube states favored the early-read strategy; eight prompted no geometric query despite task failure. We separately verify target-history reconstruction on Panda and xArm6 native controllers, without claiming cross-robot frozen-policy task success. These findings separate controller-setpoint correctness, latent-state evidence, and manipulation task progress, and motivate a falsifiable task-phase-sensitive query policy. They are not a hardware-safety theorem or a claim of universal advantage.

## 1. The actual gap: authorization, delivery, and task progress are not the same variable

The source PPO issues an achieved-relative action based on its observation. Its destination may be a persistent-target interface. Define the achieved end-effector pose `x_t`, the commanded controller target `h_t`, the source-policy action `a_t`, the *native* destination action `u_t`, and the unknown execution indicator `z_t`:

```
desired source setpoint:   d_t = G_source(x_t, a_t)
physical native command:   c_t = F_native(h_t, u_t)
controller memory update:  h_(t+1) = c_t if z_t = 1, else h_t
available command evidence:  ACK_t may be unknown even when z_t is fixed
```

For two unknown execution events, a target-history belief may contain up to four distinguishable candidate targets. Under a complete and trusted controller semantics contract, a single chosen `u_t` can be checked against each candidate's intended commanded-setpoint bound. However, that is **only an action/target certificate**. It is neither a proof that the command was physically delivered, nor a certificate that object grasping, placing or release succeeded.

**Design principle:** an action may have a valid syntax and a bounded commanded-goal error yet lack task-continuation authority because the evidence is stale or the physical interaction has progressed to an unrecoverable phase. A dynamic *read-before-contact* decision is a testable hypothesis; it is not yet established by the archived geometric-only runs.

### Three distinct claims requiring different evidence

| Claim type | What evidence would justify it | What is NOT established |
| --- | --- | --- |
| **Typed native command admissibility** | Verified controller chart; source action boundaries; legal translation BOX and rotation L2 BALL; actual commanded-target residual after native `env.step` | Collision avoidance, contact forces, stable task completion |
| **Hidden controller target history** | Known initial target; verified update law; acknowledged delivery, or bounded set of all possible deliveries; trusted readback when needed | Unobserved actual ACK truth magically inferred by geometry |
| **Task completion** | Same-seed independent true simulator worlds; public object/task progression; official task success flags; paired target-read cost | Guarantee from a setpoint error inequality alone |

## 2. What is already genuinely validated, without mixing cohorts

Each row below references an independent original experimental population. An experiment with two physical fault truths for the same reset seed is a paired counterfactual population, not twice as many independently trained policies.

| Experiment | Real registered task cases | Observed controller/task outcome | Limitation |
| --- | --- | --- | --- |
| Frozen third-party policy with fully known command ACKs | 64 new states | Independent command-history observer reproduced full-memory binary outcomes in **57/64**; achieved-pose substitute **11/64** | Reliable delivery acknowledgment assumed |
| Unknown ACK, public response + conditional privileged target read | 32 task × actual-truth conditions, 16 distinct reset seeds | **27/32** conditional and **27/32** compulsory, same paired binary outcomes; **11 vs 32 privileged reads** | Empirical physical-response envelope can exclude true history |
| Unknown ACK, naive public-response nearest-target classifier | 32 task × actual-truth conditions | **15/32 WRONG confident history predictions** | Correct task outcome is not latent-state identification |
| **Two consecutive unknown ACKs, four possible targets** | **64 NEW task reset states**, seven native controller arms per state | **45/64** geometry-triggered successes / **44 reads** vs **55/64** fixed-early successes / **64 reads** | STRONG negative evidence against geometry-only query timing |
| Two unknown ACKs with separately predeclared 16-case geometry intervention | 16 task seeds | selective **11/16 using 7 reads** vs compulsory **16/16 using 16** | All-arm complete second-fault exposure gate failed for exact-refusal arm |
| Panda + xArm6 different robot/URDF/control packing | 8 + 8 new native PhysX controller seed states | Observed command target prediction error no greater than **1.431×10^-8 metres** on both; observed held/applied trajectories differ | Controller-level only; NO frozen policy task transfer to xArm6 |

**Primary physical source for the decisive 64-state negative:** [original all-shard source experiment](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37900209486) · [original archived per-shard bytes and independent 64-case audit](./evidence/compound_ack_64_original_native_physx_420001_430032/) · [per-seed reproducible loss-mechanism audit, PR #112](https://github.com/lindicaphxag-tech/ManiSkill/pull/112).

**Positive, strictly scoped 32-state evidence:** [public-response-or-query unchanged original source](./evidence/observability_gated_query_fresh32/) · [corrected independent original-source audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833936506).

**Cross-robot native-controller evidence:** [unchanged Panda+xArm6 actual PhysX source, SHA-256 and 16-case independent auditor](./evidence/cross_robot_panda_xarm6_original16_420001_430008/) · [original exact six-job native PhysX](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37899544825).

The 64-state experiment had 448 actually simulated controller worlds, 1,530 genuine post-dispatch bounded-setpoint checks, and 192 intended-but-fault-masked commands expressly excluded from claims about executed certificates. These are NOT 448 different independent learned PPOs or external tests.

## 3. The central negative mechanism

The larger prospective two-ACK cohort isolates the StackCube gap:

| StackCube 32 original reset seeds | Successful tasks | Privileged controller target reads |
| --- | ---: | ---: |
| Geometric setpoint-error-triggered read | **13/32** | 21 |
| Fixed earlier target read at step 4 | **23/32** | 32 |

The paired contrast is **13 fixed-only successful, 3 selective-only successful, 10 both successful, 6 neither successful**. A two-sided exploratory exact paired sign test is `p=0.021270751953125`, **unadjusted** for researcher attention to this subgroup, competing cohorts and method exploration.

Of the **13 fixed-only** original StackCube outcomes:

- **Eight** geometric controller episodes spent **zero** private target reads. The continuation gate continued to regard commands as bounded.
- **Five** geometric episodes spent one private target read but still failed the task; the original source does not establish whether the read happened after a specific irreversible contact event.
- **All thirteen** geometric controller worlds proceeded to the original task's full 50-step time limit without official success, whereas the fixed-read comparator succeeded. The full raw source includes each command's legal bound checks and actual fault bookkeeping.

This is a **direct falsifier of setpoint-bound ≈ task-recovery equivalence**. It is not proof that contact forces rather than gripper changes or a different policy trajectory caused each failure. The next algorithm must therefore observe *task interaction phase or evidence freshness* and be tested in **new prospectively selected physics scenes**.

## 4. Constrained prospective next method and a deliberately strong simple opponent

A preliminary *public precontact/interaction-phase gate* is separately precommitted on fresh **PullCube 470001–470008 and StackCube 480001–480008** seeds, with nine actual native PhysX controller worlds each and the same TWO unknown ACK faults. It checks object-to-TCP/source-target proximity from the **simulator full-state object observation** already present in source-policy state; this is not camera perception. A heuristic 0.10m threshold is frozen **before** results; ambiguity near a possible physical interaction should force an immediate single trusted target read. Otherwise retain the original conservative geometry-or-one-read policy.

The control that this new method **must beat** is not an easy no-query strawman. A **task-ID prior** simply uses a fixed early read for StackCube and geometric triggers for PullCube. When composed **after** seeing the original 64 cohort, the two arms would yield 55/64 successes and 55 reads with matched original potential outcomes. **This composition was NOT originally run as a physical controller and is NOT a prospective new method result.** The new nine-world experiment runs it for real, side-by-side with the proposed precontact gate. We will not claim a task-stage innovation if the new contact heuristic merely matches or loses to this simple prior.

[Locked pre-implementation protocol for the new 16-case study](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/phase-sensitive-authority-prospective16-20261009/research/PRECONTACT_AUTHORITY_NEW16_PRECOMMIT_V1.md) · [new genuinely physically executed workflow](https://github.com/lindicaphxag-tech/ManiSkill/actions/workflows/precontact-authority-vs-task-prior-new16.yml). **No positive result for this new policy should be claimed until its separate source audit has passed.**

## 5. Mathematical scope and limitations

In an additive translated-target controller, for candidate histories `h_1, h_2` and any *common* action `u`, the relative separation is unchanged: `(h_1+u)-(h_2+u)=h_1-h_2`. Therefore repeatedly executing known same additive commands alone does not resolve unknown target-memory identity. With root-left rigid rotations a comparable left-invariant relative rotation statement holds under the assumed chart, but controller clipping and other compositions can violate simplified premises. These are **standard elementary observations**, not proposed new theorems.

The setpoint bound controls an *intended controller goal* under an assumed chart and complete candidate set. It does not constrain contact impulse, collision distance, PPO distribution shift or nonlinear grasp success. A `0.05 m` bound is not a robot safety guarantee. A four-seed-trained achieved-motion tolerance is not an independently certified physical response interval. The exact gate must refuse or escalate when assumptions are absent.

We deliberately avoid claiming a new general POMDP, a new geodesic minimax algorithm, the first action adapter, hardware-safe transfer, practical source policy transfer to xArm6, published peer review or external laboratory adoption.

## 6. Nearest prior work and remaining genuinely difficult comparisons

**ActionShift:** an existing public project on hidden action-interface contracts and learning/probing under interface mismatch, which supplies the released frozen PPO weights used here. A strong paper must make a real **same-problem, same-information-cost head-to-head** against its adaptation algorithms, not simply cite it as a model source.

**SPACE and cross-embodiment adapters:** adapting state/action representations to different robots is not new. The current distinct focus is hidden **commanded target history provenance** and physically unknown execution acknowledgments within native target-control semantics. The observed Panda+xArm6 cross-controller command invariance is a supporting mechanism check, NOT an evaluated fully trained cross-robot policy.

**Task-phase information-value controls:** task-ID fixed-read prior, equal-budget random/fixed schedules, contact-stage/gripper-phase public-state triggers, and cost-aware adaptive evidence acquisition are all essential comparisons. A method which only has a lower numerical read count but substantially worse task completion must not be marketed as a universal advance.

## 7. What would materially change outside recognition

The shortest credible path is **not** another ten owner-operated fork PRs. Give an independent robotics group an exact runnable native PhysX workflow and let them choose new seeds. Record negative cases, full original source JSON and git SHA. Also submit one **maintainer-sized, reusable controller semantic contract regression** to an upstream project if its scope matches; an unreviewed open PR or an author-fork merge is not external endorsement.

**Public reproducibility:** [source-hashed reviewer audit](./review/compound_ack_failure_witness_64.py), [one-click outsider-selected task/seed runner](https://github.com/lindicaphxag-tech/ManiSkill/actions/workflows/external-observability-gated-query-replay.yml), [cross-robot fixed-controller geometry experiment](./evidence/cross_robot_panda_xarm6_original16_420001_430008/).

**Paper gate still missing:** independently reproduced physical task-level second-controller policy, fair existing ActionShift adaptation baseline, and a prospectively demonstrated phase-sensitive evidence policy that beats a task-ID-only schedule under a declared cost/success objective. Until then, the strongest defensible contribution is a **precise evidence-versus-task-progress problem, a controller history artifact, real counterexamples and a falsifiable proposed method**, not a top-conference result already achieved.

---
**End v0.4.** All task numbers and links represent finite, author-operated experiments. No future or in-progress outcome has been silently counted.

# Survivor-Conditioned Controller Authority Under Unknown Command Execution

**Research manuscript / external-reviewer first read · v0.7 · 9 October 2026**

**Status:** independent contributor research in a public ManiSkill fork; **not submitted, not peer reviewed, no real robot deployment, no outside-lab replication, and not an official ManiSkill maintainer merge.** The results are source-audited owner-run actual official ManiSkill CPU PhysX. This is a **method experiment**, not a newly trained VLA.

## Abstract

A frozen robot policy can issue numerically valid actions with incorrect physical meaning when a destination controller accumulates commands from its *previous commanded target* rather than the measured achieved pose. Missing execution acknowledgments create several possible commanded-target histories. We investigate **survivor-conditioned action authority**: use a public robot-motion observation to eliminate inconsistent complete target-pose histories; when exactly one full state remains, inherit its paired position and orientation rather than synthesizing an orientation or requiring the rotations of discarded histories to agree. Otherwise, make one counted authoritative controller-target query. The method uses a fixed, historically calibrated—but **not independently certified**—physical response envelope and a preregistered minimum separation margin. In a newly frozen 32-reset-state PullCube/StackCube experiment after two actual native zero-arm holds with unknown acknowledgments, eight independent physical frozen-PPO controller strategies were executed per seed (256 genuine PhysX controller worlds). Public evidence selected **10/32** full-pose histories without privileged readbacks, with **zero observed wrong confident selections**; the hybrid adapter achieved **28/32** tasks using **22** target-state reads. A strong, **actually executed task-ID preselected query policy** achieved the *identical 28 successful and four failed original seeds* with **27** target reads; compulsory t4 querying used **32** reads. This demonstrates conditional information savings in the studied simulator, **not** statistical noninferiority, general SE(3) identifiability, contact safety, or superiority to existing ActionShift belief/probe adapters. An earlier independent cohort showed empirical response-model exclusions; an intentionally conservative prior rule rejected every public identification. All original successes, failures, physical faults and archival hashes are exposed.

## 1. Exact problem: knowledge of native controller target

Let the source frozen policy emit `a_t=π(o_t)`. A measured-achieved-relative interface may decode a source motion with the current end-effector pose `x_t`, while an accumulated-target native controller applies a delta to its internal **commanded** target `h_t`. After a missing execution acknowledgment, the adapter cannot know whether the previous actual native command was executed. With two unknown acknowledgments, a candidate set can contain up to four **complete** target states `H_t={(p_i,R_i)}`, where `R_i∈SO(3)`. Treating `h_t` as `x_t` is not a semantics-preserving converter.

The required controller contract distinguishes (i) *the originally intended action*, (ii) *the command physically delivered*, (iii) *the hidden controller state actually reached*, and (iv) the evidence authorizing the next command. A geometry certificate for (i) is **not** proof that (ii) occurred or that trajectory contact forces remained safe.

## 2. New, deliberately conditional public survivor rule

For the same known-delivered native t3 physical hold common to all arms, let `x,y` denote public achieved position before/after the held step. With complete native action-history candidate `h_i=(p_i,R_i)`, define the **historical empirical** compatibility residual

```
r_i = min_{alpha in [0,1]} || y - x - alpha(p_i - x) ||_2.
C = {i : r_i <= epsilon_task}.
```

The predeclared epsilon is **0.00694426256 m** for PullCube or **0.00719087966 m** for StackCube, fixed before this new cohort; neither is a physically attested deterministic plant bound. No new reward model, PPO finetuning, extra control step or online calibration occurs.

**Authorize** one complete pose history only when `|C|=1`, all alternatives have `r_j>epsilon_task+0.002m`, every stored quaternion/frame/history is valid and finite, and physical observation provenance is verified. Use the existing selected candidate's **entire** `(p_i,R_i)`. If the model fits zero or multiple candidates, or the evidence is invalid, **query exactly one authoritative native target and reset the history**.

**Conditional full-pose identification fact (existing finite-set logic):** if the full set of hypotheses contains the actual state and a valid public response model leaves exactly one hypothesis compatible, its **index** identifies the complete stored pose, even if excluded poses have different rotations. This does **not** mean public XYZ measurements independently recover an arbitrary unknown orientation. It can fail if the model is misspecified or the target-history set is incomplete.

An older, preregistered conservative rule additionally required `R_i` to agree across **all** histories—including histories already eliminated by public XYZ. It accepted **zero of 32** histories in an earlier source cohort. After the outcome was exposed, independent SHA-pinned *retrospective* reanalysis found 12 old states with unique position-compatible survivors, and all 12 matched after-run full-pose truth; this is **hypothesis motivation, never counted as prospective success**. [Original retrospective source SHA audit (Python 3.11/3.13)](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37914630239).

## 3. Prospective actual native-physics study and full source evidence

The *new method* was registered before its source implementation: [frozen protocol at commit 1f68f3d](https://github.com/lindicaphxag-tech/ManiSkill/commit/1f68f3d788525e555b9170437161554a20138cde). It selected PullCube seeds **860001–860016** and StackCube seeds **870001–870016**, two distinct unchanged externally released ActionShift PPOs, two consecutive injected **real native zero-arm-delta target holds** (t2 and t3) whose acknowledgments were UNKNOWN to the adapter, and eight genuinely stepped robot controller arms for each reset seed. The implementation includes an after-physical-step *audit-only* true target getter, never supplied to the public-history decision, and an explicit log for each private **decision** read.

| Controller arm, identical 32 frozen task reset states | Official task success | Privileged controller target reads |
| --- | ---: | ---: |
| **Survivor-conditioned full target history or one trusted read** | **28/32** | **22** |
| **Strong task-labelled preselected policy**, selective on PullCube / fixed t4 on StackCube, separately physically executed | **28/32** | **27** |
| Mandatory actual target read at t4 | **28/32** | **32** |
| Bounded approximate common action, zero read | **6/32** | **0** |

**Zero paired success discordances** versus the strong task-labelled comparator: both succeeded on **28** identical original seeds, both failed on **4** identical original seeds. **10/32** model-approved, originally action-history-derived *complete* target poses; zero observed wrong confident full-pose history labels; all 32 registered public-controller arms received both native t2/t3 physical fault interventions. Full original run: [37914343195](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37914343195) (all eight physical task shards + independent complete denominator audit green).

**Important task-stratified heterogeneity (all 32 original source states, NO selective exclusions):**

| Task stratum | Public unique full-target histories | New method task success / target reads | Strong task-aware comparator task success / target reads |
| --- | ---: | ---: | ---: |
| PullCube (16 resets) | **3/16** | **16/16, 13 reads** | **16/16, 11 reads** |
| StackCube (16 resets) | **7/16** | **12/16, 9 reads** | **12/16, 16 reads** |

**The aggregate five-read advantage is NOT uniform across tasks.** PullCube spends TWO MORE trusted target reads than its strongest genuinely executed task-labelled alternative, whereas StackCube saves SEVEN. This is a task-heterogeneous controller-state information frontier; any paper claim of uniform reduced query cost is FALSE. The matched task outcome is identical separately in BOTH task strata. Source: [permanent original full-denominator PhysX audit](./evidence/survivor_fullpose_original32_860001_870016/full_original_survivor_fullpose_new32_audit.json).

**Protocol amendment honestly disclosed:** the first physical attempt [37913956732](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37913956732) interrupted several sharded episode outputs due a Python `NameError` in the *after-actuation audit-only* variable that graded true candidate histories. One binding restoration (`winners=ev["accepted_position_indices"]`) corrected the source, with exactly the same observed-state method, original preregistration and source reset seeds. [Disclosure](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/SURVIVOR_FULLPOSE_FIRST_RUN_SOURCE_AMENDMENT.md). The full successful run is an *implementation-repaired preregistered cohort*, not independent untouched confirmatory replication.

### Actual information-cost sensitivity, not a hidden free-observation claim

The new arm acquires **two explicit public achieved-XYZ samples per seed** (64 samples in 32 trials), while the task-ID preselected strategy need not explicitly request those additional samples; the actual native physical step and PPO observation pipeline are otherwise matched. In a simple **descriptive**, post-outcome cost model `C = c_q × privileged_reads + c_p × additional_public_samples`, the observed new-minus-task-aware information cost is

```
Delta C = -5 c_q + 64 c_p.
```

Thus the new method is lower cost in this finite cohort only if the marginal public observation costs less than **5/64 = 0.078125** of one privileged controller-target read under this specified accounting. If public proprioception is already in a cached policy observation, marginal cost may be tiny; if it requires a new synchronizing sensor/actuation cycle, the benefit can disappear. This conditional fact is not a learned optimal query policy or a generic deployment cost model.

### Observed uncertainty and statistical interpretation

The methods are task-matched and seed-paired, but **28/32 = 28/32 with no discordances is not statistical population equivalence**, and the exact sign test gives no support for general superiority. Ten zero-wrong confident decisions are not evidence of a universal false-authorization probability of zero. The same earlier historical physical response model was falsified on a separate unseen condition, so the geometric rule's soundness cannot be inferred for different gains, contact states or controller families.

## 4. Essential related work and strongest remaining objections

- [ActionShift](https://github.com/Archerkattri/actionshift) already studies *hidden action contracts*, online Bayesian beliefs, bounded probe adaptation, task regret, abstentions, and exact (pool-based) model knowledge on frozen PPO and diffusion backbones. The present study does **NOT** invent action-contract adaptation, belief-state probing or query efficiency as a field. **Direct same-information ActionShift/DualABI baseline comparisons are not yet performed.**
- [SPACE](https://arxiv.org/abs/2606.24049) already studies state/action adaptation across embodiments. Our Panda controller-memory study is not evidence of general cross-embodiment frozen PPO manipulation success.
- Prior classical finite-set system identification and robust control already contain the conditional unique-candidate logic. Our experimentally falsifiable niche is **controller-target provenance under genuinely unknown prior native command execution, and conditional evidence cost**.
- A separate original Panda/xArm6 Robotiq experiment achieved 64/64 **native commanded-target POSITION corrections** under different command amplitudes, but with scripted commands and no frozen PPO task success. It cannot be pooled with the present 32 task episodes or described as learned policy transfer to xArm6.
- Another genuine 32-condition four-history PPO study using the *older conservative all-candidate SO(3) agreement rule* had **zero** publicly accepted history labels and mandatory readback on every task. It was not a fair same-seed matched head-to-head with the new method.

## 5. What would make this a genuinely competitive ICRA / CoRL submission?

1. Repeat the **unaltered** new rule on a completely new and explicitly sealed 32–128 task reset-seed cohort, with preregistered domain/plant shifts and realistic controller servo gains; quantify confident misidentification and model-falsified true histories, not just binary success.
2. Test an actually transferred competent frozen policy on a DIFFERENT robot/controller family (e.g. xArm6/Fetch) rather than relying on scripted target corrections.
3. Compare against ActionShift's strongest task-aware and entropy/DualABI probers with **matched public sensory samples, actual probe-actuation budget, privileged reads, time horizon and controller chart knowledge**.
4. Acquire one true **external investigator's own-fork result** with complete fresh-seed raw JSON and failure witnesses. Self-fork merged PRs, stars, CI checks or an unreviewed issue are not outside adoption.
5. Investigate online **model-mismatch / contact-stage certification**: historical `epsilon_task` already failed on a different task seed. Until separately attested, no hardware/collision safety or formally certified physical target identity is claimed.

## Reproduction entry points

- [Actual 32-task source and independent full-denominator audit #37914343195](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37914343195).
- [Preregistered exact source protocol](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/SURVIVOR_CONDITIONED_SO3_NEW32_PRECOMMIT_V1.json).
- [Compact full-pose selection implementation](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/survivor_full_pose_public_gate.py).
- [Actual 8-arm frozen PPO runner](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/frozen_ppo_survivor_full_pose_new32.py).
- [Independent all-32-source auditor](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/audit_survivor_fullpose_new32.py).
- [Clean research artifact merged into the author's fork #129](https://github.com/lindicaphxag-tech/ManiSkill/pull/129).
- [Original byte-unchanged evidence archival workflow](https://github.com/lindicaphxag-tech/ManiSkill/actions/workflows/archive-survivor-fullpose-new32-original.yml). This must be checked for GREEN completion before treating the archival copy as permanent.

**End of v0.7 — Author-operated simulation, current flagship candidate, not a published or externally accepted paper.**

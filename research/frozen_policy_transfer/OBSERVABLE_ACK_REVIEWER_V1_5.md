# When Did My Robot Command Execute? Public-Motion Evidence for Latent Controller-Target Memory

**Research manuscript / reviewer-first technical summary v1.5 · 9 October 2026 · NOT peer reviewed, accepted, real-hardware validated or independently replicated.**

**Proposed authorship is not claimed by this repository file.** All PhysX experiments below were author-operated. The earlier ActionShift/ActionABI teams must be credited for their published baselines and active-probing ideas.

## Abstract

Frozen visuomotor policies can issue valid action vectors that become semantically incorrect when the destination robot controller composes motion around a previously commanded target rather than the achieved end-effector pose. With unknown delivery acknowledgements, multiple target-memory histories can explain the same policy command. We study two linked but distinct questions: when can public kinematics identify the hidden history without a controller-private read, and what changes when an authoritative read updates the belief state but leaves a stale execution-branch decision? A command-conditioned set-membership observer uses pre-calibrated physical response intervals and command histories, abstaining when public evidence is ambiguous. In a pre-registered Panda/xArm6 native PhysX study with 64 applied/held fault truths and 256 independently stepped control worlds, it restored the actual commanded target **position** in 64/64 cases at unseen 0.55×/1.45× command magnitudes, versus 32/64 for a frozen fixed-amplitude response observer. This mechanism comparison does not equalize public feature representations. In a separate 32-state frozen-PPO study with two unknown ACKs, conservative XYZ-only four-history inference authorized 0/32 histories, required 32 private fallbacks, and provided no task-success improvement. A further prospective 64-state, 640-controller-world study isolated a stale post-read cache-branch confound in an earlier benchmark: after canonical cache invalidation, a phase-aware route matched fixed-query task success (56/64 each), while using 56 rather than 64 decision-time private reads; on StackCube, both methods emitted equivalent 7D native action traces across all 32 paired states. These results establish a limited observable target-memory recovery mechanism and a reproducible controller-resynchronization consistency test, **not** VLA performance, hardware safety, a certified physical response bound, independent external replication, or an improvement in official task success against the corrected fixed-read opponent.

## 1. Formal problem and scope

Consider an unchanged source policy `a_t=π(o_t)`. Its destination native controller remembers a commanded target `M_t`, with known transition `M_{t+1}=F(M_t,u_t,z_t)` where `z_t∈{applied,held}` is command-delivery truth. With an unknown ACK, the observation history supports multiple potential `M_t` values; the controller is not entitled to select one simply because its commanded action was valid.

The method must distinguish three distinct questions:

1. **Executable?** Does the transmitted native action satisfy the true controller representation, including root-left orientation conventions and the normalized SO(3) rotation unit ball? Reject invalid commands before attempting belief repair.
2. **Identifiable?** Given the known command chart, prior calibrated motion-response assumptions and *only public achieved poses*, can a physical probe separate latent histories?
3. **Worth doing?** Does an extra public probe improve task completion versus a scheduled state read under the *same* information/actuation cost? **Not yet answered by the present new OOD study.**

For a known-delivered neutral target-delta probe with before/after public achieved XYZ `x,y`, the conditional response model is

`y = x + α (M_h-x) + e, α∈[α_min,α_max], ||e||₂≤ε`.

Each history `h` predicts a line segment of possible public observations, inflated by an error radius `ε`. A **conditional unique-history witness** requires that the true public observation fit exactly one segment while all other candidates are inconsistent. A pre-action probe-disjointness certificate can use a conservative lower bound on the pairwise separation of these segments; with overlapping tubes, even an optimal one-observation classifier cannot uniquely certify every underlying history. All such conclusions explicitly depend on the response envelope's validity. The currently measured finite-sample envelopes are NOT independently attested deterministic physical guarantees.

**Distinctive engineering contract:** the decision must never access simulator `controller.target_pose`. Source-code hypotheses come from old known native command history and known controller chart; all hidden state getters occur strictly *after* actual physical correction for evaluation. A query, if used by a future combined policy, must be separately logged and costed.

## 2. Main physically stepped amplitude-OOD experiment

The [untouched pre-outcome protocol](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/ack-ood-native-amplitude-falsifier-20261009/research/OOD_ACK_PUBLIC_MOTION_PROSPECTIVE_V1.json) was committed before any new trials. The model source, actual tested runner, eight original native PhysX shards, entire population audit, and original ZIP digest can all be traced from the [first fully successful **10-job PhysX run**](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37909760484).

**Physical design:** two ACTUAL different robot articulations and gripper-action ABIs, Panda and xArm6 Robotiq; each tests fresh robot-specific initial seeds at **two command magnitudes, 0.55× and 1.45×**. In each robot×amplitude cell, eight new distinct initial seeds are paired with two *physically stepped* execution truths, `applied` and `held`. Therefore 32 distinct robot×amplitude×initial-state resets create 64 ACK truth conditions, and **four separately stepped comparator controls per truth** create 256 actual native controller worlds. Both native states are hidden from the in-loop adapter. No frozen PPO checkpoint or task success is evaluated in this study.

The four controls share a fixed native fault/probe timing and final native corrective-actuation opportunity:

- Original previously calibrated two-class **fixed-amplitude achieved-motion** classifier (frozen, no new calibration), refusing on zero or multiple compatible classes.
- Candidate-command-aware **empirical gain-segment model**, frozen on an older **separate** source-audited set of physically measured robotic responses; it uses target hypotheses derived from the known native command history and measures the public before/after *neutral* probe.
- Always-assume-command-applied, physically execute one corrective action.
- Always-assume-command-held, physically execute one corrective action.

**Original independent audit (full denominator, all negative rows):**

| Physically stepped unseen robot/amplitude | Gain-segment model | Original fixed-motion model | Always applied | Always held |
|:--|--:|--:|--:|--:|
| Panda / 0.55× (16 hidden truths) | **16/16** | 8/16 | 8/16 | 8/16 |
| Panda / 1.45× (16) | **16/16** | 8/16 | 8/16 | 8/16 |
| xArm6 Robotiq / 0.55× (16) | **16/16** | 8/16 | 8/16 | 8/16 |
| xArm6 Robotiq / 1.45× (16) | **16/16** | 8/16 | 8/16 | 8/16 |
| **All original 64 physically exposed cases** | **64/64** | **32/64** | **32/64** | **32/64** |

The result is **actual commanded-target XYZ recovery** within `1e-4m` after physical native correction, not latent-label prediction alone. The original fixed classifier **abstained 32/64** and made **0 wrong confident labels**, which must not be conflated with 32 wrong actions. Each always-guess baseline was confidently wrong in 32/64 cases. The gain-segment model had no observed wrong confident labels or abstentions in these 64 cases.

**Fairness boundary:** both empirical classifiers have zero decision-time *privileged controller target-state* reads and each physically executes the same predetermined neutral probe timing; however, the new gain method consumes an **additional public before-probe achieved-state sample and command-conditioned action-history information**, rather than the identical fixed historical displacement feature of the old model. The robot-specific calibration set size and calibration representation also differ. Accordingly, the table is a fully real native-physics **mechanism stress-test**, not a matched-information competition against a sufficiently strong ActionShift belief/probe method and not a robustness guarantee for arbitrary fault magnitudes.

The original full 64-case JSON archive and SHA256 ledger are prepared by a separate source-pinned archival workflow: [archive verifier](https://github.com/lindicaphxag-tech/ManiSkill/actions/workflows/archive-ood-ack-amplitude-original64.yml). Do not advertise the archival freeze until its successful run.

## 3. Other supporting evidence; do not pool unlike experiments

1. The original naive public achieved-pose nearest-target heuristic wrongly selected the hidden delivery history **15/32 times** in real native PhysX; task completion cannot validate latent-history identification [full negative study](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/frozen_policy_transfer/PHYSICAL_RESPONSE_32_NEGATIVE_RESULT.md).
2. A 64-reset-state true double unknown-ACK *frozen PPO task* experiment **falsified** blanket adaptive-query superiority: history-triggered 45/64 success with 44 target-state reads versus fixed-t4 55/64 with 64 [original audit](https://github.com/lindicaphxag-tech/ManiSkill/pull/110).
3. A separate preregistered **64 frozen PPO tasks** physically executed a task-labelled *pre-reset* route: **58/64 task successes with 56** privileged controller reads, matched to **58/64 with 64** fixed-t4 reads [original source report](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/frozen_policy_transfer/TASK_GATED_MULTI_ACK_FRESH64_EVIDENCE.md). **Historical descriptive observation only:** it neither incorporated a public probe nor resolves the local post-read control-flow confound documented below; do not assign a causal benefit to query scheduling until a semantics-equivalent comparator is tested.
4. The original Panda+xArm6 fixed-amplitude online hidden-ACK **physical target correction** was 32/32 with public motion vs 16/32 for each guessing baseline, without frozen PPO task success [source PR #114](https://github.com/lindicaphxag-tech/ManiSkill/pull/114).
5. A **different new preregistered** real-PhysX population at original 1.0× and smaller 0.4× found that a command-amplitude-affine two-class response mean restored **32/32** physically stepped commanded target positions vs **24/32** for the frozen fixed mean, again not frozen PPO tasks [source PR #117](https://github.com/lindicaphxag-tech/ManiSkill/pull/117), [full source execution](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37909644806).

6. A separate **prospectively registered 32-state** PullCube/StackCube task experiment used *actually physically stepped* double native target holds and **256** independently executed PPO-controller comparator worlds. The XYZ-only, orientation-conservative, four-history public-motion observer had **0/32 confident authorizations**, required **32/32** fallback private target reads, and achieved **24/32** official task successes—identical to its fixed-t4 target-reader (also 24/32, 32 reads). The preselected task-labelled route achieved **24/32 with 26 reads** and the never-query arm **8/32**. These are paired outcomes on this particular cohort, NOT support for a better observer or a safe failure-rate guarantee. [Immutable pre-outcome protocol and original full-denominator source audit](https://github.com/lindicaphxag-tech/ManiSkill/pull/125).
7. The later **prospectively registered, now fully completed**, 64-state ten-arm (640 independent native PhysX worlds) canonical intervention **isolated the actual stale-read implementation confound**: legacy fixed readback held a cached `maybe_two=True` even after authoritative resynchronization, while phase-aware readback invalidated that local cache. Under a corrected one-line canonical fixed control, task success was **56/64**, matching phase-aware **56/64**; the historically buggy fixed comparator scored 53/64. PullCube was **32/32 vs 32/32**, with phase-aware using 24 versus 32 private reads; StackCube was **24/32 vs 24/32**, both using 32 reads. Across all 32 StackCube paired states, matching timing and belief produced matching dispatched native 7D control action traces (maximum per-step absolute difference ≤1e-6 as source-audited). There were **zero paired task-success discordances** against the corrected comparator; an exploratory exact paired p=1 is NOT proof of statistical equivalence or broad task generalization. Full [10/10 original PhysX CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37914020907), [permanent original-source archive, SHA256 and all failure records](https://github.com/lindicaphxag-tech/ManiSkill/tree/main/research/frozen_policy_transfer/evidence/canonical_post_read_original64_970001_980032), [source re-audit + tamper tests](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37915107133). **The former phase-over-buggy-fixed 3-success advantage was an implementation confound, not demonstrated query-policy superiority.**

Do NOT sum these numbers into trained policies, independent laboratories, or independent platforms. Several studies use the same two robot implementations, original script/controller architecture and prior calibration evidence.

## 4. Readback linearization: a falsifiable state-consistency mechanism

An authoritative read changes more than the estimated target value. Let `B_t` be the adapter's set of possible commanded-controller targets and let `c_t = g(B_t, o_t)` represent the control-flow decision cached for the current step. An authoritative measurement `M_t^*` must perform a **single logical transaction**:

```text
(B_t, c_t) <- ({M_t^*}, g({M_t^*}, o_t))
```

Updating `B_t` while continuing to execute the previously computed `c_t` is a **stale-branch state consistency failure**. This is an implementation-level invariant, not a novel robotics theorem or a claim that a target read is physically safe.

**Paired physical falsifier.** Two independently stepped controller worlds with the *same initial reset, released unchanged PPO and native controller*, the *same authoritative read at the same time*, and the *same post-read control compiler* should emit identical native action traces when cache invalidation produces the same logical control state. The original 32 StackCube trials verify this narrow invariant to 1e-6 on dispatched native 7D actions and agree on episode success and query count. In the deliberately retained buggy comparator, 3 StackCube successes were missing; that contrast must never be attributed to when the private read occurred.

**Generalization hypotheses, NOT established results.** The next method should expose readback as an atomic API or state-machine transition, preventing cached mode, certificate, action eligibility and target-memory values from referring to different epistemic versions. The resulting policy's actual task efficacy still requires independently registered trials on new robot/controller families. Even perfectly consistent commanded target-memory estimates do not validate contact forces, physical trajectories, collision avoidance or network-level packet acknowledgements.

**Strong competitor and precise claim.** A simple task-labelled query strategy from earlier development already matches full scheduled task success on two published policies while reducing private reads. The corrected canonical comparator matches the 56/64 task success on the present frozen 64-state cohort and consumes 8 extra reads. Thus the only new task-level efficiency result here is that narrow eight-read difference; no task-success benefit over a correctly implemented fixed-read policy has been established.

## 5. Primary next experiment: fair, prospective task-level identification-vs-query

Register previously unused real PhysX initial states **before** calibration/model modification. Train/calibrate any missing robot response validity checks on separate frozen development states; publish the exact controller/source/model hashes. Then run identical frozen PPO manipulation tasks under two unknown ACKs with:
- Fixed task-labelled early readback, the **strongest already genuinely run** 58/64/56-read opponent, rather than only naive guessing or always-read.
- Command-history-only bound/refuse and the original event-triggered policy (including negative outcomes).
- Public-probe-gated controller-history inference **integrated into real policy task rollout**, explicitly tracking model falsification and contact phases, wrong history authority, task reward, costly target reads, extra physical probe steps, latency and achieved physical disturbance.
- ActionShift-style exact-belief active probes under the same known contract prior, **same public motion history, same actuation opportunities and the same counted privileged controller-target read budget**.

A defensible stronger paper result must pass this actual full-population test, ideally on an independent robot/policy/controller family, and be reproduced by somebody else's fork or laboratory. Failure to improve against the trivial task-labelled regime must remain negative. Native setpoint correctness does **not** ensure safe collision/contact trajectories, motor torques, or external network loss handling.

## 6. Provenance and reproduction

- [Canonical corrected fixed-query 64-state original source and static-evidence archive](https://github.com/lindicaphxag-tech/ManiSkill/tree/main/research/frozen_policy_transfer/evidence/canonical_post_read_original64_970001_980032)
- [Canonical 10/10 real physical simulation experiment + independent complete-source audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37914020907)
- [Independent archival re-audit, nine pinned ZIP digests, five adversarial evidence mutations](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37915107133)
- [Fixed protocol and source, NEW 64-case OOD experiment](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/ack-ood-native-amplitude-falsifier-20261009)
- [Actual native Panda+xArm6 execution and source-independent all-case audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37909760484)
- [Earlier distinct Panda+xArm6 physically corrected ACK trial](https://github.com/lindicaphxag-tech/ManiSkill/pull/114)
- [Independent realistic stronger original hidden-ACK task query comparator](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/frozen_policy_transfer/TASK_GATED_MULTI_ACK_FRESH64_EVIDENCE.md)
- [ActionShift](https://github.com/Archerkattri/actionshift) / [ActionABI](https://github.com/Archerkattri/actionabi), whose belief updates, active probing and honest abstention are existing relevant ideas. This work claims no first use of such ideas.
- [Contributor-side outside reproduction invitation](https://github.com/lindicaphxag-tech/kaggle/issues/67). No independently credited lab replication as of this report.

**Positioning:** Evidence-driven recovery of latent *execution-history state*, with action admission and geometry-based identifiability, is a narrower and falsifiable mechanism than generic hidden action-contract adaptation. It is not yet proof of a general top-tier robotics method.

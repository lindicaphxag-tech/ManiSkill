# When Did My Command Execute?
## Discrete-History Public Evidence for Frozen Robot Policies under Ambiguous Acknowledgements

*Research manuscript v1.4 · 9 October 2026 · author-operated genuine PhysX evidence, not peer reviewed or accepted*

**Zhibo Zhang** · Hangzhou Dianzi University  
**Manuscript authorship and any collaborators must be confirmed before submission.**

### Abstract

Frozen robot policies can be transferred between end-effector interfaces only if the destination preserves the semantics of their actions. An achieved-pose-relative action and a command-target-relative action need not produce the same physical target, even when their numerical coordinates agree. The discrepancy becomes a partially observed control problem when a command may have executed but its acknowledgement is missing: each unknown acknowledgement adds possible histories of the destination controller's internal commanded target. We examine whether an adapter can use public end-effector motion to eliminate entire candidate execution histories instead of paying for a privileged controller-target read. The key distinction is **hypothesis-level observability**: a motion sample may uniquely identify one *complete* six-degree-of-freedom target history without requiring all competing histories to share an orientation. We couple a finite target-history observer and a native-action admissibility check with an empirically calibrated public-motion compatibility test; ambiguous observations trigger one explicitly counted readback, not an arbitrary guess. On 64 prospectively selected ManiSkill PhysX reset states with two consecutive unknown acknowledgements, unchanged third-party frozen PPOs and eight actually stepped paired controller policies, the proposed method completed **58/64 tasks with 39 privileged target reads**. A task-preselected strong early-query comparator completed the *same 58 task states* with **57** target reads. All 64 new-method trials encountered both intended physical target holds; the public measurement selected one of four complete histories in 25 trials with zero observed incorrect confident labels. An earlier, prospectively tested orientation-consensus guard selected none and required more reads than the task-aware comparator. The result demonstrates conditional information economy on this controlled task bank—not distribution-free state-identification accuracy, superior task success, real packet-loss handling, collision safety, or independent adoption.

**Keywords:** robot learning; controller semantics; latent execution state; command acknowledgement; set-membership identification; frozen-policy transfer; selective observation.

---

## 1. Problem: execution truth is neither action syntax nor observable tool pose

The third-party source PPO policy \(\pi\) issues an achieved-relative end-effector action \(a_t\) based on the observation \(o_t\). The destination's native `pd_ee_target_delta_pose` controller instead maintains a *previous commanded target* \(M_t\). With an uncertain execution indicator \(z_t\), the native target update can be written

\[
M_{t+1}=
\begin{cases}
F(M_t,u_t), & z_t=1,\\
M_t, & z_t=0.
\end{cases}
\]

A missing acknowledgement does not disclose \(z_t\). Two missing acknowledgements can therefore leave up to four distinguishable commanded-target histories, even when the action chart \(F\) is completely known. Using achieved pose as the previous commanded target, or treating silence as a successful execution acknowledgement, is not a logically justified reconstruction. For a frozen policy this can invalidate the meaning of every subsequent native command.

The question addressed here is deliberately narrower than discovering arbitrary unknown robot-action interfaces: *given a known native controller chart and complete candidate histories, when can an ordinary public motion measurement replace an explicit privileged target-state read without sacrificing observed manipulation-task completion?*

## 2. Method: identify a complete discrete history, not independent pose coordinates

Let \(H_t=\{h_1,\ldots,h_K\}\) denote the complete set of possible native commanded-target poses computed from documented initial-state evidence and acknowledged/unknown native actions. Each \(h_i\) contains **both** XYZ target position and a quaternion target orientation. No simulator-private actual target getter enters its construction.

A known-delivered neutral native target-delta is executed at the second unknown-ACK fault step. Let \(x\) and \(y\) be the public achieved XYZ positions immediately before and after that *actual* physical step. The frozen response model is

\[
y=x+\alpha(M_i^{xyz}-x)+e,\quad
\alpha\in[0,1],\qquad \|e\|_2\le\epsilon_{task}.
\]

For each candidate history \(h_i\), compute the minimum Euclidean residual \(r_i\) between observed \(y\) and the complete interval of public positions predicted by \(h_i\). The task-specific empirical model tolerances were frozen from different historical PhysX seeds: \(\epsilon_{Pull}=0.0069443\,m\) and \(\epsilon_{Stack}=0.0071909\,m\). No test-set calibration or PPO updates are allowed.

**Authorize the complete latent history index \(i^*\)** only when exactly one residual \(r_{i^*}\le\epsilon_{task}\), and **every** competing history has \(r_j>\epsilon_{task}+0.002\,m\). The chosen history includes its own full target orientation. It is *not necessary* that all possible histories have identical orientations. This is a straightforward finite set-membership compatibility result, not a novel identifiability theorem: if two candidate public observation sets intersect, no position-only classifier can guarantee differentiation for a shared observation.

If no unique history meets the predeclared test, the adapter reads the authoritative native target exactly once at step four and resynchronizes. Every actual native command remains subject to the existing 0.05m positional and 0.05rad orientation **commanded-setpoint** admission contract. An action may pass this contract without assuring trajectory tracking, safe contacts, or task completion.

The public measurement is not free: the new controller explicitly uses two achieved-XYZ samples per task. It adds **no extra actuated probe step**, as the measured motion occurs during the common physical fault protocol. The experiments count private target reads separately from public sample access, simulator audit-only target getters, and actual native action dispatch.

### Failure and observability boundary

Two histories with identical XYZ target positions but different target orientations are not distinguishable under the position-only response model above. More generally, an empirical motion envelope can fail when contact, load, phase, actuation delay or observation noise changes; an erroneously unique hypothesis can then be harmful. Our physical study records every such confident mistake against a private target getter **only after** real physical execution, never as the method's decision input.

## 3. Prospective experiment: 64 frozen PPO reset states, 512 physical controller worlds

The [protocol was fixed before new execution](../PPO_DISCRETE_HYPOTHESIS_NEW64_PREOUTCOME_V2.json) (Git blob `b8c5205ca949720a2d39396c9f8c711e65d7982b`), selecting PullCube reset seeds `840001–840032` and StackCube `850001–850032`. Both original third-party released PPOs and their SHA-256 hashes were checked before physical rollout. The action interface is the real ManiSkill Panda controller, with source `pd_ee_delta_pose` converted to destination `pd_ee_target_delta_pose`.

In each of 64 new reset states we stepped **eight separate actual native PhysX controller-policy worlds** with the identical reset seed and relevant native fault pattern: no-fault source context, fully privileged oracle, optimistic unknown-ACK assumption, exact-or-refuse, bounded zero-query, geometry-triggered selective query, fixed step-four authoritative read, and the new public-identify-or-read controller. Actual native target holds occur at steps two and three, with gripper unchanged and missing ACK conveyed to the adapter. The test represents a **physical zero/hold injection**, not genuine network packet loss; 64 separate reset states are not 64 independently learned policies or robot embodiments.

The principal non-strawman baseline uses a **frozen task-only rule selected before the new seeds**: choose the previously developed geometric selective-query policy on PullCube and the fixed step-four query policy on StackCube. The source code physically runs both competitors and selects the entire corresponding native trajectory per registered task before any outcomes. It does not splice favorable per-timestep results after observation.

Every trial is retained, including refusals and both injected faults. We separately record official task success, privileged controller target reads, the number and audit-only correctness of confident latent-history assignments, public XYZ reads, native setpoint checks and all injected command masks.

## 4. Main results

All eight physical execution shards and the **independent full-population source auditor** completed successfully. The actual original source execution is [GitHub Actions #37913661619](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37913661619).

| Actual native PhysX policy | Task successes /64 | Counted privileged target reads |
|:--|--:|--:|
| **Full discrete-history public evidence + selective authoritative read (this method)** | **58** | **39** |
| **Strong pre-registered task-dependent route** | **58** | **57** |
| Fixed readback at step four | 58 | 64 |
| Original geometry-triggered read | 46 | 42 |
| Bounded control without reads | 8 | 0 |

The new method and the strong task-gated comparator have **identical paired official task outcomes**: 58 states were successful under both, six failed under both, and neither strategy uniquely won a state. Their source-audited *actual* private read counts were **39 versus 57**, a reduction of 18 (**31.6%**) relative to this strong policy; against always-query, 39 versus 64 is **39.1%** fewer. The data do not show higher task success than the strong comparator, and a 64-state identical success vector is insufficient to establish general statistical noninferiority.

The observer encountered the intended two physical native target holds on **64/64** registered trials and observed four candidate history targets on each. It resolved a unique whole-history candidate in **25/64** cases (zero observed wrong confident identifications); the remaining 39 used one counted authoritative native target read. With fixed prior empirical parameters, the per-task physical observations were:

| Task | Public unique-history cases | New method / task-gated successes | New privileged reads | Task-gated privileged reads |
|:--|--:|--:|--:|--:|
| PullCube (32 states) | 15 | 32 / 32 | 17 | 25 |
| StackCube (32 states) | 10 | 26 / 26 | 22 | 32 |
| **Total (64 states)** | **25** | **58 / 58** | **39** | **57** |

*The above task-specific figures are reconciled from all eight original physical execution shards. For exact original per-trial data and independent auditor, use the source archive linked below.*

### The necessary negative control

Our previous **separately prospectively executed** 32-state task study required the rotation targets of *all competing hypotheses* to agree before permitting a position-only public witness. It produced **zero** confident identification, **24/32** real task successes with **32** privileged reads, compared with **24/32** successes and **26** reads for the strong task-aware comparator. All 32 true double native fault exposures were reached, so this is a genuine negative mechanism result rather than a failed injection campaign ([original 32-state raw evidence](evidence/public_fourhistory_frozen_ppo_original32_780001_790016/)).

A **retrospective, outcome-exposed** diagnostic of those old 32 original motion trajectories revealed 12 unique complete-history indexes with no observed false labels, but **no improved controller was actually executed on that old population**. The new 64-state trial was frozen afterward, on different new seeds, before implementing and executing the improved full-hypothesis admission rule. This preserves the distinction between hypothesis development and prospective task validation.

### Critical preregistered adversarial follow-up: fixed-fault-pattern shortcut

The original 64-state experiment physically replaced BOTH fault commands with zero native arm actions on EVERY faulted rollout. While the adapter received no acknowledgement, the generating fault truth was therefore **deterministically HELD** rather than a mixture of executed and held commands. A trivial comparator maintaining a controller target under an `always-held` assumption might recover with **zero hidden-target reads**, even when it is scientifically incapable of handling an actually executed command. This is a serious **evaluation shortcut/confound**, not an acknowledged theoretical guarantee.

We have prospectively registered a fresh follow-up on **64 completely different reset states**, with the first native ACK physically **APPLIED in 32 trials** and **HELD in 32 trials** (balanced within each task), and the second command physically HELD to keep the existing public zero-delta response observation comparable. A newly added, **separately physically executed** zero-read always-assume-held adapter is included alongside the frozen public-observer method and the task-selected strong read comparator. All comparisons are stratified by actual native delivery truth. This is a strictly narrower experiment than four independently sampled two-fault outcomes, which remain untested.

[Protocol frozen before mixed-ACK PhysX execution](../../MIXED_ACK_TRUTH_PPO_NEW64_PREOUTCOME_V1.json) · [source-owned nine-controller PhysX experiment](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37915263314) · [Draft research PR #130](https://github.com/lindicaphxag-tech/ManiSkill/pull/130).

**Interpretation policy:** The 58/64 with 39-vs-57 reads above remains factual for the original **both-held** simulation population. Until the mixed-truth source audit is complete, it cannot establish robust recovery of an unknown *realized* ACK. A mixed-truth failure must remain in the next manuscript; no cherry-picking the held stratum or changing the physical parity schedule after outcomes.

## 5. Limitations and comparison with related methods

Our geometrical observation-set test draws on standard set-membership reasoning. Existing [ActionShift](https://github.com/Archerkattri/actionshift) and [ActionABI](https://github.com/Archerkattri/actionabi) studies already investigate action-interface identification, belief updates, active probes and abstention; this work does not claim to invent those broad concepts. The narrower empirical target is an **otherwise known action ABI with missing execution truth**, in which the prior commanded target is a state variable distinct from observed achieved pose.

All positive and negative experiments are **author-operated within ManiSkill CPU PhysX**, mostly on the same Panda robot and two released PPO policies. The public-response tolerances are prior empirical samples, not a certified deterministic world-model envelope. Our environment deliberately masks arm commands at known steps; it does not simulate real network transport, arbitrary interrupted execution, delayed bursts, contact-force safety or robot hardware. The new method receives additional public achieved XYZ samples, so the cost comparison is explicitly about **privileged hidden target reads**, not total system information or exact wall-clock computation. Full SE(3) proprioceptive models, contact-dependent disturbances, task-general active-query opponents and genuinely independent laboratory/fork re-executions remain unproven.

In particular, 25 correct observed history labels are not proof that the probability of a wrong confident assignment is zero on new systems, and zero paired discordances on 64 trials are not proof of task noninferiority under an arbitrary population shift. A strong ActionShift-style alternative given the same public motion samples, actuation opportunities and query cost must be executed before making any state-of-the-art comparison claim.

## 6. Reproduction, negative evidence and external reviewer challenge

- **Full new64 source-frozen actual physical experiment and 10-job independent audit:** https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37913661619
- **Original source/data archive (17 original PhysX JSON and SHA256SUMS, when automated archival is complete):** [full new64 original source evidence](evidence/discrete_hypothesis_ppo_original64_840001_850032/)
- **Fresh-run original protocol and physical controller source:** [PPO_DISCRETE_HYPOTHESIS_NEW64_PREOUTCOME_V2.json](../PPO_DISCRETE_HYPOTHESIS_NEW64_PREOUTCOME_V2.json), [frozen_ppo_discrete_history_v2_physx.py](../frozen_ppo_discrete_history_v2_physx.py), [independent source auditor](../audit_public_discrete_hypothesis_new64.py).
- **Earlier correctly preserved negative experiment:** [original new32 source](evidence/public_fourhistory_frozen_ppo_original32_780001_790016/), [registered initial 32-state experiment](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37912591209), [reproducible retrospective pilot (NOT PhysX intervention)](../audit_development_old32_full_history_index.py).
- **External researcher-owned fork entry:** [independent eight-reset PhysX workflow](../../.github/workflows/outside-discrete-history-v2-physx.yml) and [source-locked runner](../outside_discrete_history_v2_replication.py). This workflow being available is **not** an external laboratory replication.

**Current conclusion.** A complete finite controller-execution history can, in this tested fault regime, be conditionally reconstructed from ordinary public tool motion even when the competing histories have different orientations. Selectively replacing a private commanded-target read with this evidence saved actual privileged reads without changing observed frozen PPO task success on an independent, before-outcome 64-state physical simulation cohort. The credible next step is not another prettier self-fork merge, but a matched-information, independently operated fault-domain transfer study.

*Do not call this result an accepted top-tier paper, independent outside validation, a new set-membership theorem or hardware safety certificate.*

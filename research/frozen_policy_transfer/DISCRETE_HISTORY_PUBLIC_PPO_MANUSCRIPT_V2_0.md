# When Did My Robot Command Execute?
## Complete-History Public Evidence for Selective Controller-State Readback in Frozen Robot Policies

**Technical manuscript v2.0 — 9 October 2026.** Author-operated, preregistered genuine ManiSkill CPU PhysX experiments. Not peer reviewed, externally reproduced, hardware validated, or accepted for publication.

**Zhibo Zhang** · Hangzhou Dianzi University  
*Authorship and affiliations are subject to confirmation before submission.*

### Abstract

Frozen robot policies can fail after transfer between end-effector action interfaces even when their numerical action vectors remain valid. The source policy may command increments relative to an achieved pose, whereas the target controller accumulates increments from its last commanded target. Missing execution acknowledgements make this target an unobserved discrete state. We ask whether measured public motion can identify a complete controller-target history, including orientation, without a privileged target-memory read. Our observer enumerates command-consistent target histories, compares public achieved-XYZ movement against a previously calibrated response envelope, and either selects one entire historical SE(3) target or invokes one explicit state read. We first expose why an earlier all-held fault test could be defeated by an always-assume-held shortcut and why a later mixed-truth cohort reused 32 earlier reset identities. To test the resulting generalization threat without adjusting the method, we registered **64 completely disjoint PullCube/StackCube reset states before running** and physically varied the first unknown-ACK command between applied and held outcomes, with a neutral held second command. Eight original native-PhysX shards executed **576 separate controller worlds** using published, unchanged frozen PPO checkpoints. The public-history observer completed **57/64 official tasks with 33 privileged controller-target reads**, versus **56/64 with 52 reads** for a task-conditioned, physically executed strong competitor and **57/64 with 64 reads** for scheduled fixed readback. It identified one complete history from public motion in **31/64** cases with no observed confident wrong identifications. The paired success comparison has only one discordant success; it does **not** establish a statistically reliable improvement in task completion. Our narrower supported result is a reproducible, conditional reduction in privileged controller-memory dependence under a declared mixed-execution fault distribution, not a hardware safety guarantee or general solution to arbitrary unknown acknowledgements.

**Keywords:** robot learning; action semantics; partially observed execution history; controller target memory; conditional identification; selective state query; frozen-policy transfer.

---

## 1. Failure mechanism and research claim

We distinguish three states routinely conflated in robot-action transfer: the source policy's achieved end-effector pose, the destination controller's last *commanded* target, and the fact of whether the latest native command physically executed. The destination target update is

\[
M_{t+1} =
\begin{cases}
F(M_t,u_t), & z_t=1,\\
M_t, & z_t=0 ,
\end{cases}
\]

where \(M_t\in SE(3)\), \(u_t\) is a typed destination-native target increment, \(F\) is the documented target recurrence, and \(z_t\in\{0,1\}\) is the hidden execution truth. The source PPO policy is unchanged and computes \(a_t=\pi(o_t)\). Two unacknowledged intended actions can produce up to four possible target-memory histories, even if the native chart \(F\) is known exactly. A good-looking achieved pose is not evidence that an intended native target update occurred.

The falsifiable claim is narrow: **under a previously calibrated public-motion response hypothesis, a unique compatible entire target history can sometimes replace a privileged controller-memory read**. Neither generic belief tracking nor active probes are claimed as first inventions; prior ActionShift and ActionABI work already develops related ideas. The present contribution is a fault-specific, source-audited identification-and-authority gate with explicit failed cases and exact state-read accounting.

## 2. Whole-target-history observer

After an ambiguous ACK, propagate all command-consistent candidate target poses

\[
\mathcal H_t=\{M_t^{(1)},\ldots,M_t^{(K)}\}\subset SE(3)
\]

without reading the simulator's target state. Every candidate stores the actual complete position and quaternion obtained from the known native command recurrence; we do **not** independently estimate an orientation from the observed XYZ displacement.

At the predeclared second physical target-hold event, observe the publicly achieved end-effector XYZ before and after the same neutral native step, \(x,y\in\mathbb R^3\). The empirical conditional model for candidate \(i\) is

\[
y \simeq x+\alpha(M^{(i)}_{xyz}-x)+e,\qquad
\alpha\in[0,1],\quad \|e\|_2\le \epsilon_{\mathrm{task}} .
\]

The residual is the minimum Euclidean distance of \(y\) to the candidate's predicted segment over allowed \(\alpha\), with the historical task-dependent \(\epsilon\) fixed on earlier training responses. Candidate \(i\) is compatible when its residual does not exceed \(\epsilon\). Authorize public-only resynchronization **only when exactly one entire history survives** and every competitor has residual strictly exceeding \(\epsilon+0.002\) m. The complete quaternion from that survivor is used unchanged. An ambiguous, invalid, or unverified response instead consumes exactly one logged authoritative target read at the next fixed checkpoint. No test-time refit, confidence-threshold optimization, PPO retraining, hidden-controller-target getter in the public decision path, or extra actuated probing step is permitted.

This deliberately replaces an overconservative earlier guard requiring all target orientations to agree **even after their position histories had been rejected**. That earlier guard authorized 0/32 public histories in a separate prospective source run. The replacement can be wrong under shifted dynamics; a finite empirically fitted response envelope is not a certified bound on future physics.

The interface also treats authoritative readback as an atomic state update: the discrete-history belief and the same-step control branch must be invalidated together. An earlier physically executed confound-control study confirmed that leaving a stale multiple-history branch flag after readback changes controller trajectories despite identical private reads. This is a correctness condition, not evidence of collision or force safety.

## 3. Experimental design: separate development evidence from a truly new reset cohort

### 3.1 Provenance and non-independence disclosed

The initial all-held study used 64 fresh reset states and 512 native controller worlds, finding 58/64 official successes with 39 controller-private reads versus 58/64 with 57 task-aware reads. That result established task-level information economy **under two physically held commands only**, but a zero-read assume-held observer could exploit the intervention pattern.

A subsequent mixed-first-ACK experiment physically stepped 576 controller worlds and observed 58/64 successes with 31 reads versus 58/64 with 58 reads for a strong task-aware route. Its first ACK was applied in half the states. **However, 32 of its 64 task/reset identities overlapped a previously preregistered full-pose survivor study.** We preserve the outcome and original hashes but refuse to call the mixed cohort a fully independent reset-level holdout, or to pool the two studies as distinct unseen-state replications.

### 3.2 Independent pre-outcome experiment

The definitive protocol was [committed before implementing the new shard runner](https://github.com/lindicaphxag-tech/ManiSkill/commit/f6b298df1a076021783a75c8248eadd8c0f8ddfc). The new PullCube reset IDs **1180001–1180032** and StackCube IDs **1190001–1190032** are disjoint from the earlier published reset identities. The previous mixed-truth model, 9-arm physical simulator source, native controller chart, public response epsilon, 2 mm non-winner gap, action horizon, published PPO checkpoints and source actor weights were **unchanged by Git Blob**, not learned anew on these cases.

The t2 native action is genuinely **applied** on each even reset ID and physically **held** on each odd reset ID, yielding 16 applied and 16 held trials per task. The destination adapter sees the same unknown ACK in both. The following t3 native arm command is physically zero/held for every original trial and its acknowledgement is unknown. Thus this is a mixed-first-fault / held-second-fault test, **not four independently crossed t2×t3 execution truths**. A future truly mixed second command requires a changed observable motion model and a separately preregistered physically nonzero target command.

Two released external PPO checkpoints are fixed: PullCube SHA-256 \`74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7\`, StackCube SHA-256 \`e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c\`. Nine independently stepped source/no-fault, oracle and faulted comparator controller worlds run on each of 64 registered reset seeds, not on 576 independent learned policies.

The primary comparisons use **paired official native task success**, count of decision-time private target-state reads, number of public whole-pose identifications, incorrect *confident* history authorizations, and fault exposure. The strong task-conditioned competitor is chosen before outcome: PullCube uses previously fixed geometry-triggered selective target reading, StackCube uses fixed t4 target reading. The unconditional fixed t4 reader is a second strong baseline. An always-assume-held zero-private-read physical comparator is retained to expose an easier solution that exploits the fault distribution.

Public motion costs two achieved-XYZ samples per exposed public-history episode and no additional actuated step. The methods therefore do **not** have identical total information access. The supported comparison is **privileged target-state read economy**, rather than a fair all-sensor, all-computation, all-latency Pareto or SOTA claim.

## 4. Source-authenticated real PhysX results

The first original [all-green 10-job native PhysX and independent whole-denominator audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37916917436) executed eight original eight-state shards and a separately computed full-population audit. A second [hash-pinned archive and source re-audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37917471957) independently rechecked all original artifacts and rejected five deliberate source forgeries. The 16 untouched per-shard source and audit JSONs, first source auditor, recomputed auditor and SHA-256 ledger are [permanently preserved together](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/replicate-mixedack-disjoint64-20261009/research/frozen_policy_transfer/evidence/disjoint_mixed_ack_original64_1180001_1190032).

| Actually stepped strategy | Official task success | Privileged decision-time target reads |
|:--|--:|--:|
| **Complete-history public witness, then read on ambiguity** | **57/64** | **33** |
| **Strong precommitted task-conditioned selective/fixed query** | **56/64** | **52** |
| Fixed-time t4 authoritative read on every task | 57/64 | 64 |
| Zero-read always-assume-held execution history | 43/64 | 0 |
| Generic geometry-only no-query bounded/refuse | 14/64 | 0 |
| Unconditionally optimistic unknown-ACK observer | 16/64 | 0 |

The oracle is *continuously privileged*, so its source success rate is not assigned a fictitious zero private-state-information cost. The no-fault source policy is likewise a diagnostic reference and not a hidden-ACK recovery treatment.

Paired new-vs-task-conditioned outcomes are **56 both successful, 7 both failed, 1 public-only successful, 0 strong-comparator-only successful**. The observed 1/64 task-success difference does **not** support a task-efficacy superiority claim or a statistical noninferiority guarantee. In these 64 original tasks, public state access avoided **19 of the strong comparator's 52 private target reads (36.5% fewer)**, with two additional public achieved-XYZ observations per exposed episode. **31/64 complete target-memory histories were selected publicly, 0 observed confidently wrong labels**; no population error probability bound or hardware-safe authorization guarantee is claimed.

### 4.1 Task and true execution-stratified outcomes

| Task / actual physical t2 truth | n | New success | Strong success | New private reads | Strong private reads | Public whole histories selected |
|:--|--:|--:|--:|--:|--:|--:|
| PullCube / applied | 16 | 16 | 15 | 3 | 10 | 13 |
| PullCube / held | 16 | 16 | 16 | 8 | 10 | 8 |
| StackCube / applied | 16 | 12 | 12 | 11 | 16 | 5 |
| StackCube / held | 16 | 13 | 13 | 11 | 16 | 5 |
| **All original trials** | **64** | **57** | **56** | **33** | **52** | **31** |

The PullCube method and fixed-query comparator each succeeded 32/32. StackCube public and fixed each succeeded 25/32. This supports a conditional information-saving observation; it does not show fewer physical failures relative to fully queried controller memory. The observed no-confident-error figure is descriptive on this sampled set.

### 4.2 What the experiment falsifies and does not test

* The original "both faults always held" shortcut is inadequate as a universal description of the mixed-t2 benchmark: always-assume-held reached only 43/64 tasks despite consuming no private reads. Nonetheless it remains a legitimate low-cost comparator rather than a strawman to delete.
* The model does not identify every command history: it explicitly requires private target reads for 33/64 of the new trials. These are admissions of insufficient public evidence, not algorithm failures to be removed from the denominator.
* The no-fault source is not recovered perfectly by all variants, and official task completion must not be substituted for correctness of a latent history assignment.
* Our confidence envelope is historical and empirical; arbitrary contact regimes, variable gains, true t3-applied motions, new controller frames and camera/VLA outputs are outside the tested support.

## 5. Relation to prior work and validity threats

ActionShift/ActionABI already study action contracts, online belief adaptation and active probing. Standard set-membership intervals and finite hypothesis elimination are not new mathematical discoveries. The distinctive task-level application here is to preserve *whole* commanded SE(3) target-history identities under a known target-relative native ABI with uncertain command realization, and measure when achieved motion displaces a costly direct read while physical robot policy behavior is unchanged.

Several threats prevent stronger claims. All principal results are from the same ManiSkill CPU PhysX engine, one Panda native controller family and two released PPOs, without true packet transport, external robot operation, force/torque measurements, collision certification, learned VLA actuation, independently attested response envelopes or fully mixed second-ACK truth. The result is conditional on known command chart and trusted initial native target. The task-aware opponent uses fewer public motion samples than the new observer and is not matched in overall information consumption. The first held-only experiment and one mixed-first study are valuable development and falsification evidence, but the latter reuses earlier reset identities; only the newly registered 1180001/1190001 cohort is represented as wholly reset-disjoint relative to those earlier studies.

A broader method paper should test independent robot/controller regimes, matched sensing-plus-query cost, true second-fault applied/held combinations, and a third-party-owned fork run. An externally accepted benchmark or peer-reviewed review is still absent.

## 6. Reviewer entry and exact reproduction

- **New unmodified source data, all negative outcomes, and SHA-256:** [disjoint_mixed_ack_original64_1180001_1190032](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/replicate-mixedack-disjoint64-20261009/research/frozen_policy_transfer/evidence/disjoint_mixed_ack_original64_1180001_1190032)
- **Pre-outcome immutable registered protocol:** [DISJOINT_MIXED_T2_PPO64_PREOUTCOME_V1.json](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/replicate-mixedack-disjoint64-20261009/research/DISJOINT_MIXED_T2_PPO64_PREOUTCOME_V1.json)
- **Exact actual frozen source and independently scored experimental scripts:** [first full native PhysX execution and auditor](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37916917436)
- **Independent second source-hash audit, five adversarial mutation rejections and permanent source archive:** [verified archival workflow](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37917471957)
- **First mixed-truth cohort's overlap correction, results and preserved failures:** [honest prior-study boundary](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/mixed-ack-truth-frozenppo-new64-20261009/research/frozen_policy_transfer/MIXED_ACK_REVIEWER_SEED_AND_TRUTH_CORRECTION.md)
- **Older held-only task-level evidence:** [prospective 64 frozen-PPO source audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37913661619)
- **Original negative four-history orientation guard:** [32-state physically executed null](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37912591209)

An outside laboratory should freeze its own disjoint reset identities *before* triggering the exact original simulator code, preserve the same complete policy checkpoints and all negative trials, and report the copied public-state and privileged-memory budgets. Independent replication exists **only** after an actual other-operated physical simulation or physical robot experiment, not after this author's own CI succeeds.

**Research conclusion.** In this declared simulator and fault model, complete history-level public observations can substitute for some authoritative internal-controller state reads without any observed reduction in paired official policy task success relative to a strong precommitted comparator; a one-task success difference is not reliable efficacy evidence. The resulting repeatable, uncertainty-explicit controller-memory interface is a potential building block for VLA controllers, not proof of general VLA performance or verified robotic safety.

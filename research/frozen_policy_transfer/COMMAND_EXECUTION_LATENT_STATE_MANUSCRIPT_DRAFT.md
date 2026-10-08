# Command Execution as a Latent State: Evidence-Gated Target Memory for Frozen Robot Policies

**Pre-submission research manuscript draft v0.3 · not peer reviewed, not accepted, no outside replication · 9 October 2026**

**Authors, affiliation, target venue, final title: intentionally not asserted in this code artifact.**

## Abstract

A learned manipulation policy may issue the correct action in its source controller while failing after migration to a target-accumulating controller: the physical meaning of each new action depends on a hidden *previous commanded target*. If an action acknowledgement is missing, even a known controller transition law leaves multiple plausible previous-target histories. We distinguish three questions usually conflated in action adaptation: whether private target memory is **necessary**, whether ambiguous histories can be **robustly controlled without resolving them**, and when the cost of a **trusted target readback** is warranted. We study independently released, SHA-256-pinned frozen PPO checkpoints on PullCube and StackCube in native CPU PhysX without policy retraining. A separate preregistered 64-state mechanistic experiment finds identical task-level results between controller-memory and action-history reconstruction when all commands are acknowledged; a 16-state independently implemented observer further validates command-only target recursion. Under deliberately ambiguous execution, a prospectively frozen, **new-seed 64-state confirmation** finds that certificate-gated bounded execution with at most one trusted target query succeeds in **60/64** trials with **15** queries. An unconditional one-query baseline obtains **57/64** with **64** queries, while a zero-query bounded method obtains **47/64**. The query reduction is **76.6%**, but the selective–mandatory task-success difference is not statistically established. A separate 64-trial zero-query midpoint falsification yields **43/64** versus **48/64** for optimistic continuation, and a separate **preregistered 32-condition real PhysX achieved-pose probe** exposes **15/32 wrong confident ACK-history decisions** despite **19/32 official task successes**. These findings support *conditional observability and evidence-dependent query allocation*, rather than a universal need for private controller state, exact transfer, collision safety or model-free hidden-state inference.

**Keywords:** robot learning; action interface; command acknowledgement; target memory; robust control; information acquisition; frozen-policy transfer; reproducibility.

## 1. Problem and positioning

Let the frozen source policy issue `a_t = pi(o_t)`. The source end-effector delta controller interprets `a_t` relative to achieved pose `X_t`. The destination accumulated-target controller interprets the corresponding command `u_t` relative to previous *commanded target* `M_t`. The two controllers can have otherwise identical robot embodiment and task setup. A numerically valid action may be semantically wrong if `M_t != X_t`.

The destination transition may be known: `M_{t+1} = F(M_t,u_t)`. If the initial commanded target is known and the applied native commands are fully acknowledged, a straightforward observer recursively reconstructs `M_t` without reading private memory. However, if one request has unknown execution status, the adapter must retain at least two candidate histories `H_t = {M_t^applied, M_t^held}`. Retaining them is not the same as automatically knowing which one the physical controller occupies.

**Distinctive question:** When should the adapter (i) issue one action that remains acceptable under every credible history, (ii) spend one scarce *trusted* target-memory read to collapse the uncertainty, or (iii) refuse? Unlike general hidden action-ABI identification, we assume a known source/destination chart and deliberately make command *execution truth* uncertain.

### Related contributions and needed direct comparisons

[ActionShift](https://github.com/Archerkattri/actionshift) already studies online adaptation to unknown action-interface contracts, multiple PPO/diffusion backbones, action lag, belief updates and active probes; its [ActionABI](https://github.com/Archerkattri/actionabi) companion studies forensic contract equivalence and calibrated abstention. Our frozen PPO checkpoints are the **third party's original released models**, not newly trained by this project. Any eventual paper MUST compare against an ActionShift-style belief/probe policy under the same observation and actuation budgets; identifying an unknown action encoding, or having an active probe, is not a novel contribution by itself.

[TAM: Torque Adaptation Module](https://arxiv.org/abs/2606.06218), accepted at CoRL 2026, targets dynamics and torque-level motion-transfer mismatches using proprioceptive history and real-robot demonstrations. Our narrower question is the semantics and knowledge of prior *commanded target* and ACK delivery status; we neither match TAM's robot transfer nor its hardware validation. Existing set-membership, minimax interval control and observer-recursion arguments are classical, and should never be relabeled as original theorems.

## 2. Methods and information access

**M0: No policy training.** PullCube-v1 and StackCube-v1 use frozen third-party ActionShift PPO weights at a pinned published revision, each file SHA-256 checked before a run. The native original policy uses the official `pd_ee_delta_pose` chart and the destination official `pd_ee_target_delta_pose` chart. Trials execute genuine ManiSkill `physx_cpu` and read official task-success flags.

**M1: Documented history observer.** With known reset target and known applied commands `u_0,...,u_{t-1}`, the observer sets `M_hat_0=M_0`, `M_hat_{t+1}=F(M_hat_t,u_t)`. The induction is elementary. An unknown ACK branches the belief rather than quietly assuming success or omission.

**M2: Robust two-history authorization.** For each history and candidate source task target, compute the destination-native command implied by the known chart. If a common bounded command satisfies the *stated commanded-target geometric tolerance*, it can be dispatched while retaining both histories. The implementation tests finite pose cases and bounds position/rotation separately. It is **not** a guarantee for achieved poses, trajectories, contact or hardware safety.

**M3: Selective trusted readback.** When the common action cannot be authorized under the declared tolerance, use one explicitly budgeted **privileged** controller target-memory read, collapse the belief, and resume. The control and task-success comparisons must disclose that M3 receives additional state information unavailable to zero-read observers. Reading a controller target is an information action with a cost; here it is only a proxy budget, not a measured real sensor/network latency.

**M4: Heuristics and physical-response evidence.** The earliest achieved-XYZ-nearest-target heuristic is demonstrably unreliable under real native physics: in the completed preregistered **32-condition full source audit**, the heuristic confidently labels every state but makes **15/32 wrong ACK-history decisions** (including **15/16** where the original arm command actually executed), even while attaining **19/32 official task successes**. The full experiment has been independently reaggregated from all eight original real PhysX source JSONs. The next candidate is a set-membership response certificate of the form `y=x+alpha(M_actual-x)+e`, requiring an *independently calibrated* alpha interval and total model-noise bound. Its [model-level implementation and synthetic falsification tests](../ack_probe_set_membership.py) do NOT establish the response law in real physics. If both histories remain consistent or the envelope is untrusted, it refuses.

## 3. Empirical protocol and source identities

All critical conclusions separate original discovery from follow-up prospective cohorts:

| Study | Fixed trial population | State evidence or comparison | Status |
|---|---|---|---|
| Frozen-policy target-memory ABI | Four tasks, earlier public trials | Source / naive / exact-refuse / bounded projection | Author-run real PhysX |
| Explicit history falsifier | PullCube 71001–71032; StackCube 81001–81032 | Live private target vs action-history shadow | [Original run 37818985343](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37818985343); full original files permanently archived |
| Independently coded observer | PullCube 62001–62008, StackCube 72001–72008 | Command-only ACK-gated observer vs privileged converter | [Original run 37819111802](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37819111802) |
| Both ACK truths | PullCube 94001–94008, StackCube 95001–95008, two truths per seed | Optimistic, pessimistic, one-read, oracle, stop | [Original run 37824078238](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37824078238), all 32 source rows archived |
| Zero-readback midpoint negative control | Separate preregistered 64 task×fault states | Midpoint vs optimistic/pessimistic/privileged | [Original run 37825781536](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37825781536) |
| **Bounded-or-query CONFIRMATION** | **64 NEW unique seeds**: PullCube 142001–142032, StackCube 152001–152032 | Selective query vs mandatory, bounded zero-query, optimistic, stop | [Pre-frozen protocol and actual 8-job run 37828426195](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37828426195), [full-source audit 37829450301](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37829450301) |
| Achieved response one-step probe | PullCube 140001–140008 and StackCube 150001–150008 under two fault truths | Public achieved XYZ vs both history candidates; equal-step blind controls | [Complete 10/10 original PhysX and full 32-row audit 37829520809](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37829520809); [negative-results report](PHYSICAL_RESPONSE_32_NEGATIVE_RESULT.md) |

**Never sum these populations into a number of independently trained policies or robots.** They reuse two pretrained PPOs, known Panda-family controllers, and several repeated true/hidden fault conditions. Source native policy success is context, not equal-fault competitor. SAPIEN/PhysX achieved task flags cannot certify safe commands or collision avoidance.

## 4. Main confirmatory result

On the NEW 64 unique holdout reset states, preregistered before running the *unchanged* bounded-or-query evaluator:

| Controller policy | PullCube /32 | StackCube /32 | Total /64 | Privileged controller reads |
|---|---:|---:|---:|---:|
| Native source, no injected fault (context only) | 32 | 28 | 60 | 0 |
| Optimistic assumption, no read | 31 | 11 | 42 | 0 |
| Two-history bounded control, no read | 30 | 17 | 47 | 0 |
| **Bounded-or-query** | **32** | **28** | **60** | **15** |
| One mandatory trusted readback | 32 | 25 | 57 | 64 |
| Exact-only refusal | 0 | 0 | 0 | 0 |

The selective method makes **49 fewer privileged reads (76.5625% reduction)** than mandatory one-readback. Paired selective-versus-mandatory task outcomes have **five selective-only** and **two mandatory-only** successes. A two-sided exact McNemar/binomial comparison on these seven discordant states gives **p = 0.453125**: not evidence of a statistically significant task-success superiority claim. Versus no-query bounded there were **13 selective-only** and zero no-query-only successes, but additional target information is a confound rather than a fair equal-information advantage.

The selective policy succeeds at the clean-source total in this cohort, **but those counts need not be the same per-seed successes or physical trajectories**. The two controller modes can differ in contacts, timing and bounded projections. There is no measured safety claim.

## 5. Negative and causal evidence

- **Privileged target getter not universally necessary:** complete ACKs allow exact recursive commanded-target reconstruction under known chart, verified in real PhysX. This is a conditional observer fact, not system-wide hidden-state recovery.
- **No-query midpoint is not universally superior:** 43/64 total versus optimistic 48/64 in a separately preregistered original simulation. Reducing worst-case commanded-target error geometrically need not improve task success.
- **Guessing which ambiguous ACK truth occurred can reverse the winner:** the original two-fault 32-condition comparison includes StackCube 8/8 optimistic vs 0/8 pessimistic when applied, but 2/8 optimistic vs 8/8 pessimistic when held; the one-privileged-read method obtains 8/8 in each. This has a different **information budget**.
- **Task success alone does not validate state identification:** the completed 32-task-condition achieved-pose experiment classified all 32 states, **misidentified 15**, and completed 19 tasks; it demonstrates that task success can conceal systematic errors in inferred ACK execution truth. This motivated independent noise/plant-envelope attestation and refusal rather than retroactively tuning its decision margin on test states.
- **Bounds portability isn't policy portability:** public Fetch/XArm controller contract checks verify additive certificate implementation in other controllers, but no frozen learned-policy transfer or manipulation task completion on those embodiments is claimed.

## 6. What this manuscript cannot currently claim

1. Independently externally reproduced PhysX success; another researcher's fork run; official ManiSkill or ActionShift maintainer acceptance of this project.
2. Novel pose-controller target recursion, interval minimax mathematics, active probes in general, or previously unknown robot/action semantics.
3. A learned VLA, real network packet losses, hardware deployment, physical safety, actuator torque/force or collision safety certificates.
4. Statistically significant improvements in task success over the mandatory-read competitor in the 64-state confirmation.
5. Correct physical-response identification without **independently calibrated dynamics error envelopes** or precise target provenance.
6. A complete cross-robot benchmark on disjoint robot morphologies with fairness to existing ActionShift / ActionABI / dynamics adaptation baselines.

## 7. Minimum additional evidence for a competitive robotics submission

**Highest-value experiment (not another user-owned PR):** obtain an independent ActionShift maintainer or external robotics lab to run a disjoint task×two-truth cohort, compare against ActionShift's own active belief and learned identifiers using the **same external information and online action budget**, and publish full failure traces. [The third-party scope RFC](https://github.com/Archerkattri/actionshift/issues/2) asks precisely whether ACK-unknown-applied vs ACK-unknown-held deserves an opt-in upstream benchmark. The [one-click real PhysX fork-and-run entry](EXTERNAL_FORK_ONE_CLICK_PHYSX.md) reduces integration cost; this is still only an *invitation*, not external adoption.

**Original-method gate:** calibrate a genuinely realizable actuator/sensor response envelope on a task-disjoint cohort, then test a new on-demand probe/readback decision rule against matched no-probe, probe-only, learned state-identifier and trusted-read comparators; count **wrong confident authorization**, abstention, query cost, task success, timing and contact errors separately.

**Broader acceptance gate:** execute on independently maintained controller implementations and robots, with real delayed/omitted/reordered command delivery rather than a single native zero-arm-delta simulation fault. Only then consider a general controller-history recovery or real-robot reliability conclusion.

## Reproduction and credit

- [Public project first screen and data](https://github.com/lindicaphxag-tech/ManiSkill)
- [External independently selectable seed reproduction](EXTERNAL_FORK_ONE_CLICK_PHYSX.md)
- [Persistent 32-condition original source](evidence/unknown_ack_prospective_32_94001_95008/)
- [Persistent 64-state shadow observer source](evidence/shadow_observer_64_71001_81032/)
- [New64 exact original results and raw source links](ROBUST_QUERY_NEW64_PROSPECTIVE_RESULTS.md)
- [Independent falsification challenge](https://github.com/lindicaphxag-tech/kaggle/issues/67)
- [Third-party frozen PPO/benchmark origin: ActionShift](https://github.com/Archerkattri/actionshift)

**Responsible-claim statement:** All supplied source workflows were executed in the contributor's research fork. An external team has not independently repeated the physics outcomes. The definitive result in this draft is a preregistered **query-budget/task-outcome tradeoff on 64 new simulated states**, together with honest negative results and explicit missing evidence.

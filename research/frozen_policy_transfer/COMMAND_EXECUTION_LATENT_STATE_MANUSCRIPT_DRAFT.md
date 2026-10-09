# Command Execution as a Latent State: Evidence-Gated Target Memory for Frozen Robot Policies

**Pre-submission research manuscript draft v0.7 · not peer reviewed, not accepted, no outside replication · 9 October 2026**

**Authors, affiliation, target venue, final title: intentionally not asserted in this code artifact.**

## Abstract

Frozen manipulation policies can fail when a destination controller interprets each action relative to its previously **commanded** target rather than the end-effector pose used during policy training. A missing execution acknowledgement makes that previous target uncertain, even when the controller dynamics are known. We study whether an adapter should act within a verified target-error bound, obtain a trusted target-memory observation, or refuse control. The adapter maintains the applied/omitted command hypotheses and authorizes a common native action only when both satisfy a predeclared position/orientation setpoint bound; otherwise it requests one explicitly accounted target readback. Using unchanged publicly released PPO checkpoints and genuine ManiSkill PhysX in PullCube and StackCube, an earlier 64-state confirmation achieved **60/64** task successes with **15** private target readbacks, versus **57/64** with 64 mandatory reads; the paired difference was not significant (exact two-sided \(p=0.453\)). A stronger, separately frozen **64-new-state, near-equal-query** experiment compared evidence-triggered requests (17 reads) with an a priori periodic request schedule (16 reads). It obtained **58/64 versus 47/64** successes, respectively (12 adaptive-only, 1 periodic-only; exploratory exact \(p=0.00342\)). A SHA-locked retrospective fixed-budget allocation analysis further found **two states that succeeded only with deferred reads at step 5 or 6**, not with an immediate or absent read. In a separately registered **two-unknown-ACK, up-to-four-history** genuine PhysX trial on 16 additional task seeds, an all-history bounded-or-query method achieved **15/16** successes using **9** privileged target reads; reading after both failures achieved **15/16** using **32**. The latter experiment checks multi-history feasibility under the declared target chart, not task-success superiority. A disjoint 32-condition physical-response study found 15 incorrect yet confident ACK-history identifications despite 19 completed tasks, showing that task reward cannot validate controller-state inference. These results support conditional action authorization and the importance of **when** expensive evidence is acquired. They do not establish optimal query scheduling, performance across robot embodiments, equal-information superiority to existing active-belief baselines, or collision/force safety.
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

### 4.1 Fully reproducible exact paired-state evidence and information frontier

The raw-source analysis code has now been accepted into the default branch in [research PR #85](https://github.com/lindicaphxag-tech/ManiSkill/pull/85), with original SHA-256 checks for all eight physical-simulator output JSONs and an independent exact-source audit. The standalone verifier is in [the original 64-state reviewer capsule](review/PAIRED_AUTHORITY_FRONTIER_64.md); its [public Python 3.11/3.13 CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37831666978) reports **9/9 source and destructive statistical tests passed** in both environments. This is source-authentic **retrospective analysis** of the registered new-seed execution, not a second independent simulator-run cohort.

The adaptive and mandatory policies share the identical actual PhysX reset seed and original PPO at each task state. Their exact **2 × 2 matched-outcome** contingency is:

| Matched trial classification | Count |
|---|---:|
| Both selective and mandatory succeed | 55 |
| Selective succeeds, mandatory fails | 5 |
| Mandatory succeeds, selective fails | 2 |
| Both policies fail | 2 |

There are 7 discordant observations. The **two-sided conditional exact paired p-value is 0.453125** and does not establish superiority or a prospective noninferiority margin. Per task, all **32 PullCube selective and mandatory outcomes succeed** (queries 2 selective versus 32 mandatory). On StackCube, the adaptive method succeeds in **28/32**, mandatory in **25/32** (13 selective reads versus 32 mandatory). Pooling the two source policies into 64 *robot platforms*, or treating seven alternative controllers as independent replications, would be pseudoreplication.

The selective and zero-target-readback bounded policies likewise share each physical reset seed, with 47 both-success, 13 selective-only-success, 0 bounded-only-success and 4 both-fail pairs (conditional exploratory exact p=0.000244140625). **This is not an equal-information comparison:** when the source states cannot be jointly controlled within the declared bounded commanded-target tolerance, the adaptive policy may use an extra *privileged* target-state observation. This source-condition information access, not just an optimizer improvement, can explain its higher success.

For a transparent source-cohort decision-cost sensitivity analysis, take unit reward per binary native task success and assign each privileged target-memory read cost \(\lambda\ge0\). The **empirical**, post-result sums are

\[
U_{\mathrm{adaptive}}(\lambda)=60-15\lambda,\qquad
U_{\mathrm{always}}(\lambda)=57-64\lambda,\qquad
U_{\mathrm{bounded\ only}}(\lambda)=47.
\]

In *these exact 64 source trials*, adaptive has greater aggregate reward and fewer target reads than mandatory for every nonnegative \(\lambda\), **but not per-seed outcome dominance** (two opposite-exclusive victories exist). Its observed reward advantage against never querying becomes negative for \(\lambda>13/15\), with different task-stratum breakpoints: Pull `(32-30)/2=1` and Stack `(28-17)/13≈0.846`. These crossings are computed from the observed cohort *after experiment completion* and therefore do not define an optimized controller or calibrated externally valid query-price threshold. A 95% uncertainty interval on read frequency is likewise descriptive, not an unobserved fault-risk guarantee.

### 4.2 Exact external reproduction trigger and protected boundaries

The newly [merged external one-click seven-arm workflow #84](https://github.com/lindicaphxag-tech/ManiSkill/pull/84) makes a **genuine independent PhysX task rerun technically possible**, not scientifically completed. An external researcher can [fork, run the original frozen PPO/official seven-controller suite, and pick previously untested seeds](EXTERNAL_FORK_ONE_CLICK_PHYSX.md), obtaining exact method Git blobs, SHA-256 verified released weights, source environment details, complete per-trial outcomes, all actual faults and information costs. The author-run workflow [37831105250](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37831105250) passed eight additional chosen PullCube seeds; this still belongs to the *same author*, and its seeds **200001–200008 should not be reused as fresh unseen seeds**. A separate outside investigator has not confirmed any part of the original closed-loop claim as of this manuscript revision.

[ActionShift](https://github.com/Archerkattri/actionshift) and [ActionABI](https://github.com/Archerkattri/actionabi) already establish hidden action-contract adaptation and active-probe/equivalence-set baselines; the current author-operated intervention **does not directly beat** those state-of-the-art methods under a controlled common information, actuation, and simulator-cost budget. The original test uses only a known two-history command-target set; it is not evidence for arbitrary unobserved control-system model identification, learned simulator-free motor feedback inference, safety guarantees, or cross-robot task transfer. A genuinely new independent external comparison on the same two-truth physical fault family remains a required next experiment.

### 4.3 Stronger matched-cost prospective falsifier: *when* to query

The original 64-state selective-vs-mandatory comparison varies both query *availability* and *number* of trusted observations, making it insufficient to isolate scheduling effects. We therefore registered **another 64 entirely new source reset states** (PullCube 260001–260032 and StackCube 270001–270032) and, before any outcomes were observed, froze a deterministic placebo information policy: obtain exactly one private target readback only in episodes whose seed satisfies \(\mathrm{seed}\bmod4=0\), for 16 predefined query episodes, otherwise attempt the unchanged two-history bounded controller and refuse if certification fails. The adaptive controller's bounds, source code, policy/checkpoint hashes and fault model remained unchanged. Actual private reads were counted without forced post-hoc equalization.

| Frozen original controller arm | Pull /32 | Stack /32 | Total /64 | Privileged readbacks |
| --- | ---: | ---: | ---: | ---: |
| Evidence-triggered certificate/query | **32** | **26** | **58** | **17** |
| Precommitted periodic query schedule | 30 | 17 | 47 | 16 |
| Every-fault mandatory trusted query | 32 | 28 | 60 | 64 |
| No-readback bounded/refusal | 29 | 12 | 41 | 0 |
| Optimistic ACK executed assumption | — | — | 40 | 0 |

The matched adaptive-periodic contingency comprised 46 successes for both, 12 adaptive-only successes, 1 periodic-only success and 5 failures for both, giving unadjusted two-sided exact McNemar \(p=0.00341796875\). The two arms used **nearly** the same number of privileged reads, not exactly the same (17 versus 16). Thus the experiment identifies a substantial *in-cohort* advantage over this **specific fixed timing placebo**, not a globally optimal decision policy, a learned/belief-agent baseline or an equal-cost guarantee. Query placement is confounded with initial state complexity, as intended for a state-independent placebo, and no posthoc alternative schedule was optimized on the held-out episodes. Generalization beyond these two frozen PPOs in the same Panda controller family remains untested.

The source/model/query allocation was [registered in immutable commit ee209f6](https://github.com/lindicaphxag-tech/ManiSkill/commit/ee209f6bc80e2bb280f9b00e6a9bafc330bdc799), and [the original eight genuine PhysX job run 37833053629](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833053629) succeeded. The [complete all-seed outcome file and limitations](CERTIFY_QUERY_PERIODIC_PLACEBO_64_ORIGINAL_RESULTS.md) preserve every failed episode. These task-state findings were run by this contributor, not by an outside lab.

### 4.3a Exact retrospective finite-population fixed-readback allocation — and why the adaptive controller is not that allocation

We complemented the prospective period-4 timing placebo with a **read-only, source-locked** computation over the eight *unchanged* original 64-state PhysX result JSONs. The new audit [merged as PR #95](https://github.com/lindicaphxag-tech/ManiSkill/pull/95) binds the individual source file SHA-256s and even their original SHA256SUMS manifest to a previously published Git object identity. [The two independent Python environments and destructive source-mutation tests passed](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37835431517).

For each state, the actual PhysX archive contains both the **never-query bounded** controller outcome and the **fixed step-3 mandatory-query** controller outcome. Importantly, the *separately actually executed periodic-query* arm returns exactly the selected corresponding outcome in **all 64 states**, depending on its predeclared seed-divisibility decision. In this restricted simulator source setting, we can analyze **hypothetical fixed step-3 query allocations**, conditional on these recorded responses, without pretending to execute an impossible number of new PhysX trajectories.

The paired archive has **19 states where an immediate fixed query helps**, **45 where it does not change success**, and **zero where it worsens success**; the no-readback method succeeds on 41 states. Thus uniformly allocating exactly 17 fixed step-3 query episodes among the 64 produces a finite-population expected task-success count of

\[
41+\frac{17\cdot19}{64}=46.046875.
\]

The best possible 17-query allocation in the *observed* fixed-step-3 response bank reaches 58 successes, and exactly \( {19\choose17}=171\) of \( {64\choose17}=1{,}379{,}370{,}175{,}283{,}520\) such allocations attain it. **This tiny conditional combinatorial fraction is NOT a registered test p-value for our adaptive method:** the hypothetical random-allocation experiment was not prospectively executed, there are no external robot/policy replications, and adaptive control can be path-dependent.

Indeed **actual source-backed path dependence invalidates a naïve arm-switch explanation**. In two same-reset StackCube trials (seeds **270005** and **270030**), neither the immediately queried controller nor the never-query bounded controller completed the native task. The adaptive original controller did, after respectively issuing a *later* privileged target read at simulation step **6** or **5**. Because its earlier bounded actions changed the physical state before the eventual read, it cannot be reconstructed as a binary per-episode selection between the two fixed arms. This supports the more precise research hypothesis that **the time of an information event affects the ensuing trajectory**, but does not isolate timing causally from all preceding actions, contact dynamics or observations. The correct next study must compare against existing strong ActionShift adaptive probing under matched information and actuation budgets, on new tasks and hardware.

[Read full original-source mathematical/empirical audit, uncertainty boundaries, all negative cases and reproduction commands](EXACT_QUERY_ALLOCATION_64_PHYSX_RESULT.md).

### 4.3b Empirical public-response-or-trusted-readback: reducing *privileged* sensing on a different prospective fault cohort

The previous simple **nearest previous target** heuristic inferred executed versus held ACK from the achieved-EE position after a common physically stepped zero-target probe, yet reported **15 wrong confident labels in 32 original PhysX task×truth conditions**. This exposes the important difference between task completion and latent controller-memory correctness. A subsequent disjoint study calibrated a task-specific segment response residual envelope on **only four historical reset states per task**, and fixed the response model and epsilon *before* the fresh evaluation. This empirical envelope is **NOT** an independently attested physical error bound.

Our new, separately preregistered hybrid tests a **different information channel**: the public before/after-probe *achieved* EE XYZ position, combined with both commanded-target hypotheses reconstructed from the action history. At the registered probe timestep (t=3), after a possibly applied/held arm command at (t=2) with unknown acknowledgement, fit each candidate to the fixed closed-loop segment response family
[
 y=x+alpha(M-x)+e,qquad alphain[0,1],quad Vert eVert_2leepsilon_{m task}.
]
If exactly one candidate target is compatible, resume the frozen original policy with that hypothetical previous target **without querying hidden target memory**. If both or neither are compatible, refuse to guess and perform exactly **one explicitly budgeted privileged target-state readback**, then continue. We compare physically separate matched actual source/no-fault, optimistic, pessimistic, *public-only then abstain*, *public-or-read*, and *mandatory one private target read* control worlds. The same neutral-action probe is applied to all arms.

The frozen pre-result protocol [fa173507](https://github.com/lindicaphxag-tech/ManiSkill/commit/fa17350711f6c2c7cffb4cfa2bb7f8289f3ee0c4) registered PullCube seed IDs **180101–180108** and StackCube IDs **190101–190108**, each under BOTH actual command-executed/missing-ACK and physically held-command/missing-ACK: **16 distinct robot reset states × 2 fault truths = 32 paired task×truth conditions**. The external-model revision and checkpoint SHA-256, response epsilons (Pull **0.006944262561376447 m**, Stack **0.00719087965534261 m**) and public inference algorithm were not changed after the new data.

| Same-seed six-controller original PhysX arm | Official native task successes /32 | Privileged target-state decision readbacks |
|---|---:|---:|
| Original frozen policy, no fault with common physical probe | 26 | 0 |
| Same-probe optimistic history assumption | 23 | 0 |
| Same-probe pessimistic history assumption | 20 | 0 |
| Public empirical response ONLY; reject ambiguous history | 19 | 0 |
| **Public empirical unique-fit OR one explicit trusted readback** | **27** | **11** |
| Always one privileged target readback after the same probe | **27** | **32** |

The new hybrid accepted **21/32** public motion-based ACK-history decisions with **zero observed wrong confident labels among those 21**. It refused to infer on the other **11/32** and read actual privileged controller target memory **once each**. Unlike merely matching aggregate task success, the hybrid and always-read strategies had **identical task-success/failure flags for all 32 paired task×truth conditions** (zero exclusive successes in either direction). These results **do not prove** a small physical error bound or zero future misidentification probability. The original fitted envelope has only four historical robot reset states per task and must be recalibrated for shifts in the controller dynamics, process disturbance, joint motion, or contact.

[Full original eight-green-job PhysX run](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37834088246) · [all 32 unfiltered per-trial inferred-history labels, wrong-label flags, task successes, every target read and six matched arms](PUBLIC_RESPONSE_OR_READ32_ORIGINAL_RESULTS.md) · [per-file SHA-256 permanent author-operated source archive](evidence/public_or_read_new32_180101_190108/) · [successful independent-of-simulator original-data and five deliberately corrupted-source audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37835727029). They are **not** third-party lab reproduction.

**Important: our public-physical-response hybrid and our bounded-or-query controller have NOT yet been evaluated as a single, fully integrated method.** Their 27/32 task and 58/64 task outcomes are different prospective populations with different probes, information access and physical steps, and cannot be summed to claim combined policy performance. A credible integration would authorize common bounded target commands under all possible histories first, query public plant response only upon failed action certification, and then spend a trusted target read only when its calibrated admissible response set is ambiguous or invalid. That integration remains an experiment to be performed, and a proper full-information-cost comparison must equalize probe actuation and observer readings with control baselines.

### 4.4 New-seed multi-ACK extension: four possible target histories, real commanded-setpoint certification

The original two-history result restricts uncertainty to **one** ambiguously delivered native command. We separately fixed, before observing outcomes, an experiment with **two physically held commands** at simulator steps 2 and 4, while the adapter sees unknown execution receipts at both steps. With an acknowledged intervening native command, the controller's previous commanded target can have as many as **four credible histories**, whose update depends on the same verified root-left action chart. The [prespecified contract Git blob 4107c00](../MULTI_ACK_K_HISTORY_PREOUTCOME_V1.json) reserved **eight new PullCube** seeds 230001–230008 and **eight new StackCube** seeds 240001–240008, using original externally pretrained ActionShift PPO weights, without training or tuning, and two budgeted state-memory readbacks per episode.

For an explicit complete finite belief set of possible previous commanded targets \(\{(p_i,R_i)\}_{i=1}^K\), the [K-history certifier](../multi_history_authority.py) computes an **exact box-constrained translation \(L_\infty\) minimax** by a clipped midpoint of the per-axis extrema. For root-left spatial rotation, its **finite** candidate pool (existing orientations, pairwise SO(3) midpoints and chordal average) is not a globally optimal K≥3 rotation solver; instead it measures a feasible worst-case geodesic upper bound across **all K** credible states, with pairwise diameter/2 as a necessary global lower bound. Only a native-rotation-representable action meeting both predefined \(0.05\) m position and \(0.05\) rad rotational target budgets may be dispatched without an authorized readback. Missing/stale/untrusted histories, unverified controller semantics and unrepresentable native actions require refusal or an explicitly counted trusted state read.

The [original fully preregistered native PhysX run #37835511954](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37835511954) and independently repeated **same-seed** [run #37835549067](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37835549067) both completed all original-model simulator jobs and source audits. Re-running the same chosen seed set is not independent replication. Their actual task counts were:

| Paired same-reset-seed controller arm under TWO unknown ACKs | Pull /8 | Stack /8 | Total /16 | Privileged controller-target reads |
| --- | ---: | ---: | ---: | ---: |
| Source PPO, no fault (context only) | 7 | 8 | 15 | 0 |
| Continuous private target oracle (context only) | 8 | 7 | 15 | Unrestricted, not 0 |
| Optimistically treat both hidden holds as delivered | 8 | 1 | 9 | 0 |
| Strict exact-common-action or refuse | 0 | 0 | 0 | 0 |
| Four-history bounded action, no target readback | 4 | 3 | 7 | 0 |
| **Four-history bounded action, up to two reads if required** | **8** | **7** | **15** | **9** |
| Mandatory trusted target readback after each unknown command | 8 | 7 | 15 | 32 |

The selective and mandatory methods succeeded and failed on **exactly the same 15/16 and 1/16 states**, so **no task-success advantage** over mandatory readback is supported; their observed difference is the number of privileged controller-target reads (**9 versus 32**, or 71.875% fewer), not wall-clock time or energy. The zero-readback four-history method achieved 7/16 and failed or refused eight additional cases which the selective method completed, but it necessarily has less information, so this is not equal-information superiority. Its PullCube seed **230007** refused before reaching the second native fault; the strict exact-only method refused before the second fault in all episodes. These missing fault exposures are **not excluded**. The selective method physically reached **both actual fault steps in all 16 original episodes**.

The same-seed follow-up run logs record **99 K=4 control-decision steps** in the selective arm across its 16 task episodes, of which **92** have **actually dispatched** native controller actions followed by audit-only real target-state checks meeting the declared setpoint bounds. The other K=4 decisions need not correspond to executed commands; importantly, a proposed certified action that was intentionally replaced by the *fault-injected zero command* is never presented as a physically verified successful certificate. These 99/92 records are **repeated steps nested within only 16 original task seeds**, not 99 independent robotic trials. At least one source seed took two trusted reads and never reached a four-branch state because uncertainty was resolved before the second growth episode.

**Source-of-truth provenance:** The primary true, **byte-identical original PhysX JSONs** and SHA256SUMS are committed [under the public evidence directory](evidence/two_ack_khistory_original16_230001_240008/), with an [independent original-artifact GitHub SHA verification workflow](../../.github/workflows/archive-multi-ack-original16.yml). The [full actual-case report](TWO_UNKNOWN_ACK_KHISTORY_PROSPECTIVE16.md) includes the 16 task seeds and missed fault exposures. The test follows one Panda/PhysX controller family and two frozen PPOs; no hardware collision safety, general target-history source completeness, arbitrary networking or independent lab evaluation is established.

### 4.5 Outside-lab reproducibility gate — the acceptance is NOT yet external

An external reproduction must re-execute actual frozen PPO PhysX in a **different owner's fork**, with **new investigator-selected seeds**, unchanged exact source/certifier/belief-dependency hashes and full native task/fault/readback output. In particular, simply rerunning this author's registered 16 seeds or re-auditing the published JSON is valuable reproducibility but not new seed- or investigator-independent physical verification. A [GitHub outside-fork double-ACK workflow under PR #99](https://github.com/lindicaphxag-tech/ManiSkill/pull/99) is designed to enable this, with its current source identity and result hashes controlled in public Actions. Neither CI success in the contributor's own fork nor an upstream issue comment constitutes third-party endorsement.

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
- [Permanently archived original 32-state *negative* physical-response PhysX source: eight unmodified trial JSONs, original 32-row auditor, SHA256SUMS](evidence/physical_response_negative_32_140001_150008/). [Trusted post-merge source-byte archive audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37832249752) passed.
- [New64 exact original results and raw source links](ROBUST_QUERY_NEW64_PROSPECTIVE_RESULTS.md)
- [Independent falsification challenge](https://github.com/lindicaphxag-tech/kaggle/issues/67)
- [Third-party frozen PPO/benchmark origin: ActionShift](https://github.com/Archerkattri/actionshift)

**Responsible-claim statement:** All supplied source workflows were executed in the contributor's research fork. An external team has not independently repeated the physics outcomes. The definitive result in this draft is a preregistered **query-budget/task-outcome tradeoff on 64 new simulated states**, together with honest negative results and explicit missing evidence.

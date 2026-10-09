# When Should a Frozen Robot Policy Read Its Hidden Controller State?
## Evidence-Gated Authority under Unknown Action Execution

**Manuscript development draft · v0.2 · 9 October 2026**

**Evidence status:** an author-operated native ManiSkill PhysX research program, with exact released PPO hashes, prospective source protocols, complete original rows, independent offline score rechecks, and publicly executable outsider-fork tools. **Not peer reviewed; not accepted at ICRA, CoRL, RSS or any journal; not an external lab's independently reproduced result.** The scientific conclusions below are intentionally narrower than “safe transfer” or “action-space SOTA.”

### Abstract

Transferring a frozen manipulation policy across controller interfaces can fail even when their action vectors have the same units and dimensions. In a target-accumulating controller, the commanded pose depends on the previously commanded target, which may differ from the achieved robot pose and may become ambiguous after an unacknowledged command. We study *evidence-gated action authority*: a controller-specific mechanism that either reconstructs a target from attested command history, infers a candidate from a public physical response, or obtains an authoritative controller-state read when the available evidence cannot distinguish possible histories. In two released third-party PPO manipulation tasks executed in native ManiSkill PhysX, an outcome-blind 32-condition study of a public-response-or-query adapter reproduced every paired binary task outcome of a mandatory single-read controller (27 successes and five failures for both), while making 11 rather than 32 privileged target reads. This efficiency is conditional on an empirical, not physically certified, response envelope: a separate prospective cohort falsified that envelope on one true-history case, and an uncalibrated one-probe classifier made 15 wrong confident history inferences in 32 conditions. An additional 32-seed causal intervention on query timing found 31/32 task successes with seven evidence-triggered reads versus 32/32 with 32 fixed step-five reads, revealing a concrete success–information trade-off rather than universal adaptive superiority. We release full-denominator source data, failure witnesses and fresh-seed execution entry points. Our results concern commanded-target semantics and selected simulated fault conditions; they do not establish contact safety, general robot identifiability, or broad cross-embodiment transfer.

### 1. The precise scientific question

A frozen source policy `pi(o_t)` produces a desired action, but a target controller can interpret it in terms of *hidden internal commanded-target history*, not only measured arm pose. If a native control command was submitted and its acknowledgment was lost, a receiver may not know whether its internal target state advanced. A seemingly reasonable wrapper that replaces the old target with the measured achieved pose can silently change the intended physical setpoint.

We ask three separable questions: **(i)** Which previous-target evidence is sufficient to authorize translation of the *next* native action? **(ii)** Can public achieved robot motion remove uncertainty without revealing the private target state? **(iii)** When is paying for an additional authoritative target read preferable to either continuing with a bounded approximation or refusing? We use “authority” for **the provenance that justifies a commanded target**, **not** for a certified right to execute a safety-critical manipulation in hardware.

This is narrower than inventing delta-action conversion, a generic POMDP solver or action-interface system identification. ActionShift already explores hidden action contracts, belief/probe adaptation and released frozen-policy backbones; SPACE explores adaptive state/action representations across robots. Our contribution candidate is a *falsifiable controller-memory-state fault model and an empirically measured evidence-information budget*, not a claim of priority over those methods.

### 2. Controller-state mechanism and necessary limitations

Let `x_t` denote achieved tool pose in a verified coordinate frame, `h_t` the controller's stored previous commanded target, `u_t` a legal native delta command, and `d_t` the next desired physical target computed from a source policy. In a simplified translational target-accumulating chart,

`g_t = F(h_t,u_t) = h_t + u_t,`

rather than `g_t = x_t + u_t`. After ambiguous delivery there may be a finite candidate set `H_t = {h_t^(1), ..., h_t^(k)}`, not a single certified hidden state. The physically executed controller may hold its previous target, even when an API call returned or its receipt was lost.

**Simple impossibility fact (not a novel theorem).** In the affine translational chart, a common exact delta `u` can drive both distinct candidates `h_1` and `h_2` to exactly the same desired target `d` only if `h_1=h_2`, since `h_1+u=d=h_2+u`. Absent clipping, the best worst-case translational displacement error over two candidates is at least half their separation in the chosen norm. Bounded controls, different frames, rotations and controller saturation may further restrict feasible common actions. **A bounded *commanded-setpoint* error does not imply manipulation task success or safe contact.**

**Variant A—certified only relative to attested semantics.** If controller frame, units, update law and command acknowledgments are known, carry forward a source-independent target-history observer. If delivery was uncertain, represent both possible targets. When one common native action falls within an explicitly declared commanded-target error budget for every state candidate, a conservative setpoint translation may be authorized. Otherwise, either refuse or consume one privileged read of the actual target and resynchronize.

**Variant B—empirical public response followed by conditional authority.** After one identical native zero-arm-delta diagnostic action, observe public achieved positions `x` and `y`. Given two action-history-computed target hypotheses `M_h`, compute

`r_h = min_{alpha in [0,1]} || y - x - alpha*(M_h-x) ||_2.`

Using a **task-specific empirical envelope** `epsilon`, fit the response under each history. If exactly one candidate has `r_h <= epsilon`, provisionally use that candidate without reading private memory; if neither or both fit, issue one authoritative target read before continuing. `alpha` and `epsilon` are **NOT independently attested physical dynamics** and do not yield a general safety/identifiability certificate.

**Important implementation distinction:** Variants A and B were evaluated as related **different concrete controllers on different source-seed cohorts**. Results from one cannot automatically be assigned to an unevaluated combination of both. A unified implementation and cross-family trial would be a separate new experiment.

### 3. Benchmark integrity and comparators

All native task trials use official ManiSkill CPU PhysX; the PPO policies are unchanged externally released ActionShift checkpoints, and no policy training occurs. The physically simulated missing-acknowledgment conditions explicitly distinguish an **actual applied native command** from an **actual neutral arm command**. Neither is evidence of real ROS/TCP packet dropping, reordering, force/contact safety or unknown plant calibration.

We compare actual independent simulator-stepped arms under matched seeds and task horizons, and preserve **every source seed and failed episode**. Privileged reads are separately counted; constantly reading actual private target and querying conditionally are **not equal-information arms**. Binary official task success is evaluated apart from correctness of the inferred hidden target history. Where matched “fault truths” share a reset seed, they are paired counterfactual conditions, not independent policies or independent robot operators.

| Experiment, original native PhysX cohort | Prespecified task/fault population | Decisive result | Interpretive limit |
| --- | --- | --- | --- |
| Trusted acknowledged action history | 64 independent new task seeds | Independent target-history observer and live-private-memory arms both 57/64 binary successes, achieved-pose-memory substitute 11/64 | Requires reliable delivery receipts and known controller recurrence |
| Simple public nearest-command-target guess | 32 task × command-truth states | **15/32 WRONG confident hidden-history labels**, 19/32 task successes | A completed task does not imply correct latent state classification |
| Frozen historical empirical public response | 32 fresh task × truth conditions | 24/32 unique labels with zero observed wrong; **1 TRUE history excluded by the response model**; 22/32 task successes | The empirical plant-error envelope is not generally valid |
| **Public-response-or-one-read** | **32 further fresh task × truth conditions** | **27/32 success BOTH conditional and mandatory**; **11 vs 32 private target reads**, exact 32/32 binary outcome agreement | Not statistical equivalence or hardware safety; source-confirmed, author-operated |
| Actual PhysX query-time intervention | **32 entirely different reset seeds** | Event-triggered **31/32 success, 7 reads**; fixed t3 **31/32, 32 reads**; fixed t5 **32/32, 32 reads**; fixed t6 **27/32, 28 reads** | Fixed t5 wins on one task state; cannot claim universal adaptive success |
| Strict shared two-per-eight budget | 64 other registered task seeds, 8 physical trial shards | Capped trigger **50/64 using 10 reads**, fixed preplanned schedule **44/64 using 16**, discordances **9 vs 3** | **PRIMARY PREREGISTERED FAULT-EXPOSURE GATE FAILED** on one StackCube seed; DESCRIPTIVE ONLY |

All studies used distinct indicated source cohorts except explicitly noted within-study paired command-truth states. Do not pool their numerators as if testing one identical algorithm, common outcome population or precommitted joint hypothesis.

### 4. Strong positive finding: fewer target reads at the same observed paired outcome

The most direct public-motion study used PullCube seeds `180101–180108` and StackCube seeds `190101–190108`, each under two actual simulated command-execution truths, for 32 task/truth conditions and **16 distinct reset seeds**. Six physical controller arms ran independently from corresponding resets. The hybrid queried a privileged target **only** after the public motion observation failed to select exactly one target history.

Both the conditional hybrid and the mandatory target-read comparator succeeded on exactly the **same 27 of 32** conditions and failed on the **same five**. There were no paired success discordances. The hybrid used **11 privileged decision reads**, and the mandatory comparator 32. Thus the realized reduction was **21/32 = 65.625%** of mandatory privileged reads in this finite cohort. The public response selected 21 histories without private state, with **zero observed wrong confident labels in this sample**. This establishes a concrete cost/outcome observation, NOT population-level noninferiority, zero future errors or an independently proven physical error bound.

**Audit links:** [full original unchanged JSON and SHA256](./evidence/observability_gated_query_fresh32/) · [actual eight PhysX source jobs](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833095443) · [independent source-only audit after auditor variable-shadowing correction, GREEN](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833936506).

### 5. More decisive counterexample: physical query timing and value of information

The first proper actual-simulator timing intervention was preregistered **before** physical outcome collection, on fresh PullCube seeds `280001–280016` and StackCube seeds `290001–290016`—32 distinct task seeds. At each seed, independent PhysX worlds used a zero arm command at step 2 with unknown ACK. The evidence-triggered arm queried if its fixed robust goal bound rejected; fixed query arms instead read exactly at step 3, 5 or 6 (unless they refused before the intended read). Every arm controlled a real simulation rather than having branch outcomes synthetically substituted.

| Arm | Task success | Actual privileged target reads |
| --- | ---: | ---: |
| No read, robust approximate goal | 24/32 | 0 |
| **Evidence triggered** | **31/32** | **7** |
| Fixed query at step 3 | 31/32 | 32 |
| Fixed query at step 5 | **32/32** | 32 |
| Fixed query at step 6 | 27/32 | 28 |

Against fixed step 5, the evidence-triggered arm had **zero** exclusive wins and the fixed arm **one** exclusive win, **StackCube seed `290012`**. The exploratory two-sided exact paired sign test has `p=1` for this single discordance; it does not prove population equality. The fixed step-five method buys one additional observed success with 25 additional privileged reads. If one *post hoc* defines descriptive utility `U = task_success_count - lambda * target_read_count`, the two arms have equal observed utility at `lambda=1/25=0.04` successes per read. **This is an interpretation tool, not an experimentally validated optimal decision threshold.**

The exact original eight 4-state shards, an independently recomputed full audit and SHA256 provenance are permanently archived at [query-timing causal source evidence](./evidence/query_timing_causal_new32_280001_290016/). A fresh [Python 3.11/3.13 source-hashed Pareto audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37897331088) checks the original full denominator, reads, paired seed `290012`, source tampering and the exact unadjusted sign test. Its public source is [`review/query_timing_frontier.py`](./review/query_timing_frontier.py). The source-only analysis introduced **no new physics execution**.

### 6. Negative but necessary: strict shared-budget exposure failure

A separate **predeclared, strictly shared 16-token ceiling** study used PullCube seeds 360001–360032 and StackCube seeds 370001–370032. Every registered seed and each of nine actual controller arms were retained. The completed original offline audit [`37896670586`](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37896670586) found:

- capped evidence-triggered method 50/64 successes with **10** reads;
- fixed-budget schedule 44/64 with **16** reads;
- paired successes differing: capped-only **9**, fixed-only **3**, exploratory two-sided exact `p ≈ 0.146`.

**Do not use this as confirmatory efficacy evidence.** At **StackCube seed `370029`**, seven faulted arms refused an **unrepresentable native target rotation at pre-fault step 0**; the planned native hold fault at step 2 never occurred. The preregistered all-64 fault-exposure **primary gate therefore FAILED**, even though the exact original source-shard audit itself eventually ran green. The study remains valuable as preserved **descriptive/safety-of-measurement evidence**. A new entire prospectively sealed cohort is needed to make a compliant confirmatory claim; merely excluding or replacing `370029` would be outcome-conditioned selection.

### 7. Scientifically supported claims, and claims still missing

**Supported in simulation:**
1. When controller goal updates are accumulated, previous commanded-target memory—not necessarily achieved tool pose—can materially change frozen policy task performance.
2. A separately implemented confirmed-command history observer can recover target semantics when receipts are reliable, without continuously reading private goals.
3. A calibrated public-motion observer coupled to a conditional authoritative read reduced private target information cost while retaining **all observed paired binary outcomes** on a prospectively registered finite 32-condition cohort.
4. Actual physical query timing matters. A fixed time-5 read may sometimes produce one more success than an evidence-triggered read, at greater measured information cost.

**NOT supported:**
- universal/novel first-ever action adaptation, hidden-state system identification or minimax mathematics;
- safety of robot contact forces, collisions, trajectory feasibility or real unknown network ACK packet delivery;
- independent validity of a four-seed-trained response-model envelope or no errors on future tasks;
- task-level policy generalization to trained VLA models, untested embodiments or hospital robots;
- statistical population equivalence from a zero-discordance cohort;
- formal CoRL/RSS/ICRA paper acceptance, official ManiSkill upstream adoption, outside-lab validation.

### 8. Highest-leverage next tests (required before a strong publication)

The scientific bottleneck is no longer “more successful author-owned CI.” Three missing falsifiers are critical:

**Equal information cost:** freeze the same total number of privileged target reads under event-triggered versus a competitive *state-independent timing/allocation* policy on a **genuinely new full-fault-exposure cohort**. Separate a cap, entitlement, and exact realized expenditure. Predeclare how to handle pre-fault controller refusal—do not accidentally relabel it as an injected fault.

**Mechanistic generalization:** test a *different maintained robot/controller implementation* with its own released frozen task policy, or a genuinely different actuator/servo-gain environment. The existing Fetch/XArm6 native controller command-target checks are not a successful transferred policy on either embodiment. Calibrate trustworthy response-model uncertainty and report when it excludes the real history.

**Unbiased external adoption:** ask an unaffiliated research group to fork the [one-click real PhysX fresh-seed experiment](https://github.com/lindicaphxag-tech/ManiSkill/actions/workflows/external-observability-gated-query-replay.yml) and publish full original JSON/provenance including failures. An invitation, own-fork PR merge, or own CI check is **not external recognition**.

### 9. Reproduction and available implementation

All links are to the current **contributor-owned** GitHub fork; they are not official upstream ManiSkill releases. An independent reviewer should begin with [the complete reproducibility guide](./OUTSIDE_REPRODUCTION_GUIDE.md) and [the top-level audit packet](./review/README.md). One command recomputes timing statistics from untouched archived source files, without installing a simulator:

```bash
python -m research.frozen_policy_transfer.review.query_timing_frontier \
  --output /tmp/query_frontier.json
```

To rerun physics on unseen seeds, use the original six-arm [external selector](https://github.com/lindicaphxag-tech/ManiSkill/actions/workflows/external-observability-gated-query-replay.yml), or fork into an unrelated lab's GitHub organization.

### Reviewer-facing contribution statement (pending external scrutiny)

We propose **controller-memory action authority as an explicit information-provenance problem for frozen-policy transport**: first represent which physical target history is known, then decide whether a bounded common action, a public physical probe, an authorized state query, or refusal is justified. Original PhysX results and negative controls indicate that state authority, not just action vector compatibility, can drive the measured task outcome and information cost. Whether the proposed evidence gate generalizes better than existing ActionShift belief/adaptation under a matched information budget is **an open question**, not a result established by this manuscript.

**End of draft v0.2 — no external accept/review claim.**

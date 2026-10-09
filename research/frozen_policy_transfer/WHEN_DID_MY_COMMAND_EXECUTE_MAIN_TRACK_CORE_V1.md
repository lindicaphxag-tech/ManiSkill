# When Did My Command Execute?
## Execution-History Observability and Selective State Reads for Frozen Robot Policies

*Main-track submission core, v1 — 9 October 2026. This is a research-paper draft, not accepted or externally peer reviewed. The extended record and full negative-experiment ledger are in [v2.3](WHEN_DID_MY_COMMAND_EXECUTE_MANUSCRIPT_V2_3.md). Authors should maintain the conference's current anonymous PDF template rather than submitting this Markdown directly.*

### Abstract

A robot controller can remember a commanded target pose while its source policy expects actions relative to the achieved end-effector pose. When execution acknowledgements are lost, the external action stream is compatible with several latent controller-target histories, so naïvely repeating the policy's displacement can silently change semantics. We study whether public end-effector motion can identify the complete latent SE(3) execution history and selectively avoid a privileged controller target read. We propagate finite histories through the known native action chart, test motion compatibility using a fixed empirical observation envelope, and query native state when no unique public candidate survives. Our evidence separates *information-only substitution* from *end-to-end policy performance*. With physically identical fault-step commands and one identical downstream compiler, public inference and mandatory readback have equal paired task outcomes on 64 native PhysX states (53 joint successes, 11 joint failures) while using 48 rather than 64 privileged reads. A disjoint preregistered 64-seed, four-ACK-history factorial physically executes 2,304 independent ManiSkill controller-policy worlds. On all 256 source-seed/truth cells, our adapter succeeds 221 times and makes 195 private reads, compared with 202 successes and 221 reads for a prespecified task-aware control (seed-clustered two-sided label-swap sensitivity p=0.00241). Independent native motor-action traces reveal predecision t3 intervention differences in 64 of 256 pairs, so the second result measures end-to-end method behavior rather than the isolated causal value of a query. Separately audited false history identification and a prospectively unhelpful extra confidence-margin gate delimit the method's reliability. The results establish a falsifiable execution-state observability problem and a selective information mechanism, not guaranteed identification, independent-laboratory replication, or physical robot safety.

### 1. Introduction: an interface fault that ordinary policy uncertainty misses

A source policy may emit an end-effector-relative delta while its destination controller accumulates deltas onto its *previous commanded target*, not its achieved physical pose. After an unknown ACK, the same policy observation and nominal command can correspond to different native target-reference states. This is neither merely an uncalibrated policy action distribution nor an unknown action-axis mapping: the chart is known, yet the *executed command history* is hidden.

**Question.** When does public achieved motion disambiguate the full internal target history, and when should the adapter pay for a private native-controller target read?

We contribute:

1. **Execution-history state:** four full SE(3) latent target histories under two independently applied/held unknown ACK events, and an explicit set-membership abstention boundary. We do not claim set-membership itself is new.
2. **Information-isolated native causal control:** a physically matched-prefix, shared downstream belief/compiled action implementation, with original 64 paired task outcomes and counted private reads.
3. **Registered end-to-end factorial:** a *separate* 64-seed × four-ACK-truth study with 2,304 actual native PhysX worlds, exact initial-state audit, paid sensing and actor-specific real t2/t3 motor traces, plus a seed-clustered effect calculation.
4. **Falsification rather than selective reporting:** one previously confidently wrong public history, a prospective negative confidence-gap test, and failed physical-source audits preserved verbatim.

The full generality claim is intentionally narrower than VLA policy adaptation: these studies use two released frozen PPO task policies on one native Panda target-memory chart.

### 2. Problem and observability mechanism

Let the known native pose-update chart be \(F\). The hidden ACK event \(b_t\in\{0,1\}\) indicates a physically applied native arm command at event \(t\); \(b_t=0\) means held/no update. For two unknown ACK events, the observer tracks a finite set of possible commanded target transforms
\[
\mathcal H=\{h=(b_2,b_3):b_2,b_3\in\{0,1\}\},\qquad
T_{t+1}^{h}=F(T_t^{h},u_t,b_t).
\]
The different \(T^h\) must be propagated under the actual native target-relative semantics; extrapolating the policy's achieved-relative delta alone is incorrect. A complete candidate carries target XYZ **and** orientation, even though the present public discriminator primarily uses observed achieved XYZ; two candidates indistinguishable in XYZ cannot be assumed distinguishable in orientation.

A known-delivered neutral arm probe at t4 exposes before/after public achieved motion \(y\), without revealing the private target. For candidate history \(h\), the published motion-response model supplies \(\hat y_h\) and residual \(r_h=\|y-\hat y_h\|_2\). With the already calibrated fixed \(\epsilon_{task}\) and 2-mm competitor margin \(\delta\), accept a unique complete history \(h^*\) if
\[
r_{h^*}\le\epsilon_{task},\qquad
\forall h\neq h^*:\ r_h>\epsilon_{task}+\delta;\qquad\delta=0.002\ \text{m}.
\]
Otherwise, make one *counted* native private-target read, collapse the hypothesis set and continue policy execution. The empirical \(\epsilon_{task}\) is not a mathematically guaranteed conservative motion/noise bound.

**Identification boundary.** If two physically possible target histories have intersecting observable response sets for the available public measurements, no deterministic decision can identify the true history at all observations in the intersection. Under independently validated complete response envelopes, a unique compatible candidate would be conditionally identifiable. Our empirical motion envelope does not establish that premise. A confidently wrong public history in an external seed cohort of the *same author's experiment* directly demonstrates nonzero practical identification risk.

**Information costs:** native privileged target read; two public achieved XYZ samples for each exposed public observer; one *physically executed* neutral t4 step; all policy motor displacement and latency. A 25% reduction in *privileged reads* is not a 25% latency reduction.

### 3. Experimental protocol and independent falsification gates

We use released fixed PPO checkpoints for PullCube and StackCube (no training). Both fault commands at t2 and t3 are genuinely physically applied or held in separately stepped ManiSkill CPU PhysX controller worlds, not merely switched in an offline array. Applied/held truth is available to an audit-only source trace, never to the method.

**Experiment I: isolated information treatment.** A fresh 64-task sample physically dispatches the same actual t2 and t3 native six-axis commands for the public and fixed-reader arms, and the same neutral probe t4. The audit verifies predecision achieved and commanded target poses to a fixed tolerance. Both arms then use the **same** `UncertainDeliveryBelief`, same `normalized_target_delta(... old_override=single_history)` native compiler and same ACK updates; the deliberate difference is public admissible history or private read versus mandatory private read. Outcomes are audited independently from the exact original physical shards.

**Experiment II: fully crossed end-to-end comparison.** A new, disjoint *preregistered* population uses PullCube `3210001–3210032` and StackCube `3220001–3220032`. Each one of 64 original source seeds is run under all four actual ACK patterns. All 64 four-condition initial public observations are bit-identical. With nine separately stepped controller-policy worlds per physical condition, there are 256 task cells and 2,304 original native simulator worlds. Every source/truth cell remains in the denominator, including early failure. Preselected comparator, third-party checkpoint identity, policy horizon, action chart and acceptance thresholds are frozen before outcomes.

The **prespecified practical superiority threshold is 4 percentage points** in native task success against the task-aware control. The source auditor treats one seed's four physical fault truths as **one correlated cluster** when calculating a two-sided method-label swap sensitivity and a seed-clustered bootstrap. No 256-row iid testing.

**Transparency gates.** A previous factorial's initial-state hash check failed on seven StackCube seeds; we disclosed the failure rather than retaining only valid seeds. In the new 64-seed confirmation, all 32 native physics shards passed but the initial all-run workflow selected the obsolete 32-seed auditor; we preserve that failure and separately re-run the already-frozen correct 64-seed auditor over **unchanged byte-identical** original source files. Neither source-only re-audit is another independent physical replication.

### 4. Results

| Physically executed comparison | Public complete history or read | Comparator | Interpretation |
|:--|:--|:--|:--|
| 64 physically matched-prefix and identical downstream-compiler task resets | 53/64 successes; **48** native private reads | Mandatory read: 53/64; **64** reads | Paired 53 both-success, 11 both-failure. **Information-specific** reduction in charged reads, no observed task-success difference |
| Fresh 64-seed × four physical truths (256 task cells, 2,304 worlds) | **221/256** successes; **195** private reads | Prespecified task-strong: **202/256** successes; **221** reads | **+19/256 = +7.421875 pp** observed end-to-end task success; 26 fewer private reads. Paired 197 both-success, 30 neither-success, 24 public-only, five comparator-only |

The confirmatory factorial's seed-clustered two-sided label-swap *sensitivity* is **p = 0.002410888671875**; cluster bootstrap percentile 95% success-gap interval **[+3.125%, +12.109%]**. The positive descriptive gain exceeds the preregistered 4-percentage-point criterion; no randomized-method causal treatment assignment is implied.

**Essential motor-action negative evidence.** From the original 256 physical trajectories, public and task-aware arm actions match at t2 in all 256 worlds but at t3 in only **192/256**; against mandatory readback they match **128/256** at t3. Both original methods physically receive the known neutral t4 at all 256 cells. Thus the full factorial success gap is an **end-to-end policy treatment** and cannot be attributed solely to information availability. Experiment I—not Experiment II—isolates the private-read mechanism more cleanly.

**Reliability and active-probe counterexamples.** A separate physically registered 64-seed cohort logged **one confidently wrong public history** (StackCube 1730027). An extra 4.5-mm best/second residual-gap rule, chosen after examining that failure, was subsequently executed *prospectively* on a new 64-state 640-world cohort. It achieved exactly the same 52/64 paired task successes as the original rule with **41 instead of 39 private reads**, with zero observed wrong histories under either rule in that new cohort. This is a negative result for simplistic margin tuning. A small distinct genuinely physical 32-state nonzero-active versus neutral-probe pilot also yielded **28/32** official successes for both, with more private reads (**28** active versus **26** neutral); the active intervention additionally spent a real nonzero arm displacement. This pilot is not an optimized strong active-probing baseline and is not pooled with the main population.

### 5. Related work and novelty boundary

**Uncertainty-aware policy steering.** [When to Act, Ask, or Learn (RSS 2026)](https://www.roboticsproceedings.org/rss22/p142.html) already selects whether to act, clarify or intervene using conformal calibration in simulation and hardware. We therefore claim *no invention* of selective asking, abstention, or uncertainty-aware policy steering. The distinction is a **hidden native commanded-target execution-history state** after unknown ACK events, with physical source action semantics and auditably counted privileged readbacks.

**Inference-time verification.** [Visual Verification Enables Inference-time Steering and Autonomous Policy Improvement (RSS 2026)](https://www.roboticsproceedings.org/rss22/p079.html) examines generalist policy selection, steering and autonomous learning; it has broader deployment demonstrations. Our subject is controller target-history observability under known action chart rather than general-purpose visual verification.

**Native controller and dynamics adaptation.** Action-channel mapping, gain and torque correction, and representation changes are meaningful adjacent problems, but they neither prove that a missing ACK has been resolved nor imply a correct private target. Our own full-factorial predecision action differences prevent an isolated-query causal claim against all comparisons.

### 6. Discussion and limitations

**What can be claimed.** The same-source information isolation experiment demonstrates private read substitution at unchanged observed task outcomes, under the tested Panda controller and two frozen PPO tasks. The separate full-factorial registered confirmation demonstrates a positive, reproducible *end-to-end* success/read frontier on fresh native simulator seeds, conditional on one particular stateful controller chart and fault generator.

**What cannot.** Empirical residual calibration is not a validated actuator uncertainty envelope, and observed zero wrong labels in one cohort is not zero deployment risk. The 256-cell factorial has 64 independent source-reset clusters and action-level confounds; the p-value is a method-label swap sensitivity under assumptions, not a randomized causal p-value. An authored GitHub workflow and preserved SHA256 sources do not equal outside-investigator replication. We have not demonstrated true delayed/reordered packet delivery, collision-safe active probes, a separate native controller family with task-competent frozen policies, full VLA fault recovery or hardware safety.

**Required next discriminating tests.** (i) Physically frozen action-prefix plus common-code postquery baseline at greater power, (ii) task-competent frozen VLA on an *actually stateful* target-memory controller under crossed unknown ACKs, (iii) same real physically available probe/sensing/latency budget versus a strong actively optimized selector, and (iv) independent researcher-selected seeds and original physical trace publication. These are specific open experiments, not completed contributions.

### Reproducibility and independent reviewer access

The evidence is source-verifiable without trusting any summary table: [64 matched-prefix original source](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/shared-compiler-evidence-original64-20261009/research/frozen_policy_transfer/evidence/shared_compiler_twoack_original64_1480001_1490032), [256-cell × 9-world complete actual native original sources, SHA256 and independent auditor](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/confirmatory256-original-source-audit-20261009/research/frozen_policy_transfer/evidence/confirmatory_fourtruth_original256_3210001_3220032), [separate physical motor/probe cost audit](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/confirmatory256-original-source-audit-20261009/research/frozen_policy_transfer/evidence/confirmatory256_real_motor_probe_cost_original), and [failed original whole-workflow audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37934425888). An outside researcher must run newly chosen original task episodes and publish their own sources; recomputing the author's JSON is only an independent *audit*, not a physical reproduction.

**Research status:** publishable author-run simulator evidence with real positive and negative findings; *not* an accepted main-track or excellent-paper result. Acceptance and independent recognition cannot be guaranteed.

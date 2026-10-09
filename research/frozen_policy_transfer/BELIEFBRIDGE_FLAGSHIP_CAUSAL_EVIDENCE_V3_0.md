# BeliefBridge — Complete Controller-History Evidence under Unknown Command Execution

**Reviewer-facing research core v3.0 · 9 October 2026**  
**Evidence tier:** author-operated, source-hash-controlled real ManiSkill CPU PhysX with frozen third-party PPO. **Not externally replicated, peer reviewed, robot-hardware validated, or a demonstrated VLA task-level improvement.**

## Contribution in one sentence

When an action acknowledgement is missing, do **not** infer the controller's last commanded target from the observed achieved end-effector pose. Preserve a finite belief over *complete* possible target histories, test whether measured public motion uniquely supports one history, and consume an explicit privileged controller-target read only when that evidence is insufficient.

## Why this is a distinct, falsifiable question

Conventional policy-to-controller action adaptation assumes the native interface or target memory is known at execution time. Here, two unknown receipts leave up to four target-memory histories even when the native action chart is perfectly specified. This is **execution-history uncertainty**, rather than full unknown ABI, arbitrary dynamics shift or learned world-model prediction.

Related work on unknown action contracts includes [ActionShift](https://github.com/Archerkattri/actionshift) and [ActionABI](https://github.com/Archerkattri/actionabi). Those works address hidden wiring, frame/gain/target/lag semantics and active identification. We do **not** claim to invent action probing or finite-belief adaptation. The restricted question here is whether *an unobserved APPLIED/HELD execution bit in a known target-relative controller* can be resolved from public physical evidence, and whether that trades off successfully against consuming trusted target-memory reads when a frozen pretrained manipulation policy continues.

## Exact mechanism and scientific claims

Let `M_t ∈ SE(3)` be the native controller's **last commanded target**, not its achieved end-effector pose. With known command `u_t` and hidden delivered/executed truth `z_t ∈ {0,1}`:

`M_(t+1) = F(M_t,u_t)` when `z_t=1`; otherwise `M_(t+1)=M_t`.

For unknown receipts, propagate **all** admissible complete position+quaternion histories, without reinterpreting achieved XYZ as target truth. Each next command must satisfy conditional geometric target bounds for every still-representable hypothesis, or must request an authoritative read/refuse.

At a precommitted known-delivered neutral native probe, compare original per-history public achieved-XYZ responses against a **previously frozen empirical** gain/noise envelope. A history is publicly admitted only when exactly one *entire SE(3) history* is compatible and every alternative exceeds the predeclared residual+margin. **All other outcomes (including zero survivors) require one logged authoritative read or refusal.** This is an empirical decision rule, **not** a mathematically certified physics/safety guarantee. It is vulnerable to response-model misspecification, contact changes and observation shift.

The independent experimental lever is the **privileged target memory readback count** at comparable official frozen-policy task outcome; public samples/latency/actuation/force have to be charged separately. A reduction in reads does not alone establish total information efficiency.

## Authentic evidence ladder — distinct cohorts, not pooled IID trials

| Physically executed source cohort | Native fault truths | Public-history success / private reads | Main actual comparator success / private reads | Scientific boundary |
|---|---|---|---|---|
| [Genuinely seed-disjoint PPO64 original #37916917436](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37916917436); [archive #37917471957](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37917471957) | t2 true APPLIED/HELD balanced; t3 physically HELD across all trials | **57/64 · 33** | task-aware **56/64 · 52**; fixed **57/64 · 64** | t3 known generator is fixed; not full 2×2 execution truth; early development cohorts include separately disclosed seed reuse |
| [True 2×2 PPO64 original #37919576643](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37919576643); [source archive #37920293099](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37920293099) | Both t2 and t3 physically APPLIED/HELD, balanced across **different** resets | **55/64 · 50** | task-aware **56/64 · 59**; fixed **57/64 · 64** | Original main comparator arms did not have guaranteed identical pre-query physical prefixes |
| [New exactly matched-prefix 2×2 PPO64 original #37921574816](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37921574816); [source-only corrected audit #37922292514](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37922292514) | Both t2 and t3 physically APPLIED/HELD; all 64 new resets pass audit-only pre-t5 identical PUBLIC/FIXED native-command, achieved-pose and target-pose parity | **56/64 · 43** | **physically prefix-matched FIXED**: **55/64 · 63**; separately stepped task-aware **55/64 · 58** | Only PUBLIC vs FIXED is a strict physical-prefix pair; task-aware is not automatically matched. Different public-vs-private information access remains. |

**Latest original matched-prefix audit details:** 64 new task/reset states, 576 individually physically stepped native controller worlds, 21/64 public-confident history admissions, **zero *observed* wrong-confident admissions** in this cohort; all 64 public methods experienced both actual faults. Pair *public vs task-aware* (not strict prefix-matched) is 55 both successful, 8 both failed, 1 public-only, 0 task-aware-only. Neither 1 discordance nor the 56-vs-55 unpaired headline supports task-success superiority or statistical noninferiority.

**Audit failure transparently retained:** The original 576-world run ended `failure` at its *final independent auditor* because of an incorrectly named Python import; its genuine eight physics shards completed successfully. No physics was rerun or altered for the fix: [separate source-only audit job #37922292514](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37922292514) verifies pinned exact original physics/prereg/model blobs, downloads all eight original shard artifacts, fixes only the nonexistent audit-module reference, and independently checks every original row. The originally failed audit remains public and must be mentioned in any research release.

### A decisive negative result that prevents a simplistic method claim

[Source-frozen one-public-probe vs two-public-probe original #37921282989](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37921282989): **64 new task/reset states, 640 real PhysX worlds**, physically equal two-step neutral actuation for both observation strategies.

| Strategy | Official task successes | Privileged reads | Confident history admissions | Public achieved-XYZ samples | Wrong-confident |
|---|---:|---:|---:|---:|---:|
| Single public response segment | 48/64 | **41** | **23** | **128** | 0 |
| Two public response segments, both required compatible | 48/64 | 43 | 21 | 256 | 0 |

Additional sensing did **not** improve official task success, and the stricter two-segment admission consumed two more private reads in this cohort. Do not frame two correlated samples as independent. A different earlier full-joint fault cohort reported **two wrong confident authorizations**; we must preserve that counterexample to reject any general false-zero-error guarantee. A more robust monitor must be tested on **new** fault regimes before method promotion.

## Exact limitations that must stay in abstract or main text

1. One controller family (Panda) and two frozen published PPO task families in the matched-prefix task-level study; xArm6 native target-restoration tests elsewhere are **task-free** and not robot-generalization of these policy success results.
2. Balanced 2×2 truth patterns **between reset IDs**, not all four physical truths on each identical reset. Within any given truth the policies are paired, but cross-truth causal estimates require full factorial same-reset tests.
3. Read economy is **not information-equivalent or energy-equivalent**: public XYZ samples, actual probe commands, latent-model priors and runtime latency must be compared with a matched information/actuation/latency-cost active-identification baseline.
4. No real packet transport failures, no pressure/force/collision/hardware-safety certificate, no treatment of arbitrary unavailable native action contracts. Actual observed task success is not a physical safety guarantee.
5. All current physics is **author-operated**, not independent outsider reproduction, and the draft PRs in a user's own fork are **not** upstream acceptance.
6. SmolVLA/LeRobot published-model forward and native LIBERO rollout pilot are an **independent, incomplete gate**; do not add any VLA success or VLA recovery percentages to the PhysX PPO outcomes.

## Reviewer-ready sequence of next falsification gates (ranked by scientific value)

**Gate A — causal and budget correctness.** Preserve the original 64×9 matched-prefix source and audit; report exact paired PUBLIC-vs-FIXED episode outcomes and failure timing, plus public-sensor cost and per-trial read expenditure. Compare to an actually executed ACK-specific active-information-gathering baseline with identical allowed public frames and real motion budget. These cannot be replaced by posthoc synthetic scores.

**Gate B — failure-model shift.** A new prospective same-reset full 2×2 experiment (all four truth patterns per reset) under varied contact and gains, calibrated using *separate* training states; include confident-wrong counts and abstentions. A repeated original held-out set without independent precommit is not prospective evidence.

**Gate C — policy/embodiment transfer.** Reuse a **task-competent** published matching checkpoint on another independently verified native controller/robot family. Avoid pretending Panda PPO action tensors generalize to xArm6 or that LIBERO 'relative' necessarily means accumulated controller target.

**Gate D — external research acceptance.** An outside investigator picks genuinely new seeds and runs the pinned source on their own fork, publishes actual raw artifacts with independent SHA proofs, and confirms or falsifies our specific claim. No author-controlled CI should be described as independent outside-lab adoption.

**Publication claim ceiling TODAY:** A focused, reproducible finding about *execution-history observability and selectively spending privileged controller-state queries* on frozen simulated PPO manipulation tasks. There is **no justified claim today** of generally safe action authority, generic VLA recovery superiority, statistically verified noninferiority, or top-conference acceptance.

# When Did My Robot Command Execute?
## Matched-Information Controller-State Readback under Unknown Execution

**Reviewer-ready working manuscript v2.3 · 9 October 2026 · unreviewed author-operated native PhysX**

### Abstract

A frozen robot policy can issue geometrically valid Cartesian deltas but still command the wrong target when a controller integrates motions from its internally remembered target and execution acknowledgments are missing. We study whether observed end-effector motion provides evidence sufficient to select a complete finite target-history hypothesis without an expensive privileged controller-target read. Our adapter retains execution-consistent target hypotheses, checks native action representability, and authorizes a full target state only when exactly one candidate explains the public motion within an empirically calibrated compatibility tube; otherwise it takes one accounted authoritative readback. Unlike coordinatewise rotation consistency tests, the history selection inherits the candidate's already-computed full pose. We establish a harder, paired causal comparison: 64 original PhysX task resets with both physical ACK truths applied or held, fixed pretrained external PPOs, and a verified identical physical pre-decision command/achieved/target-pose prefix for the public-history and fixed-read treatments. The public method succeeded on 56/64 tasks using 43 private reads; fixed-time readback succeeded on 55/64 using 63 reads. The paired difference was one task, with no claim of superiority or noninferiority. A separate 16-state, 160-world source-frozen same-information pilot observed 14/16 successes with 13 private reads for finite-history admission, compared with 14/16 and 16 reads for a precommitted 0.95 normalized-residual-weight heuristic and fixed read. A new, distinct preregistered 64-state matched-information comparison has begun; its result is **not yet known**. These results isolate the price of controller memory evidence under simulation, not hardware safety, real packet-loss recovery, or universal confidence guarantees.

### 1. The narrow contribution

Unknown delivery is an uncertainty over **which physical target memory transition occurred**, even if the native action mapping is documented. Given the original commanded-target memory \(M_t\), requested normalized action \(u_t\) and actual delivery truth \(z_t\),

\[M_{t+1}=\begin{cases}F(M_t,u_t),&z_t=1\\M_t,&z_t=0\end{cases}\]

Two unknown acknowledgements generate up to four full 6D target candidates with quaternion orientation. Blindly replaying a cached frozen-policy action chunk can silently treat its obsolete target history as current. A correct bridge must separately prove (i) physical action chart admissibility, (ii) membership of true target in the hypothesis set, (iii) public response-model validity, and (iv) availability of a readback/refusal route. A setpoint certificate does not provide contact/force/trajectory safety.

The algorithm's finite-history uniqueness is not a new identification theorem: for a public achieved-motion sample \(x\to y\), test candidate target position \(p_i\) using the historical residual

\[r_i=\min_{\alpha\in[0,1]}\|y-x-\alpha(p_i-x)\|_2.\]

Select the entire stored \((p_i,R_i)\) only when exactly one residual is within the fixed task epsilon and every alternative exceeds epsilon by the originally frozen 2 mm separation margin. Do not invent orientation from XYZ; it is inherited from the uniquely compatible **discrete history**. Read the trusted controller target once when ambiguous, unrepresentable or unsupported. The epistemic flaw is that epsilon is a prior **empirical**, not mechanically certified, bound; wrong confident decisions remain possible under dynamics/contact shift.

### 2. Existing prospective causal evidence: new physical matched-prefix 64

Experiment: exactly 32 fresh PullCube and 32 fresh StackCube reset IDs (`1380001–1380032`, `1390001–1390032`), two original unretrained publicly released PPO models, true four physical ACK patterns `held/held`, `applied/held`, `held/applied`, `applied/applied`, eight per task/truth, and nine physically stepped controller strategies per reset. The first two actual ACK-affected arm commands occur at native steps t2/t3; both alternative controllers physically execute the same known-delivered neutral t4 step and use identical pre-t5 native fault actions. A source auditor requires **achieved position+SO(3), hidden commanded-target position+SO(3), and actual dispatched fault action** to agree to `≤5e-5` between the specific new-public and fixed-target-reader comparator arms at the decision boundary. Hidden target getters used for this parity assertion are audit-only and are never handed to the experimental public method.

| Actually paired native PhysX treatment | Task successes on 64 | Actual private target decision reads |
|---|---:|---:|
| **Complete-history public witness or one read** | **56/64** | **43** |
| Fixed authoritative read at t5 | 55/64 | 63 |
| Task-ID preselected earlier strong controller | 55/64 | 58 |
| Zero-read always-assume-held | 39/64 | 0 |

Against task-labelled comparator, seed-paired exclusives are **one new-only, zero task-labelled-only** (55 both, 8 neither); exploratory exact test offers no evidence of stable population task-superiority. The fixed comparator's actual private read count is 63, not 64: do not invent a query when that arm terminated before it could read. The public method authorized 21 full-history candidates from the empirical public tube, with no observed wrong-confident indices. An iid hypothetical 0/21 one-sided 95% error upper bound is about 13.3%; this is not a valid physical-envelope reliability certificate.

**Coverage caveat:** The source audit reports zero states in which **every one of all eight faulted comparator arms** both survives until and takes a common t4 neutral step: exact-only/refusing arms may terminate naturally. Therefore, do **not** call all nine policies identical-prefix interventions. The causal pre-decision matched SE(3) **specific pair** of the public and fixed-read arms is independently checked for every source state; query-only interpretation is restricted to that comparison. Earlier preliminary CI failed because of a source auditor's misspelled import path, not because the genuine original eight physics shards failed; preserve the first CI failure. The original-source-only corrected-import audit completed successfully, with its original denominators and missing-coverage flag retained.

[Original full PhysX eight-shard run (first independent-source audit job failed on import)](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37921574816) · [Corrected-source independent original 64 audit (no rerun)](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37922292514) · [Permanent source-only research archive CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37922389404).

### 3. The real same-information statistical opponent, not a marketing label

An additional independently frozen native PhysX 16-state source experiment (`1700001–1700008` PullCube, `1710001–1710008` StackCube) introduces a physically executed *third* action-authority policy. It sees **exactly the same two public achieved XYZ samples** and neutral command as our original full-history selector, on the **same physical pre-t5 achieved and private-target pose**, but weights competing hypotheses by `exp(-0.5 (r/epsilon)^2)` and authorizes only if the top normalized weight reaches predeclared `0.95` and respects the prior compatibility gate. These scores are **not calibrated Bayesian posterior probabilities**. This is a useful simple, information-matched comparator, not the official ActionShift DualABI probe-and-belief algorithm.

| Frozen original 16-state pilot | Official task success | Private target reads | Public confident full-history selections |
|---|---:|---:|---:|
| Our complete-history compatibility gate | 14/16 | 13 | 3 |
| Same-information normalized residual-weight `0.95` gate | 14/16 | 16 | 0 |
| Compulsory same-physical-prefix t5 private read | 14/16 | 16 | Not applicable |

All three policies have the **same 14** original task successes; this pilot shows fewer counted private reads for our method under one precommitted heuristic competitor, not higher task success or a conclusive sample-efficient SOTA guarantee. Three observed confident correct histories are far too few to claim any safety probability, and this baseline's conservatism may be sensitive to its particular fixed score threshold. Original evidence includes true physically stepped ten controller worlds per seed; the source audit requires native command/pose equality before the decision and retains all failures.

[First fully completed 16-state original ten-controller PhysX CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37923604209).

### 4. New preregistered 64-state information-matched test — RESULT PENDING

Before implementing the new driver or seeing new outcomes, an immutable protocol registered PullCube `1760001–1760032` and StackCube `1770001–1770032`, the original unchanged method Git blob `6e039af56006827fc2fe063b541cfa3dcd1ddc89`, the original frozen published PPO checkpoints, the same 0.95 heuristic score, task epsilon/margin, t2/t3 physically applied/held joint truth balance, and the same paired physical t4 step. Each task/truth stratum contains eight unique states, with 10 separately stepped controllers per seed (**640 planned native simulator worlds**).

**The executable full 64-state experiment is running, but until eight original shards, full source hashing, all physical-prefix audits and 64-state recomputation pass, its task-success/readback metrics are unknown and no confirmed advantage may be claimed.** Any pre-decision mismatch is an invalid experiment, not a repairable positive outcome. Preserve every fault refusal and model-confident error, whether favorable or unfavorable.

[Immutable test protocol and code](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/matched-public-bayes-native16-20261009/research/MATCHED_PUBLIC_BAYES_NEW64_PREOUTCOME_V1.json) · [actual native PhysX CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924192162).

### 5. Related approaches and external-acceptance vetoes

ActionShift / DualABI already considers hidden compositional action semantics, active bounded probes, Bayesian-style beliefs and task-regret stopping. This study neither invents set-membership control nor task-value-of-information. The distinct and still-to-be independently adopted problem is the **executed/not-executed state transition of a known, stateful native target controller** under uncertain acknowledgements, alongside typed action validity and the right to query an authoritative target. Against an ActionShift-style active strategy, actual step, public sensing and privileged target cost units need to be harmonized; readback count alone is NOT a fair universal cost metric. A separate controller embodiment with a genuinely compatible frozen policy, real network fault injection, observed phase/contact distribution shift, and outside-laboratory independent reproduction are outstanding.

**Three non-negotiable claims boundaries:** all results are author-controlled CPU PhysX, not real ROS/TCP dropped ACKs or certified safety; two PPO tasks share one Panda controller chart, not multi-policy or multi-embodiment generalization; observed identical successes do not establish noninferiority without a precommitted margin and sufficient sample size. No official upstream method adoption, paper acceptance or independent third-party completed task reexecution is claimed.

### 6. Direct external reviewer falsification

Recompute existing SHA-backed original source rows, check every task and ACK truth, then independently choose NEW seeds in a different fork and reproduce the exact frozen native PhysX seven/ten-controller operation. Count real private decision reads (never after-the-step hidden audit getters), public XYZ observation events, actually executed neutral probes, rejected and nonrepresentable native commands, and binary official success. Publish disagreement and failure rather than selecting the best reported arm. A meaningful reviewer decision requires this evidence and matched-cost ActionShift-grade active sensing, not only this manuscript's stated point estimates.

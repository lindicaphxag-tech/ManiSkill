# Multi-ACK BeliefBridge: full untouched 64-state ORIGINAL native PhysX prospective result

**2026-10-09 — completed original frozen-policy, precommitted, source-audited native simulator experiment.** This is a full honest systems benchmark including negative cases. **No independent outside-lab replication, peer-reviewed acceptance, hardware safety, real network packet loss, or cross-robot generalization has occurred.**

## Reproducible original evidence (not simulated counterfactual splicing)
1. [Preregistration before new seed outcomes](../COMPOUND_ACK_NEW64_PROSPECTIVE_V1.md): PullCube seeds 420001–420032 and StackCube 430001–430032; no continuation from the development 400001/410001 cohorts.
2. [Full 64-source-state original real native PhysX run #37900209486](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37900209486): **9/9 jobs SUCCESS**, exactly 8 of 8 complete eight-seed native simulator shards and the frozen source contract.
3. [Original 64-source-state independently reconstructed evidence audit #37900694213](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37900694213): **SUCCESS**. The standard-library auditor downloads *all eight originally authored raw artifacts*, checks every original `SHA256SUMS` and source/checkpoint/protocol identity, all 64 per-seed seven-arm official task outcomes and true controller read counts, and every actual/masked residual audit. [Auditor source](./review/audit_compound_ack_new64.py).
4. [Full raw machine-readable analysis result JSON and original-artifact manifests](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37900694213/artifacts/11602396896) includes **all 64 rows**, with explicit identical reset-state pairing and negative outcomes retained.
5. Method/runner Git blobs frozen from the prior complete 16-case native PhysX experiment: `99836af14205fe3e95e52a2e0d68237c7c8a9045` and multi-target SE(3) certificate `36707a177549104ba5b4bd9bcebc76518f0d2840`. Original unchanged one-ACK runner/2-state certifier SHA pinned separately; released ActionShift Pull/Stack PPO checkpoints verified per task. **No policy was trained or adapted on the prospective test states.**

## Original full-denominator tasks (64 independent physical reset states; 448 matched native controller worlds)

| Actual controller world | PullCube successes/32 | StackCube successes/32 | Pooled native task successes /64 | Real privileged decision target reads |
|---|---:|---:|---:|---:|
| No-fault source pretrained PPO, context ONLY | 31 | 31 | 62 | 0 |
| Continuously privileged target-state oracle under two holds | 32 | 26 | 58 | continuous and **not zero-cost** |
| Optimistic assume delivery ACK | 6 | 0 | 6 | 0 |
| Strict all-target exact common action or refusal | 0 | 0 | 0 | 0 |
| Conservative common bounded action, no query | 9 | 2 | 11 | 0 |
| **Conservative bounded / ONE evidence-triggered target read** | **32** | **13** | **45** | **23 + 21 = 44** |
| **Conservative bounded until fixed t=4 trusted read** | **32** | **23** | **55** | **32 + 32 = 64** |

All source tasks physically stepped inside ManiSkill/PhysX, not policy predictions imputed from a source action log. The native injected intervention replaces the arm target command with a **zero/hold command at step indices 2 AND 3** while keeping the gripper. Only the abstract command acknowledgement is unknown. **It is not real packet loss.** Under this controller-native intervention, the three bounded belief strategies (zero-read, selective-read, scheduled t4 read) reach **four different commanded-target-memory hypotheses in every source reset state**; support for sixteen is a *source-code capacity*, not an empirically exercised 16-state belief.

## Pairwise exact matched-original-state statistics — fixed query beats selective on StackCube

- **Pooled 64-state matched comparison:** 42 both succeeded, 3 selective-only successes, **13 fixed-only successes**, 6 both failed. Exploratory conditional exact two-sided McNemar/sign p = **0.021270751953125** (16 discordances), i.e. direction strongly against a claim of selective superiority. This is not a paper-wide adjusted causal or robot-model population p-value.
- **PullCube 32:** selective 32/32 with 23 actual target reads; fixed 32/32 with 32 actual reads. Both task successes tie. Zero-read 9/32.
- **StackCube 32:** selective **13/32 with 21 reads**; fixed **23/32 with 32 reads**. Original paired outcomes: 10 both succeeded, 3 selective-only, **13 fixed-only**, 6 neither. Zero-read only 2/32.
- Saving 20/64 privileged reads (**31.25% fewer**) comes at **10/64 fewer task successes**. Selective and scheduled reading are genuine tradeoffs and neither should be advertised as pointwise dominant over the other.
- Avoid pooling the two tasks as if 64 distinct PPO/robot families had been sampled; there are only TWO third-party frozen PPO checkpoints on ONE Panda/controller family. Native seeds are distinct initial-state worlds, not independent model/algorithm treatments.

### Conditional setpoint verification, not whole-robot safety
- The raw original eight shard archives hold **1,530 actual physically DISPATCHED bounded-commanded-target post-step checks**; the audit verified every measured position max-component error was at most its specific certificate upper bound + `1e-4`, and every SO(3) geodesic target error was at most the specific bound + `1e-4`.
- **192 candidate commands were intentionally overwritten/held at fault steps 2–3.** Every one was kept in a *masked/NOT_EXECUTED* ledger; NOT a physically verified certificate.
- No collisions, contacts, forces, learned closed-loop stability, robot or human physical safety, bitwise provenance authentication or multi-robot transfer are certified.

## Scientific verdict and new research question
**Confirmed original systems negative result:** an action-authority certificate that permits execution until it fails is NOT sufficient to choose a good *query time* for downstream contact-rich manipulation. Even on new, preregistered seeds, the reactive timing hurt StackCube in exchange for fewer private target reads. This isolates an unresolved question with actual physical-simulator consequences: **when is early information worth paying for BEFORE the uncertainty geometry crosses the hard authorization threshold?**

The geometry uses existing minimax/finite-set techniques and by itself is not a novel theorem. Candidate originality would concern *the interface between privately stateful action memory, explicit query rights, irreversible task dynamics, and costed intervention timing.* A strong contender must compare with equally budgeted scheduled/stochastic or state-aware information policies, preserve an untouched test cohort, and exhibit better end-to-end task outcomes on multiple controller/task families. **No such newly improved method has yet passed that gate.**

## Graduate-admissions and third-party review boundary
This 64-state original closed-loop dataset and reusable runner/auditor support a credible independent study request, especially because unfavorable cases are preserved. A GitHub Actions run operated by the contributor is **not itself external scientific endorsement**. We invite a reviewer to re-execute the source-frozen native PhysX in an outside account using *new* unreported seeds, and to independently audit the original source/checkpoint SHA. This remains separate from formally merged and maintainer-approved Braindecode EEG model integrations.

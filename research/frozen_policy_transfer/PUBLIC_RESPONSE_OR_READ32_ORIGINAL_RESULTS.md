# Prospective dual-truth public-achieved-response or one-authority-read controller recovery

**32 out-of-discovery native ManiSkill PhysX task×execution-truth outcomes, all original failures preserved.** This is a single author's real CPU simulator experiment, NOT a true network packet-loss test, real-robot safety demonstration or externally reproduced method.

## Frozen *before* new source runner / trial outcomes

[Pre-outcome protocol commit `fa173507`](https://github.com/lindicaphxag-tech/ManiSkill/commit/fa17350711f6c2c7cffb4cfa2bb7f8289f3ee0c4), immutable protocol blob `bdcad7dff2fbe55ef7f1215f15adcda9d7372407`. Never altered the previously frozen empirical public-response segment-fit code (Git blob `064bb46831b61af73ad445bc836326837ec5468f`), with epsilon 0.006944262561376447m Pull / 0.00719087965534261m Stack. **Small** disjoint calibration sets Pull 140001–140004 and Stack 150001–150004 only; the previous negative 32 outcomes and earlier successful validation were NOT fitted or used for revising the method.

New actual physics task reset seeds PullCube 180101–180108 and StackCube 190101–190108 each tested under two native command truths: intended target executed at t=2 but no ACK, or physically **neutral/zero** arm target executed at t=2 with unknown ACK. 16 unique robot reset states ×2 truths = **32 task×truth conditions**, NOT 32 independent robot resets. All six physical controller arms take the exact same zero-arm/unchanged-gripper probe at t=3 and use the original frozen public PPO without retraining.

## Experimental mechanism and validity

The new **PUBLIC-FIT-OR-ONE-READ** arm inspects PUBLIC pre/post-probe **achieved EE XYZ**, plus both candidate previous commanded goal XYZ hypotheses reconstructed from the action history, without using any private target getter to classify execution. If exactly one of the two historical response segments lies within the separately frozen empirical task envelope, it infers that history and continues with **zero** privileged decision reads. If two histories are plausible OR neither fits, it refuses to guess and performs exactly **one explicitly counted** privileged controller-target getter call, resets the target memory estimator and resumes the same frozen policy.

This differs from a naive closest-target classifier which previously made **15/32 wrong confident ACK-history classifications** even though tasks could sometimes succeed. The empirical envelope is a **statistical training-data heuristic**, not an independently attested closed-loop response law, no chance guarantee of 0 future errors, and no certification of mechanical collision/force safety.

## Predeclared native PhysX task outcomes

| Physical controller arm | Genuine completed tasks | Privileged internal target reads |
|---|---:|---:|
| Original source PPO + common probe, no fault | 26/32 | 0 |
| Optimistic assumes delivered ACK | 23/32 | 0 |
| Pessimistic assumes native target hold | 20/32 | 0 |
| Public empirical inference ONLY, abstains if ambiguous | 19/32 | 0 |
| **NEW public evidence OR one privileged query** | **27/32** | **11** |
| Mandatory one privileged target read AFTER same probe | 27/32 | **32** |

**Exactly 21/32 public ACK-history decisions made without a privileged state getter, 0 wrong confident hidden-history labels among these 21 accepted decisions**. The other **11/32 explicitly consumed ONE privileged target readback** and did not misrepresent the source of its information. The real task-success outcomes match the mandatory-readback arm on **32/32 individual matched conditions** (paired exclusive wins: 0 in either direction). These task successes are not the same metric as correct ACK-history classification: both are separately audited.

**Evidence budget**: saved **21/32** privileged target readback calls while maintaining paired task-success parity in this exact 32-condition PhysX sample. This is NOT equivalent-information algorithmic superiority: the method uses a private read when the public empirical classifier abstains.

### All eight original source cohorts

| Task | Actual target truth | Fixed 4-state shard | Source | Optimistic | Public-only success | Hybrid success | Always-read success | Public classified | Hybrid private reads |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| pull_cube | Applied, ACK unknown | 0 | 3 | 3 | 2 | **3** | 3 | 2 | 2 |
| pull_cube | Applied, ACK unknown | 4 | 4 | 4 | 2 | **4** | 4 | 2 | 2 |
| pull_cube | Held, ACK unknown | 0 | 3 | 4 | 4 | **4** | 4 | 4 | 0 |
| pull_cube | Held, ACK unknown | 4 | 4 | 4 | 3 | **4** | 4 | 3 | 1 |
| stack_cube | Applied, ACK unknown | 0 | 3 | 2 | 0 | **2** | 2 | 1 | 3 |
| stack_cube | Applied, ACK unknown | 4 | 3 | 4 | 4 | **4** | 4 | 4 | 0 |
| stack_cube | Held, ACK unknown | 0 | 3 | 1 | 2 | **3** | 3 | 3 | 1 |
| stack_cube | Held, ACK unknown | 4 | 3 | 1 | 2 | **3** | 3 | 2 | 2 |

### Every original task × seed × truth, including refused or failed trials

| Task | Seed | Actual command truth | Public response label | Wrong confident ACK history? | Explicit private goal read | Optimistic native success | Public-only native success | Hybrid native success | Mandatory native success |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|
| Pull | 180101 | applied | applied | 0 | 0 | 1 | 1 | **1** | 1 |
| Pull | 180102 | applied | *reject inference* | — | 1 | 0 | 0 | **0** | 0 |
| Pull | 180103 | applied | *reject inference* | — | 1 | 1 | 0 | **1** | 1 |
| Pull | 180104 | applied | applied | 0 | 0 | 1 | 1 | **1** | 1 |
| Pull | 180105 | applied | applied | 0 | 0 | 1 | 1 | **1** | 1 |
| Pull | 180106 | applied | *reject inference* | — | 1 | 1 | 0 | **1** | 1 |
| Pull | 180107 | applied | applied | 0 | 0 | 1 | 1 | **1** | 1 |
| Pull | 180108 | applied | *reject inference* | — | 1 | 1 | 0 | **1** | 1 |
| Pull | 180101 | held | held | 0 | 0 | 1 | 1 | **1** | 1 |
| Pull | 180102 | held | held | 0 | 0 | 1 | 1 | **1** | 1 |
| Pull | 180103 | held | held | 0 | 0 | 1 | 1 | **1** | 1 |
| Pull | 180104 | held | held | 0 | 0 | 1 | 1 | **1** | 1 |
| Pull | 180105 | held | held | 0 | 0 | 1 | 1 | **1** | 1 |
| Pull | 180106 | held | held | 0 | 0 | 1 | 1 | **1** | 1 |
| Pull | 180107 | held | *reject inference* | — | 1 | 1 | 0 | **1** | 1 |
| Pull | 180108 | held | held | 0 | 0 | 1 | 1 | **1** | 1 |
| Stack | 190101 | applied | *reject inference* | — | 1 | 1 | 0 | **1** | 1 |
| Stack | 190102 | applied | *reject inference* | — | 1 | 1 | 0 | **1** | 1 |
| Stack | 190103 | applied | applied | 0 | 0 | 0 | 0 | **0** | 0 |
| Stack | 190104 | applied | *reject inference* | — | 1 | 0 | 0 | **0** | 0 |
| Stack | 190105 | applied | applied | 0 | 0 | 1 | 1 | **1** | 1 |
| Stack | 190106 | applied | applied | 0 | 0 | 1 | 1 | **1** | 1 |
| Stack | 190107 | applied | applied | 0 | 0 | 1 | 1 | **1** | 1 |
| Stack | 190108 | applied | applied | 0 | 0 | 1 | 1 | **1** | 1 |
| Stack | 190101 | held | held | 0 | 0 | 1 | 1 | **1** | 1 |
| Stack | 190102 | held | *reject inference* | — | 1 | 0 | 0 | **1** | 1 |
| Stack | 190103 | held | held | 0 | 0 | 0 | 1 | **1** | 1 |
| Stack | 190104 | held | held | 0 | 0 | 0 | 0 | **0** | 0 |
| Stack | 190105 | held | *reject inference* | — | 1 | 0 | 0 | **0** | 0 |
| Stack | 190106 | held | held | 0 | 0 | 0 | 1 | **1** | 1 |
| Stack | 190107 | held | *reject inference* | — | 1 | 0 | 0 | **1** | 1 |
| Stack | 190108 | held | held | 0 | 0 | 1 | 1 | **1** | 1 |

## Native-source provenance and replication instructions

Original eight green ManiSkill PhysX original shard jobs [run 37834088246](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37834088246), exact original running source `f1423b307ed37c2e6413868d3213412424c6dc97`, frozen externally released third-party PPO SHA256 Pull `74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7`, Stack `e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c`, released revision `6bdeb28810330ab5425ccd629bb561c58a56ff85`. Each of the eight original artifacts includes four separate seeded trial records, with SIX matched native controller worlds in each trial, the full original console log and package-environment freeze:

- pull_cube, applied_no_ack, fixed start-offset 0: [original physical simulator job 113506578897](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37834088246/job/113506578897) · [exact source original ZIP artifact 11575141229](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37834088246/artifacts/11575141229)
- pull_cube, applied_no_ack, fixed start-offset 4: [original physical simulator job 113506579633](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37834088246/job/113506579633) · [exact source original ZIP artifact 11575580533](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37834088246/artifacts/11575580533)
- pull_cube, neutral_arm_delta_no_ack, fixed start-offset 0: [original physical simulator job 113506579196](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37834088246/job/113506579196) · [exact source original ZIP artifact 11575505568](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37834088246/artifacts/11575505568)
- pull_cube, neutral_arm_delta_no_ack, fixed start-offset 4: [original physical simulator job 113506579303](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37834088246/job/113506579303) · [exact source original ZIP artifact 11574119834](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37834088246/artifacts/11574119834)
- stack_cube, applied_no_ack, fixed start-offset 0: [original physical simulator job 113506579250](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37834088246/job/113506579250) · [exact source original ZIP artifact 11574817153](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37834088246/artifacts/11574817153)
- stack_cube, applied_no_ack, fixed start-offset 4: [original physical simulator job 113506579223](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37834088246/job/113506579223) · [exact source original ZIP artifact 11575835044](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37834088246/artifacts/11575835044)
- stack_cube, neutral_arm_delta_no_ack, fixed start-offset 0: [original physical simulator job 113506579224](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37834088246/job/113506579224) · [exact source original ZIP artifact 11574911831](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37834088246/artifacts/11574911831)
- stack_cube, neutral_arm_delta_no_ack, fixed start-offset 4: [original physical simulator job 113506579255](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37834088246/job/113506579255) · [exact source original ZIP artifact 11575725221](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37834088246/artifacts/11575725221)

[**Immutable native evidence audit**](../audit_public_response_or_read32.py) ensures full denominator, distinct seed/truth identities, original PPO source checkpoints, exact physical fault/probe reach, private readback permissions, incorrect ACK-history labels even when tasks succeed, per-task official success and native projection exactness. [Trusted-only permanent source archive mechanism](../../.github/workflows/archive-public-or-read-new32-original.yml) checks eight original artifact ZIP SHA-256 digests before writing byte-identical raw JSONs to the repository main branch. Do not cite the permanent archive as finished until that trusted-main job succeeds.

## What this does NOT claim

**No independently attested dynamics.** A tiny empirical error envelope fit on 4 previous state seeds per task is subject to shift and finite-sample error. **No proof of zero false confident state authorization**, even though 0/21 occurred here. **No true network communication failure.** Faults were official native PhysX target holds vs actual physical execution with unknown ACK. **No collision or contact safety result.** Decision confidence here is about last commanded target states, not achieved joint/EE trajectory force limits. **No cross-robot policy result** or second independent controller. **No official upstream or academic external adoption yet**. These are original contributor experiments on the one Panda target controller.

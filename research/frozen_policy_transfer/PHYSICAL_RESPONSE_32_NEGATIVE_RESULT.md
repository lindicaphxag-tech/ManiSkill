# Preregistered 32-state genuine-PhysX negative result: one-step achieved-pose ACK classifier

**Complete experiment, not a successful method claim.** Original run and full source audit: [GitHub Actions 37829520809](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37829520809), **10/10 success**. All eight actual native PhysX task×fault×chunk jobs completed, and an independent ninth job reaggregated **all 32 source task-condition rows**. The protocol was frozen [before code/results](https://github.com/lindicaphxag-tech/ManiSkill/commit/f237fadb70895bc94889f3ff44cb6c41d296b323), original Git blob `de2109c36cbb767ee1a4af11c981f1256ed60eac`; the unchanged *repaired* runner Git blob is `06a6cc465c4f0cd896ddc6e761f291c1e8287417`.

## Direct per-condition original source results

Each group has eight fixed real PhysX states, **same task seed** for all five controller arms. All reported numbers below are official once-per-episode task successes, not safe trajectories or correctly identified controller histories.

| Frozen PPO task | Actual ACK-unknown arm truth | Native source, no fault | Blind assume applied, equal probe | Blind assume neutral, equal probe | Achieved-pose heuristic, equal probe | One privileged target read, equal probe | Confident wrong ACK-history labels |
|---|---|---:|---:|---:|---:|---:|---:|
| PullCube 140001–140008 | Applied, ACK missing | 7/8 | 7/8 | 4/8 | **4/8** | 7/8 | **8/8** |
| PullCube 140001–140008 | Zero arm delta delivered, ACK missing | 7/8 | 8/8 | 8/8 | **8/8** | 8/8 | 0/8 |
| StackCube 150001–150008 | Applied, ACK missing | 7/8 | 6/8 | 0/8 | **1/8** | 6/8 | **7/8** |
| StackCube 150001–150008 | Zero arm delta delivered, ACK missing | 7/8 | 0/8 | 6/8 | **6/8** | 7/8 | 0/8 |
| **Total across 32 task×truth conditions** | **32** | **28/32** | **21/32** | **18/32** | **19/32** | **28/32** | **15/32** |

**Critical mistake:** The achieved-XYZ-nearest-target heuristic confidently classified all **32/32** trials and made **15/32 (46.875%) wrong history authorizations**. It was wrong **15/16** times the command actually executed, but correctly identified **16/16** held-command conditions. Overall ACK-history classification accuracy is **17/32 (53.125%)**, close to the majority held-guess strategy under this balanced design. Task success was not a proxy for correct controller-state identification: on four new PullCube applied states, the heuristic recovered 3/4 tasks yet confidently identified the wrong history on all four.

**Inference:** a single no-op native target-delta probe does **not** generally reveal the hidden last-commanded target by nearest-distance of achieved pose. A gripper command is repeated during the probe as specified; this is not real packet loss, and the arm target may track with lag, gain mismatch or contact-related disturbances. The heuristic assumes a relationship between achieved pose and commanded target that is not proven. It should be **falsified/rejected as a method**, not tuned on these test seeds after seeing the outcome.

## Equal-time, unequal-state information ladder

All four destination controller arms receive the same one-step probe/pause budget. Blind optimistic, blind pessimistic and the achieved-pose classifier have **zero private target getter during decisions**. The readback arm receives **one privileged target-memory read after probe**, so its 28/32 is **not** a fair equal-information advantage; it is a useful costed target-state ceiling. The source-policy row is fault-free context, not an equal-fault benchmark.

The naive classifier has no abstention once its arbitrary 2 mm nearest-distance margin is exceeded; all 32 classified. More aggressive refusal without an externally validated response envelope is scientifically justified, not a performance improvement claim. A separate **conditional standard set-membership** [implementation and mathematical note](ACK_RESPONSE_SET_MEMBERSHIP_CERTIFICATE.md) now exists, but has **no independently calibrated alpha/error envelope and no actual PhysX success result**; its synthetic unit tests do not repair this negative result.

## Prespecified integrity checks

- Both PullCube and StackCube PPOs are the original released [ActionShift checkpoint artifacts](https://huggingface.co/kattri15/actionshift-baselines), SHA256-pinned, frozen, never retrained.
- Both hidden truths were simulated by a genuine SAPIEN/ManiSkill step: requested native arm action applied, or zero native arm action substituted, with retained gripper action. No packet-loss service or real robot hardware is tested.
- **32/32** source task-condition rows reached the injected fault; **32/32** reached the one-step physical probe. Eight original 4-state JSONs were analyzed, not reconstructed from prose summaries.
- All inexact bounded projections are labeled `NOT_EXACT`. A wrong confident history guess counts as an error even if the official task-success flag is true. All episode failures remain in denominators.
- [Original independent source auditor](../audit_physical_response_32.py) matches all eight source-JSON success counts, wrong-authorization flags, private target-read ledgers, predeclared seeds, simulator/model provenance, fault/probe exposures and per-episode decision outputs. [Adversarial tests](../../tests/test_physical_response_32.py) include wrong-label, missing-seed, leakage and false-exact regression witnesses.
- The first fixed-protocol run failed **before any interpretable task outcome** due to a pending-ACK observer snapshot ordering bug. The [implementation-only correction](https://github.com/lindicaphxag-tech/ManiSkill/commit/1200105601326dce541cebdd037770472300b0b8) moved a pre-action pose snapshot before `prepare()` without changing preregistered tasks, seeds, threshold or intervention. This repaired exact runner produced the full 10/10 successful original CI.

## What would count as stronger next research?

1. Freeze a separately **calibrated physics/sensor envelope** on disjoint states; in future task trials, authorize a history only if its predicted physical-response set is uniquely consistent with public observation. Report **coverage, wrong authorization, physical model falsification, task success and query cost separately**. The new certificate is a known set-membership argument, not invented SE(3) theory.
2. Compare learned response-history estimators and existing [ActionShift belief/probe methods](https://github.com/Archerkattri/actionshift) under **equal available information and equal time/probe budgets**, not against handicapped blind guessing.
3. Move beyond the one Panda controller family and simulated one-step zero-target fault, using independently maintained robot implementations and genuine delayed/dropped/reordered actuator commands. The currently available Fetch/XArm joint-controller tests are contracts, not cross-robot frozen-policy task transfers.
4. Obtain a reproducible, genuinely **external** research/lab run with their own novel preregistered seeds and complete failures, not a self-fork PR count.

**No external scientific acceptance, real-robot safety, guaranteed identified controller state or method superiority is claimed here.** The validated outcome of this study is a failure mode and a fully auditable negative result.

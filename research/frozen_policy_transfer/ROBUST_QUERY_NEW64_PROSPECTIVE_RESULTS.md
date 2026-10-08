# 64 new-seed prospective validation of unchanged bounded-or-query frozen PPO

**Result: 8/8 real ManiSkill PhysX CPU CI jobs succeeded, 64/64 predeclared unique reset state outcomes retained, full original model/runner/SE3-certifier SHA frozen.** Original experiment remains contributor-operated, NOT an independent third-party replication or physical robot safety guarantee.

## Method freeze (before new seeds were executed)

- **Original discovery method**: [four green-jobs run 37826881229](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37826881229), exact successful method commit `db4fe4dd9d09aaff67c5dcf12213ad737162282d`, original experimental runner Git blob `1dc653cdc44e422c8340475ad00f828b3a41eb4f`, robust bounded SE(3) certifier Git blob `bb5fd155b7291fb127f94138fca321201c8271c3`.
- **New validation preregistered BEFORE seed runner**: [commit 9ebb39e](https://github.com/lindicaphxag-tech/ManiSkill/commit/9ebb39ef01c06869c60f923cdba5d1e4e5626b1d), protocol Git blob `70a16b787acb4380f9c7109c741a996453be1319`, unchanged budgets position infinity norm **0.05m**, geodesic angular distance **0.05rad**, max **one** privileged controller-target readback, and target arm-hold step index 2.
- **Genuinely NEW 64 independent reset states** not included in previous 16-state discovery: PullCube 142001–142032 and StackCube 152001–152032. Eight CI jobs, 8 distinct seeds each. This is a state-disjoint *same-lab/same-simulator* validation, not external-lab independent replication.
- Original public third-party frozen PPO checkpoints, no retraining: Pull SHA256 `74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7`; Stack SHA256 `e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c`; published HF revision `6bdeb28810330ab5425ccd629bb561c58a56ff85`.
- [**Eight original PhysX CI jobs and all original stdout**](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37828426195), source tested head `d91081d30b3d56824e30dd9b3673b4f6db3b5f96` (same SHA-checked source method as original run).
- A simulated arm command is physically replaced by a neutral/hold target native action at step 2; gripper still actuates and PhysX advances. **No actual real-world lost/reordered network packets; no robot hardware collision/force safety measurements.**

## Full-denominator native task outcomes

| Control | Task success (64 truly NEW state seeds) | Total PRIVILEGED target readback queries |
|---|---:|---:|
| Original source PPO controller without fault (context only) | 60/64 | 0 |
| Continuously privileged actual target controller under fault (oracle) | 58/64 | Continuous privileged access (not counted as 0) |
| Optimistic assume ACK delivered, but actual arm target held | 42/64 | 0 |
| Strict exact-common-action refusal | 0/64 | 0 |
| Bounded two-target action, **never** read back | 47/64 | 0 |
| **Bounded two-target action, query iff cannot certify** | **60/64** | **15** |
| Mandatory **one privileged target readback on every fault** | 57/64 | **64** |

**Decision readback reduction**: `76.5625%` fewer compared to the always-read-once method; this measures ONLY controller-target *decision readback calls*, not GPU energy, task time or communication bandwidth. **Paired task-success contrast** adaptive vs always: 5 adaptive-only wins, 2 mandatory-only wins. Unlike a general superiority claim, this small paired difference requires statistical uncertainty; do not call it significant.

Against exactly **zero-readback** matched information, the adaptive strategy uses more information when uncertain, so success gains do NOT establish equal-information algorithmic superiority. Its contribution is a **resource/decision tradeoff** backed by a verified setpoint error certificate conditional on a known two-hypothesis memory model.

## Per-task results

| Task | Unique states | No-fault source | Optimistic (0 reads) | Bounded no reads | **Selective** | Mandatory | Selective trusted reads |
|---|---:|---:|---:|---:|---:|---:|---:|
| PullCube | 32 | 32 | 31 | 30 | **32** | 32 | 2 |
| StackCube | 32 | 28 | 11 | 17 | **28** | 25 | 13 |

**Per-task 8-seed original chunks**

| Task | Chunk | Fixed seed range | Source | Optimistic | Bounded no read | Selective | Mandatory | Selective reads |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| pull_cube | 0 | 142001–142008 | 8 | 8 | 7 | **8** | 8 | 1 |
| pull_cube | 1 | 142009–142016 | 8 | 7 | 8 | **8** | 8 | 0 |
| pull_cube | 2 | 142017–142024 | 8 | 8 | 7 | **8** | 8 | 1 |
| pull_cube | 3 | 142025–142032 | 8 | 8 | 8 | **8** | 8 | 0 |
| stack_cube | 0 | 152001–152008 | 7 | 1 | 5 | **6** | 6 | 3 |
| stack_cube | 1 | 152009–152016 | 7 | 4 | 3 | **6** | 7 | 3 |
| stack_cube | 2 | 152017–152024 | 7 | 3 | 5 | **8** | 7 | 3 |
| stack_cube | 3 | 152025–152032 | 7 | 3 | 4 | **8** | 5 | 4 |

**Per-state original CI-output transcription:** 64 lines, including failed source and target trials.

| Task | Seed | Source | Optimistic | Bounded no-read | Selective | Mandatory | Query count | Certified bounded actions | Selective refusal if any |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Pull | 142001 | 1 | 1 | 1 | 1 | 1 | 0 | 4 | — |
| Pull | 142002 | 1 | 1 | 1 | 1 | 1 | 0 | 4 | — |
| Pull | 142003 | 1 | 1 | 1 | 1 | 1 | 0 | 5 | — |
| Pull | 142004 | 1 | 1 | 1 | 1 | 1 | 0 | 5 | — |
| Pull | 142005 | 1 | 1 | 1 | 1 | 1 | 0 | 4 | — |
| Pull | 142006 | 1 | 1 | 1 | 1 | 1 | 0 | 5 | — |
| Pull | 142007 | 1 | 1 | 1 | 1 | 1 | 0 | 5 | — |
| Pull | 142008 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | — |
| Pull | 142009 | 1 | 1 | 1 | 1 | 1 | 0 | 4 | — |
| Pull | 142010 | 1 | 1 | 1 | 1 | 1 | 0 | 4 | — |
| Pull | 142011 | 1 | 1 | 1 | 1 | 1 | 0 | 5 | — |
| Pull | 142012 | 1 | 1 | 1 | 1 | 1 | 0 | 4 | — |
| Pull | 142013 | 1 | 1 | 1 | 1 | 1 | 0 | 3 | — |
| Pull | 142014 | 1 | 1 | 1 | 1 | 1 | 0 | 4 | — |
| Pull | 142015 | 1 | 1 | 1 | 1 | 1 | 0 | 5 | — |
| Pull | 142016 | 1 | 0 | 1 | 1 | 1 | 0 | 5 | — |
| Pull | 142017 | 1 | 1 | 0 | 1 | 1 | 1 | 4 | — |
| Pull | 142018 | 1 | 1 | 1 | 1 | 1 | 0 | 5 | — |
| Pull | 142019 | 1 | 1 | 1 | 1 | 1 | 0 | 4 | — |
| Pull | 142020 | 1 | 1 | 1 | 1 | 1 | 0 | 5 | — |
| Pull | 142021 | 1 | 1 | 1 | 1 | 1 | 0 | 5 | — |
| Pull | 142022 | 1 | 1 | 1 | 1 | 1 | 0 | 5 | — |
| Pull | 142023 | 1 | 1 | 1 | 1 | 1 | 0 | 5 | — |
| Pull | 142024 | 1 | 1 | 1 | 1 | 1 | 0 | 4 | — |
| Pull | 142025 | 1 | 1 | 1 | 1 | 1 | 0 | 5 | — |
| Pull | 142026 | 1 | 1 | 1 | 1 | 1 | 0 | 4 | — |
| Pull | 142027 | 1 | 1 | 1 | 1 | 1 | 0 | 5 | — |
| Pull | 142028 | 1 | 1 | 1 | 1 | 1 | 0 | 5 | — |
| Pull | 142029 | 1 | 1 | 1 | 1 | 1 | 0 | 4 | — |
| Pull | 142030 | 1 | 1 | 1 | 1 | 1 | 0 | 4 | — |
| Pull | 142031 | 1 | 1 | 1 | 1 | 1 | 0 | 4 | — |
| Pull | 142032 | 1 | 1 | 1 | 1 | 1 | 0 | 4 | — |
| Stack | 152001 | 1 | 0 | 1 | 1 | 1 | 0 | 9 | — |
| Stack | 152002 | 1 | 0 | 1 | 1 | 1 | 0 | 10 | — |
| Stack | 152003 | 1 | 0 | 1 | 1 | 1 | 0 | 11 | — |
| Stack | 152004 | 1 | 0 | 0 | 0 | 0 | 1 | 16 | — |
| Stack | 152005 | 1 | 0 | 0 | 0 | 1 | 1 | 17 | — |
| Stack | 152006 | 1 | 1 | 0 | 1 | 1 | 1 | 5 | — |
| Stack | 152007 | 1 | 0 | 1 | 1 | 1 | 0 | 13 | — |
| Stack | 152008 | 0 | 0 | 1 | 1 | 0 | 0 | 14 | — |
| Stack | 152009 | 0 | 0 | 0 | 0 | 0 | 0 | 47 | — |
| Stack | 152010 | 1 | 1 | 0 | 1 | 1 | 1 | 2 | — |
| Stack | 152011 | 1 | 0 | 1 | 1 | 1 | 0 | 13 | — |
| Stack | 152012 | 1 | 0 | 1 | 1 | 1 | 0 | 14 | — |
| Stack | 152013 | 1 | 1 | 1 | 1 | 1 | 0 | 13 | — |
| Stack | 152014 | 1 | 1 | 0 | 1 | 1 | 1 | 3 | — |
| Stack | 152015 | 1 | 0 | 0 | 0 | 1 | 0 | 47 | — |
| Stack | 152016 | 1 | 1 | 0 | 1 | 1 | 1 | 5 | — |
| Stack | 152017 | 1 | 0 | 1 | 1 | 1 | 0 | 8 | — |
| Stack | 152018 | 1 | 1 | 0 | 1 | 1 | 1 | 6 | — |
| Stack | 152019 | 1 | 0 | 1 | 1 | 1 | 0 | 14 | — |
| Stack | 152020 | 1 | 1 | 0 | 1 | 1 | 1 | 2 | — |
| Stack | 152021 | 0 | 0 | 1 | 1 | 0 | 0 | 11 | — |
| Stack | 152022 | 1 | 0 | 1 | 1 | 1 | 0 | 15 | — |
| Stack | 152023 | 1 | 1 | 0 | 1 | 1 | 1 | 3 | — |
| Stack | 152024 | 1 | 0 | 1 | 1 | 1 | 0 | 11 | — |
| Stack | 152025 | 1 | 0 | 1 | 1 | 1 | 0 | 16 | — |
| Stack | 152026 | 1 | 0 | 1 | 1 | 0 | 0 | 16 | — |
| Stack | 152027 | 1 | 0 | 1 | 1 | 1 | 0 | 10 | — |
| Stack | 152028 | 1 | 1 | 0 | 1 | 1 | 1 | 2 | — |
| Stack | 152029 | 1 | 1 | 1 | 1 | 1 | 0 | 14 | — |
| Stack | 152030 | 0 | 0 | 0 | 1 | 0 | 1 | 5 | — |
| Stack | 152031 | 1 | 1 | 0 | 1 | 1 | 1 | 6 | — |
| Stack | 152032 | 1 | 0 | 0 | 1 | 0 | 1 | 21 | — |

## Convergence and error accounting

All seven target arms were PhysX stepped under exactly the same seeded reset and intended task policy. Native `info['success']` is recorded and **all** fault events and failure/refusal rows kept. For selective/readback cases, controller memory is accessed only by an explicitly accounted privileged decision read, or as **post-action audit only** for setpoint proof checks. `NOT_EXACT` bounded native action projections are disclosed in original source rows; no exact source policy equivalence or physical robot safety is claimed.

This study includes **538** audit-only native bounded-action post-dispatch setpoint checks recorded for the adaptive arm. The certificate is about **previous controller commanded-target state consistency and commanded-target error**, not achieved trajectory, joint torque, collision clearance, force/contact, or network fault resilience.

## Original sources and independent reproduction

Original run: [37828426195](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37828426195) · [Preregistered method-locked PR #80](https://github.com/lindicaphxag-tech/ManiSkill/pull/80) · [One-click external fork + new-seed PhysX guide](INDEPENDENT_REPLICATION_QUICKSTART.md).

The accompanying trusted-main archive workflow, once successfully merged and run, makes **byte-identical original JSONs with SHA-256 checksums permanently accessible**. Until that job actually completes, use the original CI artifact links; do not imply that an archive already exists.

**Research claim limit**: One Panda controller family, two released frozen PPO policies, simulated target-hold instead of true packet loss, two-task source competence, original author-run; no official upstream CST merge, formal statistical proof of superior task success, independent laboratory results, hardware safety, or guaranteed L8/L9/RA-L acceptance.

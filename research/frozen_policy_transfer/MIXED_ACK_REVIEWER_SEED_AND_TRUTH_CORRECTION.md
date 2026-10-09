# Mixed-ACK frozen PPO falsifier: reviewer-first corrections to holdout identity and fault truth

**Status: 2026-10-09.** This note does not alter the original preregistration, runner, source rows, original auditor, or empirical response thresholds. **Source-authentic** does not automatically mean **fully seed-disjoint** or **independently reproduced**.

## Executed source results, not a new run

The [first complete original real native PhysX source and independent auditor](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37915263314) records 64 reset IDs, 9 separately stepped virtual controllers per reset (576 PhysX worlds), and two actual unknown-ACK fault time indices. At **t2** precisely 32 applied and 32 held actions were physically dispatched; at **t3** all 64 were held. It is **not** a joint four-truth 2×2 experiment, real network packet loss, real robot-hardware safety, or a new trained VLA.

| Fully original physically executed method | Official success | True decision-private target reads |
|---|---:|---:|
| Public complete-history XYZ witness → fallback read | **58/64** | **31** |
| Task-labelled strong selectable/fixed query | **58/64** | **58** |
| Every task t4 fixed query | **59/64** | **64** |
| Physical zero-read always-assume-held alternative | **43/64** | **0** |
| Earlier generic selective query | **56/64** | **48** |
| Geometry-only no-query bounded/refuse | **11/64** | **0** |

New relative to task-aware comparator: 57 both succeed, 5 neither, 1 public-only success, 1 comparator-only success. The public path committed **33/64 complete target-history identifications, zero observed confident wrong labels**, with 31 logged authoritative target reads. Observed difference **27/58=46.6%** in private read count under this fault distribution **does not establish statistical noninferiority or population zero-wrong reliability**.

Stratified exact original data:

| Task / actual t2 command | n | Public success | Strong success | Public reads | Strong reads | Public unique labels |
|---|---:|---:|---:|---:|---:|---:|
| PullCube t2 applied | 16 | 16 | 15 | 4 | 12 | 12 |
| PullCube t2 held | 16 | 16 | 16 | 10 | 14 | 6 |
| StackCube t2 applied | 16 | 15 | 15 | 9 | 16 | 7 |
| StackCube t2 held | 16 | 11 | 12 | 8 | 16 | 8 |

## Material seed-identity contamination, disclosed and not retroactively repaired

The earlier distinct [full-pose survivor preregistration](https://github.com/lindicaphxag-tech/ManiSkill/commit/1f68f3d788525e555b9170437161554a20138cde) was committed **2026-10-09 09:47:59 UTC** with PullCube reset seeds 860001–860016 and StackCube 870001–870016. This study's mixed-ACK [frozen pre-outcome protocol commit](https://github.com/lindicaphxag-tech/ManiSkill/commit/134b6a3d0b19d0622bea1757a83be5438e687f8e) was committed **2026-10-09 10:01:09 UTC** and uses 860001–860032 / 870001–870032.

Thus **32/64 task/reset identities overlap** a previously preregistered, physically different study. The mixed-ACK physical interventions are genuinely different, so the original source runs and audit are real; however a claim that all 64 reset identities were untouched by earlier research is incorrect. These two studies cannot be pooled as two independently selected reset-level prospective replications, and the mixed study must not be advertised as a purely independent prospective holdout cohort. Preserve the raw negative and positive rows, never silently relabel, exclude or tune those first 16 IDs/task.

## Stronger, genuinely disjoint prospective replication

The [new preregistration committed **before** its experimental runner](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/replicate-mixedack-disjoint64-20261009/research/DISJOINT_MIXED_T2_PPO64_PREOUTCOME_V1.json) uses PullCube 1180001–1180032 and StackCube 1190001–1190032, **without changing the original physical mixed-ACK runner Git Blob**. Its [new native PhysX source/action/audit workflow](https://github.com/lindicaphxag-tech/ManiSkill/actions/workflows/disjoint-mixed-ack-ppo64-native-physx.yml) is an author-operated new-cohort falsifier: original outcomes, whatever they are, must be compared with their own matched task-aware comparator. A running or successfully started workflow is *not* efficacy evidence; no outcome is claimed until all eight physical shards and the independent complete audit pass.

The second ACK remains **always held** in this new replication. A future full 2×2 physical-truth experiment must separately preregister a genuinely deliverable nonzero second action and correct the t3-neutral-probe assumption, otherwise even a successful "t3 applied" flag would not constitute physically different execution truth.

## External-researcher acceptance boundary

A GitHub fork author merging their own research PR is not an upstream merge or independent external validation. The actionable review unit is the reproducible source and original complete matrix: **specify a contrary reset/fault distribution, match public-sensing/readback/actuation budgets, rerun unchanged released PPO, preserve every wrong confident history and both official task outcomes**. A reviewer endorsement requires an actual outside person's independent run or external technical response, not simply more owner-operated CI.

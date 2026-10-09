# First real two-robot fixed-anchor SE(3) repair intervention — fully sourced findings

**10 October 2026 · 128 actual author-operated ManiSkill CPU PhysX worlds.**

## What was frozen BEFORE outcomes

[Protocol and exact registry](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/repair-effect-observability-certificate-20261010/research/PHYSX_ANCHOR_REPAIR_FIRST128_PREOUTCOME_V1.json): Panda seeds 720001–720008 and xArm6 Robotiq 730001–730008, each with both actual native physical t2 ACK truths (applied/held), two known-delivered t3 actions (zero or +0.35 normalized z rotation) and both independently physically stepped t4 repair arms. That is **16 independent robot/reset seeds, 64 matched prefix pairs, 128 correlated physical worlds**.

Both repair arms were given the exact true ACK history (oracle) to isolate repair-transition semantics. Desired goal was the immutable full-SE3 controller target after t1, NOT the previous moving held target. The transition-unaware ablation ignores t3 while computing inverse; action-aware analytic compensation includes it. Both use the identical initial pose/actions/truth/probe, and private controller getters are solely audit measurements, never action inputs. No learned policy or online ACK inference was tested.

## All actual source-audited outcomes

| Robot | Zero/ignore transition | Zero/compensate transition | Rotational probe/ignore transition | Rotational probe/compensate |
|---|---:|---:|---:|---:|
| Panda (16 correlated conditions per cell) | 16/16 | 16/16 | **0/16** | **16/16** |
| xArm6 (16 correlated conditions per cell) | 16/16 | 16/16 | **0/16** | **16/16** |

Max observed t4 commanded-target SO(3) residual for nonzero rotation: Panda ablation **0.0350000121 rad**, action-aware **1.07e-8 rad**; xArm6 ablation **0.0350000091 rad**, action-aware **1.07e-8 rad**. In **32/32** robot/reset/ACK truth groups the known nonzero rotation produced >0.001 rad actual commanded target drift; all **64/64** paired repair arms had matching original pre-repair public prefixes.

These outcomes establish a physical **failure case for omitting known probe transitions in a fixed-target SE3 repair**, NOT an advantage over a competent dynamics-aware strong baseline. The simple analytic transition-aware inverse is the correct baseline; the full finite belief planner was not physically executed. The result is not manipulation-task success, no model completeness certificate, no contact safety, no VLA transfer, no external replication.

## Failure history and authentic first-run preservation

1. [FIRST physical run #37993147659](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37993147659), original source commit da75e908038f6315785ffd840a0938053d3b8ab8: prereg PASS and all FOUR true simulator shards PASS; **overall run failed** because the source-only aggregation environment omitted gymnasium. This first-run failure is not hidden or relabeled as green.
2. [Separate recovery and permanent first-source re-audit #37993568117](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37993568117): validated the first run ID, source hash, run attempt and five successful original precursor jobs. Downloaded the four ORIGINAL physical shard artifacts, installed the missing audit import dependency and recomputed the full 128-condition factorial WITHOUT rerunning physics. Overall success.
3. [Permanent first-run archive and SHA256 manifest](https://github.com/lindicaphxag-tech/ManiSkill/tree/evidence/anchor-first128-first-physics-20261010/research/frozen_policy_transfer/evidence/anchor_first128_first_physics_20261010): 19 byte-checked original files plus manifest (original source JSON, all console logs, environment and revision IDs, independently rerun author-source audit).

**Reviewer limitation:** original per-world JSON stores final commanded-target SE3 residuals computed during original PhysX, but does NOT independently export the final raw commanded target quaternion. The archive authenticates those source-calculated residuals; independent raw-pose distance recomputation would need a new experiment with both raw before/after quaternions recorded.

## Comparison with legitimately established contributions

[AAAI 2018 Safe RL via Shielding](https://ojs.aaai.org/index.php/AAAI/article/view/11797) already studies formally synthesized safety shields. [AAAI 2018 Safe RL via Formal Methods](https://ojs.aaai.org/index.php/AAAI/article/view/12107) explicitly cautions that assurance depends on the physical system matching its verified model. [AAAI 2023 Safe Policy Improvement for POMDPs](https://ojs.aaai.org/index.php/AAAI/article/view/26763) shows that finite partial-observation policy theory is mature. Here the added value is a physically executed controller-target contract counterexample with full source provenance, not a generally novel POMDP solver.

Additional L8/L9-style outcome gates: independently frozen real controller transition/getter semantics; fair known-state-aware analytic baseline; calibrated and unseen public-only ACK inference; actual learned policy manipulation tasks with measured costs and contacts; a non-author fresh-seed replication; and genuine external adoption. None is established by this single oracle-truth ablation.

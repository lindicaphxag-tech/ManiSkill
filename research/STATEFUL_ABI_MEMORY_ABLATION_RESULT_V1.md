# Frozen PPO stateful-memory causal ablation — real PhysX result

**Status:** Precommitted single-task mechanism gate PASSED. Contributor-executed official ManiSkill PhysX episodes, not independent replication or physical robot safety.

## Frozen source identity

- Protocol committed **before** editing the original controller runner: https://github.com/lindicaphxag-tech/ManiSkill/commit/b27cf073b4183f7c9e8d9de116d94f646cb2863d
- Protocol Git blob SHA-1: bec1bad6d17c0c0782958fd0be540c24fb35b7f2
- Official full 4x8-seed source and aggregate CI: https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37814189680
- Public external third-party PPO model weights SHA-256: 3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8
- **Exactly 32** original independent PickCube task states 22001–22032; all five controller arms measured at genuine closed-loop success flags, no dropped or replaced seed.

## Actual unselected prospective results

| Control arm (all use same frozen PPO) | Real task successes |
|---|---:|
| Original achieved-relative source | 31/32 |
| Naive direct target-copy | 4/32 |
| Memory-aware exact-only conversion, reject unrepresentable | 9/32 |
| **Actual target-memory conversion + bounded projection** | **31/32** |
| **Memory-blind otherwise-identical conversion + bounded projection** | **4/32** |

**Paired:** 27 live-memory-only successes, zero state-blind-only successes, **net +27/32**. The registered mechanism gate was +6/32, after source competence ≥24/32; both gates passed without retuning.

Strict exact-only controller refused in **23** episodes; memory-aware approximate controller made **27 non-exact bounded projection steps**. Success is not proof of exact semantics or safe execution. The state-blind controller applies the same source-action decoding, XYZ-Euler representation and bounded projection. Only its reference pose is changed from the actual last controller target to the achieved EE pose. Therefore the matched comparison isolates the *value of current target-controller memory* under this simulated intervention.

## Immutable actual original artifact SHA-256

| Original file from completed 5-JSON artifact | SHA-256 |
|---|---|
| stateful_abi_memory_ablation_aggregate.json | 06d3cfb009098e9c94ea04d3713e235d35df99f20587a438f1d30a3eb9a134fe |
| stateful_abi_memory_ablation_chunk_0.json | 52031796cc73d416756289f588d5c0ffe4ccef5623a0e9b63ccbaebec0fc70f2 |
| stateful_abi_memory_ablation_chunk_1.json | 2b07c75f674e0393ca293beb3e637818404aa96902a0a4f545e298c28e3b815c |
| stateful_abi_memory_ablation_chunk_2.json | 3f366a2a42a24100a8ddca64272b9e706b6763941ad13ff5326e8a9d3c6d1621 |
| stateful_abi_memory_ablation_chunk_3.json | 89b9061db308c9cc11cc9b698f86ace8a2da9783fdd85d9549f317ffae673f33 |

Original artifact: https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37814189680 (complete-stateful-abi-memory-causal-ablation-32-originals). Runtime evidence was independently recomputed and these five ZIP file hashes verified. Do not infer permanent main-branch archival from a temporary workflow artifact; separate archive is needed.

## Independent previous task, not double-counted as new holdout

Historical PushCube unseen 41001–41032 result for a distinct released PPO: memory-aware bounded controller 29/32, matched state-blind bounded controller 20/32, with **11 stateful-only / 2 state-blind-only** paired successes. This existed before the current PickCube preregistration and is *not* new test data. Full records: https://github.com/lindicaphxag-tech/lindicaphxag-tech/blob/main/research/frozen_policy_transfer/evidence/pushcube_holdout_41001_41032.json

## Research boundary

Original-control-input models, standard constrained action projection and standard relative/absolute controllers have prior art. This task-specific result does not establish a first-ever action adapter, unseen-controller-family generalization, VLA behavior, physical safety or third-party deployment. All numbers above are author-side results. The separately frozen PullCube/StackCube task/checkpoint validation in https://github.com/lindicaphxag-tech/ManiSkill/pull/58 has NO POSITIVE OUTCOME CLAIM until its own real PhysX source and aggregator finish.
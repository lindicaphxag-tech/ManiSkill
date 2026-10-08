# Prospective 48-seed frozen PPO target-memory holdout — observed results

Canonical workflow: https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37809684134

**Frozen BEFORE this CI:** [48-seed protocol](TARGET_MEMORY_48_SEED_PRE_REG_2026_10_09.md)
Fixed task seeds 20001–20048 inclusive. All 48 individual records were
extracted from this single public run log, with no omissions.

**Important provenance:** the frozen third-party PPO is
`kattri15/actionshift-baselines/ppo/pick_cube_final_ckpt.pt`;
SHA256 `3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8`.
We neither trained nor fine-tuned it. The simulator was ManiSkill3
Panda/PickCube-v1, PhysX CPU with up to 50 steps/episode, and identical
initial policy-level observations for all paired controllers.

## Complete outcomes

| Method | Success | Rate |
|---|---:|---:|
| Frozen PPO on original achieved-relative controller | 47/48 | 97.92% |
| Strict memory-aware migration; refuse unrepresentable action | 8/48 | 16.67% |
| Memory-aware bounded projection of unrepresentable actions | **48/48** | **100%** |
| Target-relative controller with raw native-action copy | 6/48 | 12.50% |

There were **40/48 episodes** where exact action transport was refused;
the projected arm applied **43 non-exact projections across 40 episodes**,
with maximum required normalized original amplitude **1.6562**.
The projected arm succeeded on all 48; this does not prove exact
target-action or trajectory preservation, and the projected method was
selected on 4 earlier development episodes (seeds 42/270/429/2026).

Notably seed 20016 had source failure at 50 steps, while the projected
target successfully reached the task signal after 36 steps and used
four projected actions. This is a single paired observation, **not**
proof that approximation is superior to the original controller.

The 40 refused episodes were **not silently scored as converter task
failures** under a hypothetical safety policy; they are reported
separately as hard refusals, while the unconditional strict completion
count is 8/48. This is important when assessing executability vs task
success.

## Complete per-seed evidence

Y = task success_once; N = no success within fixed horizon.
Columns follow **source / strict / projected / raw-copy**.
Action amplitude is an upper envelope on source-desired
`pd_ee_target_delta_pose` *normalized native control* before projection.
No metric implies real-world safety.

| Seed | Source | Strict | Projected | Raw copy | Strict event | Projection steps | Required amplitude(s) |
|---:|:---:|:---:|:---:|:---:|:---|---:|---|
| 20001 | Y | N | Y | N | REFUSED | 1 | 1.489 |
| 20002 | Y | N | Y | N | REFUSED | 1 | 1.631 |
| 20003 | Y | Y | Y | N | — | 0 | — |
| 20004 | Y | N | Y | N | REFUSED | 1 | 1.433 |
| 20005 | Y | N | Y | N | REFUSED | 1 | 1.037 |
| 20006 | Y | N | Y | Y | REFUSED | 1 | 1.292 |
| 20007 | Y | N | Y | N | REFUSED | 1 | 1.449 |
| 20008 | Y | N | Y | N | REFUSED | 1 | 1.246 |
| 20009 | Y | N | Y | N | REFUSED | 1 | 1.471 |
| 20010 | Y | N | Y | N | REFUSED | 1 | 1.520 |
| 20011 | Y | N | Y | N | REFUSED | 1 | 1.233 |
| 20012 | Y | N | Y | N | REFUSED | 1 | 1.390 |
| 20013 | Y | N | Y | N | REFUSED | 1 | 1.417 |
| 20014 | Y | N | Y | N | REFUSED | 1 | 1.597 |
| 20015 | Y | N | Y | N | REFUSED | 1 | 1.296 |
| 20016 | N | N | Y | N | REFUSED | 4 | 1.580, 1.184, 1.606, 1.049 |
| 20017 | Y | Y | Y | N | — | 0 | — |
| 20018 | Y | N | Y | N | REFUSED | 1 | 1.517 |
| 20019 | Y | N | Y | N | REFUSED | 1 | 1.098 |
| 20020 | Y | N | Y | N | REFUSED | 1 | 1.281 |
| 20021 | Y | N | Y | N | REFUSED | 1 | 1.219 |
| 20022 | Y | Y | Y | N | — | 0 | — |
| 20023 | Y | N | Y | Y | REFUSED | 1 | 1.187 |
| 20024 | Y | N | Y | N | REFUSED | 1 | 1.065 |
| 20025 | Y | Y | Y | N | — | 0 | — |
| 20026 | Y | Y | Y | N | — | 0 | — |
| 20027 | Y | N | Y | N | REFUSED | 1 | 1.236 |
| 20028 | Y | N | Y | N | REFUSED | 1 | 1.551 |
| 20029 | Y | N | Y | N | REFUSED | 1 | 1.533 |
| 20030 | Y | N | Y | N | REFUSED | 1 | 1.622 |
| 20031 | Y | N | Y | Y | REFUSED | 1 | 1.145 |
| 20032 | Y | N | Y | N | REFUSED | 1 | 1.262 |
| 20033 | Y | N | Y | N | REFUSED | 1 | 1.050 |
| 20034 | Y | Y | Y | N | — | 0 | — |
| 20035 | Y | N | Y | N | REFUSED | 1 | 1.656 |
| 20036 | Y | N | Y | Y | REFUSED | 1 | 1.188 |
| 20037 | Y | N | Y | N | REFUSED | 1 | 1.611 |
| 20038 | Y | Y | Y | N | — | 0 | — |
| 20039 | Y | N | Y | N | REFUSED | 1 | 1.532 |
| 20040 | Y | N | Y | N | REFUSED | 1 | 1.043 |
| 20041 | Y | N | Y | Y | REFUSED | 1 | 1.417 |
| 20042 | Y | N | Y | N | REFUSED | 1 | 1.494 |
| 20043 | Y | N | Y | N | REFUSED | 1 | 1.559 |
| 20044 | Y | N | Y | Y | REFUSED | 1 | 1.527 |
| 20045 | Y | N | Y | N | REFUSED | 1 | 1.345 |
| 20046 | Y | N | Y | N | REFUSED | 1 | 1.456 |
| 20047 | Y | N | Y | N | REFUSED | 1 | 1.256 |
| 20048 | Y | Y | Y | N | — | 0 | — |

## Claim boundaries and next replication

- Standard bounded clipping/projection is established prior art. The
  potential original research problem is **controller-owned state
  completion + observability-consistent policy projection +
  executability detection / controlled relaxation**.
- A method that clips actions is **not** exactly executing the source
  policy when clipping occurs. Therefore do not use
  `same-policy execution-equivalent` for projected outcomes.
  It is *same frozen weights, modified execution semantics*.
- Only one frozen PPO, robot, task and native controller family have
  been tested for the learned-policy memory migration. Physics backend
  remains CPU simulation. No robot hardware tested.
- Compare stronger safe/receding-horizon constrained controllers,
  longer horizons, different gains/controller families, and new
  preregistered seeds/tasks before paper-level claims.
- Independently reproduced results and upstream maintainer approval
  have not been demonstrated.

Related prior work: [ActionShift](https://github.com/Archerkattri/actionshift)
already addresses hidden robot action-interface adaptation; this pilot
does not claim to invent action-coordinate conversion or bounded
projection.

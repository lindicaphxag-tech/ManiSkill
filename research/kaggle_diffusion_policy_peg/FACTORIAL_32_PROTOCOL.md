# Frozen 32-source-demo factorial replication: PegInsertionSide

Freeze **before running** this branch's CI. This is a CPU-only, 2×2
converter×controller *demonstration replay* experiment, NOT a policy-learning
outcome, SemRepair maintained adoption, or a prospective bug discovery.

## Exact source and intervention identity

- Environment and raw official demonstration archive: pinned
  `haosulab/ManiSkill_Demonstrations`,
  revision `d674485bbffdd533914e52d272fdda34c0515608`,
  `PegInsertionSide-v1.zip` SHA-256
  `7d61e4319a0395b220574f1e26ea65bd4ad1406387fb3debfbea96a2ddbb6a9c`.
- Frozen original source: `62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3`.
- Frozen converter `#1495`: `69facfaafaa0ef233d36ef19e6cd9a0f03532ee0`.
- Exact controller `#1472` patch:
  `eed9be164797d41540421bda8adb3840377d7087`, including
  archived regression blob `ce7e6e66cf3e286168d3d82f763307e18b587659`.
- Four cells: neither change, converter-only, controller-only, both.
- Each cell independently replays the **same first 32 source episodes**
  and the same preserved episode seed set. No cross-cell reuse of converted
  trajectory tensors. Seed membership is explicitly recorded.
- Headless state only, `physx_cpu`, `pd_ee_delta_pose`, software Vulkan
  Lavapipe available but `render_backend=none` at actual replay boundary.

## Confirmatory holdout and disconfirmation

The first **eight** source episodes were inspected in the earlier development
run (run `37715587885`). The **next 24** source episodes are held out for
replication in this freeze and their results are unknown as of this protocol.

Primary descriptive comparisons **on the 24 unseen source episodes**:

1. controller-only vs no-fix demo conversion success;
2. controller-only vs combined-fix success;
3. converter-only vs combined-fix success.

Record every result, including invalid trajectory conversion and zero successes.
Use exact source-seed pairing and a two-sided exact McNemar/binomial sign test on
discordant pairs as an accompanying descriptive statistic. Report denominators,
both directions of discordance and the point estimate of the 2×2 interaction,
without treating it as a multi-seed robot policy success estimate.

**Disconfirming outcome:** if the controller-only failure from the first 8
episodes does not replicate in the new 24 or if the four-cell sign/interaction
pattern changes, publish this discrepancy; do not retune selection thresholds
or remove failed episodes. If no four-way-successful seed intersection exists,
the corresponding four-cell **learned-policy paired trial is structurally
non-trainable**; do not invent policy metrics.

## Promotion gates

This 32-episode test is only a source-seed-paired replay replication. No
general claim of task-level policy improvement, external maintainer approval,
scientific mathematical priority or I2 external hit follows from it.

Publication-grade learned-policy claims require longer actual training, held-out
task success with independent policy random seeds, proper effect sizes/CIs,
the exact training/observation source hashes, and a documented baseline.

## Output audit

The fixed public branch must output `factorial_replay.json` containing exact
source seed membership, 4 per-cell success indicators per seed, overall and
held-out counts, pairwise discordances, exact sign test p-values and unambiguous
source identity. Raw demo data and checkpoints remain unexported.

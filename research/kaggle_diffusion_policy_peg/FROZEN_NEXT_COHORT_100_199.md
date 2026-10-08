# Locked next-cohort replay check: PegInsertionSide episode indices 100–199

**Committed before reading the enlarged 0–99 replay results.**
This is a reproducibility/selection guard, not a claim that the next cohort
exists or a prior independent third-party preregistration.

## Origin of the hypothesis

An author-run **8-episode** (indices 0–7) source-paired 2×2 official
replay [CI #37715587885](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37715587885)
reported baseline=6, converter-only=6, controller-only=0,
combined=6. Original 8-arm evidence was independently re-audited
[CI #37719750458](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37719750458).

**An enlarged 100-episode indices 0–99 exploratory replication**
[CI #37719545972](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37719545972)
has already started, but its four-arm outcome has NOT been inspected at the
time of this commitment. It overlaps the first eight and therefore is not
an independent holdout relative to the original discovery.

## Locked next cohort

- Fixed official dataset archive:
  `haosulab/ManiSkill_Demonstrations`, revision
  `d674485bbffdd533914e52d272fdda34c0515608`,
  `demos/PegInsertionSide-v1.zip`,
  SHA-256 `7d61e4319a0395b220574f1e26ea65bd4ad1406387fb3debfbea96a2ddbb6a9c`.
- Original source *episode indices* **100..199 inclusive** exactly in archived
  metadata order (no random seed cherry-picking), with their original
  `episode_id` and `episode_seed` identities.
- Abort, record and disclose `insufficient_holdout_source` if fewer than
  200 episodes are present, or if any selected record lacks stable seed,
  has duplicate seed, or is not flagged successful in original data.
  **Never substitute** a different cohort after viewing outcomes.
- All four source code intervention cells, replay backend, CPU mode,
  controller action encoding and checksum verification must match
  the 0–99 experiment:
  - base `62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3`
  - converter #1495 current head
    `69facfaafaa0ef233d36ef19e6cd9a0f03532ee0`
  - controller overlay #1472 head
    `eed9be164797d41540421bda8adb3840377d7087`.
- Each arm must independently replay the original raw cohort; per-seed
  binary conversion outcomes and four-arm source-seed pattern must be
  written before any survivor filtering or policy fitting.
- Do not train a policy on a failed arm with fewer than the required common
  demos; do not fabricate task success for such an arm.

## Frozen diagnostic predictions (generated from the *first eight*, not novel laws)

1. **Controller-only penalty**: replay-success rate with #1472 alone
   will be at least **0.20 absolute** lower than the baseline among
   original source indices 100–199.
2. **Composition effect**: #1495 + #1472 will have replay-success rate
   at least **0.20 absolute** higher than #1472 alone.
3. **Converter-only is not guaranteed beneficial**:
   explicitly report converter-only vs baseline in both directions;
   do not promote any increase without an original-denominator analysis.
4. **Interaction**: report observed finite-cohort
   `CK-C-K+B` and all four matched discordance tables, including zero
   surviving cells. No prespecified minimum interaction is required
   for a valid/negative test.

Each first-two prediction can be falsified independently; no replacing
results after seeing 0–99 or 100–199 outcomes. Passing thresholds does NOT
prove broad policy success, repair safety, gauge novelty, or external adoption.

## Evidence and external recognition boundary

This is an author's follow-up check motivated by an already observed
eight-case result. It is stronger against same-episode fitting than repeating
the 0–7 prefix but **not** a blind third-party test of the original
hypothesis, and is not a random sample of the full robot-task population.
Report exactly who executed the experiment; author-operated GitHub CI
does not earn a third-party reproduction/adoption credit.

A separate trained-policy success experiment requires complete training,
multiple independent policy and evaluation seeds, and complete reporting
of every failed conversion cell; demo replay is only a prerequisite.

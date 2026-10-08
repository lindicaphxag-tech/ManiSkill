# Erratum: original 100–199 replay is NOT a valid disjoint holdout

**Date:** 2026-10-08

## Status

**Withdrawn as validation evidence:** [previous nominally green replay
#37745942944](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37745942944).

The visible 90/91/1/91 replay counts from that workflow cannot be credited as a
disjoint 100–199 test. They do **not** establish a second-cohort replication.

## Mechanism and independently detected contradiction

The precommitted holdout document correctly froze original source-episode
indices 100–199, and `run_assay.py` sliced the original JSON metadata to
choose those indices for bookkeeping. However, the actual replay input was
still prepared with:

```python
shutil.copy2(raw_demo_path, arm_raw_path)
shutil.copy2(raw_meta_path, arm_raw_path.with_suffix(".json"))
```

The official `replay_trajectory --count 100` then consumed the **first 100
episodes of the full input HDF5**, rather than physically materializing
source groups 100–199. Thus the source index annotation was not bound to the
executed trajectories.

A separate SHA-auditing workflow downloaded the raw supposed holdout
[artifact #11537191729](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37745942944/artifacts/11537191729).
[Audit #37752017483](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37752017483)
correctly **FAILED** with
`ValueError: claimed success count differs from source-seed matrix`.

The auditor did not silently rewrite counts or reinterpret the cohort.

## Corrected experiment (not yet validated)

A new isolated branch,
[`fix/peg-heldout-source-selection-v2`](https://github.com/lindicaphxag-tech/ManiSkill/tree/fix/peg-heldout-source-selection-v2),
adds `slice_source_cohort.py` to physically copy only original HDF5
`traj_{episode_id}` groups 100–199 and *synchronously reindex* their JSON
episode IDs to 0–99 while preserving exact original episode seeds and
recording SHA-256 identities. It fails closed on missing groups, duplicate
source IDs/seeds, or changed cohort membership.

Its pipeline must pass both a new exact HDF5 selection test and all four
replays on the **actual sliced dataset**, followed by a separate original
artifact audit. Until then **there is no valid second-cohort result**.

The source cohort remains indices 100–199 as preregistered in
[`FROZEN_NEXT_COHORT_100_199.md`](FROZEN_NEXT_COHORT_100_199.md).
It is **not** replaced with a new or more favorable cohort.

## Evidence that remains valid

- 0–7 exploratory replay: 6/6/0/6, from 8 original demonstration requests.
- 0–99 first-cohort replay: 90/91/1/91, 100 frozen requests, with successful
  independent source-seed matrix/digest audits.
- Two-arm paired official Diffusion Policy smoke: six matched demonstrations,
  893 transitions per arm, two optimizer updates per arm, both arms 0% on
  very short evaluation horizons.

These results support a software contract interaction *hypothesis*, not
learned-policy superiority or upstream maintainer adoption.

**No external recognition/I2/reproduction counter was incremented.**

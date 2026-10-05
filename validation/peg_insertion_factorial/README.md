# PegInsertionSide policy-level 2x2 causal validation

This validation branch answers the policy-level question requested by the
ManiSkill maintainer in issue #1138.

It separates two semantic faults in the `pd_ee_delta_pose` path:

- **C** — controller scaling fix from upstream PR #1472;
- **E** — converter representation fix from upstream PR #1495.

The four frozen source conditions are:

| condition | controller | converter | source commit |
|---|---|---|---|
| 00 | legacy | legacy | `62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3` |
| 10 | #1472 | legacy | `a231074ef562a9638e24c3f9a4d35bb70d4960d1` |
| 01 | legacy | #1495 | `cdd6db713ffe7edc3e0df3abfab51ea5320c1c0b` |
| 11 | #1472 | #1495 | `24dcccba3d0aeae56b6fba1f5168e22cc340ab71` |

The validation-only unit assay on this repository already establishes the
mechanism-level factorial closure: fixing either boundary alone remains wrong,
while 11 reconstructs the intended non-commuting rotation.

## Why the demonstrations must be regenerated

PR #1495 changes trajectory conversion. Reusing one pre-converted
`trajectory.state.pd_ee_delta_pose.physx_cpu.h5` for all four conditions would
erase the converter intervention from the training labels.

This protocol therefore starts from the same original motion-planning
`trajectory.h5` (pd_joint_pos) and replays it independently under each source
condition.

## Anti-selection protocol

Replay defaults to `allow_failure=False`, so different source conditions may
save different subsets of successful demonstrations. Training each condition on
"its own first 100 successful demos" would confound semantics with dataset
selection.

The protocol therefore:

1. replays the same first 150 original episodes under all four source conditions;
2. records each condition's replay-success set;
3. intersects the saved episode IDs;
4. requires at least 100 common episodes for the primary policy comparison;
5. materializes exactly the same first 100 common episode IDs into all four
   training datasets;
6. hashes every resulting HDF5/JSON pair.

If fewer than 100 common episodes survive, the primary policy comparison is
**not** considered valid. Replay-success differences are still reported as a
conversion-level result.

## Official baseline configuration

The training command follows ManiSkill's own state Diffusion Policy baseline for
PegInsertionSide-v1:

- 100 demonstrations;
- `pd_ee_delta_pose`;
- `physx_cpu`;
- max episode steps 300;
- 100,000 training iterations;
- evaluation every 5,000 iterations;
- 100 evaluation episodes;
- seed 1 for the maintainer-facing first pass.

A paper-level replication should use additional predeclared seeds rather than
treating one training run as an independent scientific result.

## Run

From this validation branch:

```bash
bash validation/peg_insertion_factorial/setup_worktrees.sh
bash validation/peg_insertion_factorial/convert_all.sh
python validation/peg_insertion_factorial/make_common_subset.py \
  --root "${PWD}/.factorial" --n-common 100
bash validation/peg_insertion_factorial/train_all.sh 1
python validation/peg_insertion_factorial/collect_results.py \
  --root "${PWD}/.factorial" --seed 1
```

The raw demonstrations are downloaded once and copied into isolated
condition-specific asset roots before replay, so converted files cannot overwrite
each other.

## Primary metrics

For every condition:

- conversion success count / attempted original episodes;
- exact common episode set;
- converted-dataset SHA256;
- best and final `eval/success_once`;
- best and final `eval/success_at_end`;
- training seed and exact source commit.

The causal comparison is the 2x2 table, not a single patched-vs-main number.

## Claim boundary

The factorial unit test is mechanism evidence.
This GPU policy experiment is the maintainer-requested policy-level evidence.
Neither counts as external adoption until an upstream maintainer retains the
change in the default branch.

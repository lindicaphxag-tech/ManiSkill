# PegInsertionSide Diffusion Policy Factorial — Execution Protocol

Validation branch: `validation/peg-insertion-dp-factorial`

This is project-native evidence for ManiSkill #1138 / #1472 / #1495. It is
not a SemRepair benchmark and does not count as external adoption by itself.

## Frozen four cells

| Cell | Converter | Controller | SHA |
| --- | --- | --- | --- |
| A | old | old | `62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3` |
| B | old | #1472 | `a231074ef562a9638e24c3f9a4d35bb70d4960d1` |
| C | #1495 | old | `cdd6db713ffe7edc3e0df3abfab51ea5320c1c0b` |
| D | #1495 | #1472 | `24dcccba3d0aeae56b6fba1f5168e22cc340ab71` |

## Critical validity rule

Do **not** reuse one preconverted
`trajectory.state.pd_ee_delta_pose*.h5` across cells.

#1495 modifies trajectory conversion. Every cell must start from the same raw:

```text
PegInsertionSide-v1/motionplanning/trajectory.h5
```

and independently replay it into `pd_ee_delta_pose`.

The harness hashes the raw and converted datasets and refuses official training
when converted episode counts differ.

## One-time environment

From this validation branch:

```bash
python -m pip install -e .
python -m pip install -e examples/baselines/diffusion_policy
python -m mani_skill.utils.download_demo PegInsertionSide-v1
```

The raw demonstration should then exist under the normal ManiSkill demo root.

## Smoke gate

Smoke is only an execution/installation check:

```bash
python validation/run_peg_insertion_dp_factorial.py \
  --work-root <work>/peg_factorial \
  --raw-demo ~/.maniskill/demos/PegInsertionSide-v1/motionplanning/trajectory.h5 \
  --phase all \
  --profile smoke \
  --seed 1
```

Never report smoke success as policy-performance evidence.

## Official seed-1 block

Run all four cells under one frozen configuration:

```bash
python validation/run_peg_insertion_dp_factorial.py \
  --work-root <work>/peg_factorial \
  --raw-demo ~/.maniskill/demos/PegInsertionSide-v1/motionplanning/trajectory.h5 \
  --phase all \
  --profile official \
  --seed 1 \
  --track \
  --wandb-project-name SemRepair-ManiSkill-Factorial
```

Official profile follows the upstream state baseline:

- 100 demonstrations;
- 100,000 training iterations;
- 300 max episode steps;
- eval every 5,000 iterations;
- 100 eval episodes;
- 10 eval environments;
- `pd_ee_delta_pose`;
- `physx_cpu` simulation backend.

## Seed expansion rule

Do not decide whether to run more seeds after inspecting only a favorable cell.

After the complete four-cell seed-1 block:

- if the harness/environment is invalid, fix the protocol and rerun all four;
- if the block is valid, freeze the analysis and run seeds 2 and 3 with
  `--phase train` using the already frozen replay outputs;
- negative or null results are retained.

## Primary readout

The upstream-facing result should lead with:

1. conversion/replay success and episode counts;
2. `success_once`;
3. `success_at_end`;
4. training/eval curves;
5. the already-established SO(3) causal 2x2 result;
6. exact code/dataset hashes and environment manifest.

Do not lead with SemRepair terminology. The maintainer asked whether the
rotation convention affects the official Diffusion Policy path; answer that
native project question directly.

## Interpretation discipline

A strong D result with weak B/C is evidence that representation convention and
controller sign are complementary faults.

A strong A result is not automatically evidence against the two bugs: the
existing geometry assay shows that the two old faults can partially cancel.
Policy results must therefore be interpreted together with the causal SO(3)
factorial.

If replay episode counts differ, that is a conversion/controller outcome, not a
license to train mismatched datasets. Stop and report the replay result first.

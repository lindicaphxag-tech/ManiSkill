# Hugging Face Jobs launch packet — ManiSkill #1495

Status: launch-ready, **not launched**. GPU execution incurs Hugging Face Jobs
charges and therefore requires explicit spend authorization.

## Why this surface

The maintainer request in ManiSkill #1138 is concrete: train the
PegInsertionSide Diffusion Policy with the fix and share training curves.

This packet executes exactly that frozen comparison. It is not a new benchmark.

## Container

Use ManiSkill's documented Docker image:

`maniskill/base`

The upstream ManiSkill documentation states that this image supports CPU/GPU
simulation and includes the CUDA/Vulkan environment expected by SAPIEN.

The entrypoint then installs the **exact source SHA** under test in editable
mode, so the preinstalled ManiSkill wheel is not the experiment identity.

## Recommended hardware

Default: Hugging Face Jobs `t4-medium`.

Reason:
- 1x T4, 16 GB GPU memory;
- 8 vCPU / 30 GB RAM;
- PegInsertionSide evaluation uses `physx_cpu` with 10 eval environments, so
  CPU capacity matters as well as model-training GPU capacity.

Current published Jobs price at packet creation: **$0.60/hour**.

Use an explicit timeout. A 10-hour cap bounds one variant to $6.00 and the
seed-1 pair to $12.00 maximum compute charge. This is a cap, not an estimate of
actual runtime.

A10G is not the default because `a10g-small` currently provides fewer CPU
cores (4) at a higher hourly price ($1.00/hour), although it has more GPU
memory.

## Frozen seed-1 pair

Both jobs use:
- `SEED=1`
- `NUM_DEMOS=100`
- `TOTAL_ITERS=100000`
- `TRACK_MODE=tensorboard` unless a W&B secret is deliberately supplied.

### Baseline job

Image:
`maniskill/base`

Flavor:
`t4-medium`

Timeout:
`10h`

Environment:

```text
VARIANT=baseline
SEED=1
TRACK_MODE=tensorboard
```

Command:

```text
/bin/bash /path/to/hf_job_entrypoint.sh
```

### Fixed job

Identical except:

```text
VARIANT=fixed
```

## Frozen launcher identities

- bootstrap / entrypoint SHA: `1f778f58dbfd9c94cb5e6b64affbf26f11fa18ee`
- experiment-harness SHA: `7e3ee79fd50979c15bd9d234d4a120d04e05a7e3`

The bootstrap commit only needs to contain the launcher. The launcher then clones
the separately frozen experiment harness, so updating this documentation cannot
silently change the experiment.

## Cloud bootstrap command

HF Jobs starts from a Docker image, so the practical command clones only the
small validation harness and invokes the committed entrypoint:

```bash
set -euo pipefail
git clone --filter=blob:none https://github.com/lindicaphxag-tech/ManiSkill.git /tmp/harness
git -C /tmp/harness fetch origin 1f778f58dbfd9c94cb5e6b64affbf26f11fa18ee
git -C /tmp/harness checkout --detach 1f778f58dbfd9c94cb5e6b64affbf26f11fa18ee
exec bash /tmp/harness/validation/pr1495/hf_job_entrypoint.sh
```

The entrypoint then checks out a frozen harness commit and the runner separately
clones the exact baseline/fixed source SHA.

## Evidence survival

No persistent disk is required for the primary evidence.

At completion the runner prints:

1. `manifest.json`;
2. `summary.json` containing the complete TensorBoard scalar series.

Therefore the immutable Job log retains:
- code identity;
- raw/converted demo hashes;
- episode counts;
- GPU identity;
- success/loss curves.

If W&B is desired later, set `TRACK_MODE=wandb` and pass `WANDB_API_KEY` as
a Jobs secret. Do not put the key in a normal environment variable or repo.

## Acceptance gate before using the result upstream

The pair counts only if:

- both jobs used the same seed, demo count, iteration count and raw-demo hash;
- baseline manifest target SHA equals the frozen baseline;
- fixed manifest target SHA equals the upstream PR head;
- converted-demo hashes may differ, because conversion is the intervention;
- both converted episode counts are recorded;
- neither run silently changes training hyperparameters;
- the full scalar series is present for both runs.

A null or negative result is retained.

## Cost gate

Do not launch either paid job from automation until the account owner explicitly
authorizes the GPU spend.

The protocol smoke in GitHub Actions is free of this gate and currently passes.

# ManiSkill #1495 — maintainer-requested PegInsertionSide validation

Purpose: answer the exact follow-up requested by the ManiSkill maintainer in
issue #1138: run the Diffusion Policy baseline on `PegInsertionSide-v1` and
share training/evaluation curves for the rotation-convention fix.

This validation branch is deliberately **not** the upstream PR branch. The
upstream patch stays at one commit / two files. Training infrastructure and
evidence live here so reviewer-facing code remains minimal.

## Frozen comparison

- upstream baseline: `mani-skill/ManiSkill@62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3`
- PR #1495 fix: `lindicaphxag-tech/ManiSkill@cdd6db713ffe7edc3e0df3abfab51ea5320c1c0b`
- environment: `PegInsertionSide-v1`
- demonstrations: official ManiSkill motion-planning demos
- observation: state
- control mode: `pd_ee_delta_pose`
- simulation backend: `physx_cpu`
- demos: 100
- max episode steps: 300
- training iterations: 100000
- primary evaluation metrics: `eval/success_once`, `eval/success_at_end`
- tracking: Weights & Biases + local TensorBoard
- initial seed: 1
- confirmation seeds after a signal is observed: 2 and 3

The core training settings are copied from ManiSkill's own
`examples/baselines/diffusion_policy/baselines.sh`. They are not tuned from
the outcome of this comparison.

### Causal hygiene: variant-private demo conversion

The raw official motion-planning trajectory is copied into a directory named by
`VARIANT + TARGET_SHA`, then replayed/conversion-generated **unconditionally**
under that exact source revision. Baseline and fixed runs therefore cannot reuse
the same derived `pd_ee_delta_pose` trajectory even when executed sequentially
on one machine.

Each manifest records:

- SHA-256 of the common raw trajectory copy;
- SHA-256 of the variant-derived trajectory;
- raw and converted episode counts;
- exact source SHA and GPU identity.

This prevents a subtle false-null failure mode in which the fixed run would
silently train on a trajectory converted by the baseline implementation.

## Online-GPU execution

The runner is designed for an ephemeral cloud notebook/VM such as Kaggle or
Colab with a CUDA GPU. Run baseline and fixed variants in separate clean
sessions if GPU memory or package state is tight.

```bash
export WANDB_API_KEY=...
export WANDB_PROJECT=maniskill-pr1495-peg-dp

VARIANT=baseline SEED=1 bash validation/pr1495/run_peg_dp.sh
VARIANT=fixed    SEED=1 bash validation/pr1495/run_peg_dp.sh
```

If seed 1 shows a material divergence, repeat with `SEED=2` and `SEED=3`.
Do not change hyperparameters between variants.

## Evidence boundary

A single-seed curve can satisfy the maintainer's requested reproduction, but it
is not a statistically strong policy-performance claim. Three paired seeds are
the minimum planned confirmation set for a research-facing statement.

The desired external-facing result is not "our patch must win." A null result
or regression is retained and reported. The experiment exists to determine
whether the representation correction has end-to-end policy consequences under
the official baseline.

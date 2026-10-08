# Reproduce the frozen PPO state-memory controller compiler (CPU)

Independent reproduction entry point. No proprietary datasets, robot
hardware, training, or GPU needed. The checkpoint belongs to ActionShift
and is credited accordingly. Results below are from author-run CI,
**not** independently replicated externally.

## Environment (Linux CPU / Python 3.11)

```bash
git clone https://github.com/lindicaphxag-tech/ManiSkill.git
cd ManiSkill
git checkout validation/frozen-ppo-memory-only-ablation-20261008
# On Ubuntu install libvulkan1 mesa-vulkan-drivers libgl1 libosmesa6
python -m pip install -e . huggingface_hub
python research/frozen_ppo_target_memory.py
```

The script downloads immutable external frozen PPO weights, verifies
`sha256=3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8`,
checks projected 42-D policy observations against the full 49-D target
ABI (including its 7-D controller target), and runs **all 32 seeds
30001..30032**. No fine-tuning occurs.

Canonical already-run workflow:
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37751599480

Results: source 31/32; exact-memory/refuse 6/32; memory-aware bounded
projection 32/32; achieved-pose-only bounded projection 2/32;
direct-copy native policy actions 2/32. Full per-seed JSON is printed
as `FROZEN_TARGET_MEMORY_EPISODE` and saved in
`frozen_ppo_target_memory.json`.

**Primary scientific discriminator:** compare the two bounded-projector
arms. Their policy checkpoint and action chart stay the same.
One reads the *previous controller target pose*; the other uses
the *current achieved end-effector pose*. Merely adding another
action scaling/clipping procedure cannot explain why they differ.

## Reproduce separate experiments (do not aggregate as same holdout)

```bash
git checkout validation/frozen-ppo-target-memory-32-holdout-20261008
python research/frozen_ppo_target_memory.py
# seeds 20001..20032; prior independent feasibility holdout

git checkout validation/frozen-ppo-10014-reproducibility-20261008
# The workflow runs 12 independent processes and saves initial-state hashes.
# Do NOT reinterpret those as 12 independent episode seeds.
```

The stateful method emits **APPROXIMATE_BOUNDED_PROJECTION** when a native
target delta lies outside source action limits. This is a non-exact
surrogate action; even if the task succeeds it is **not an exact
controller-equivalence certificate**.

## Falsification and external review requested

The strongest potential counterexamples are:
- A task/controller where previous-target memory is irrelevant,
  yet the memory-aware method appears to have an advantage.
- Another robot/policy where bounded projection harms source competence.
- Changes to action integration, reference-frame semantics, gravity,
  contact solver, or variable impedance that violate our assumptions.
- A run where 42-D projection is not the exact trained policy input ABI.

Please include exact commit and dependency versions, per-seed logs,
first divergent step, and the control/observation-mode contracts. We
seek negative reports as strongly as positive reproductions.

The public code targets a specific simulator/controller implementation,
not general robot safety. Generic delta/absolute action adaptation,
target tracking, and bounded projection are established prior work;
their isolated novelty is not claimed.

> **REPRODUCIBILITY UPDATE, 2026-10-08:** The original prospective
> batch below is a true record of that specific run, but its seed
> 10014 failed compiled-controller outcome **was not stable across
> independent executions**. A standalone rerun, and 8 repeated
> single-seed episodes, each succeeded (source step 19, compiled step 25).
> Two separate **full 32-seed** reruns then produced
> **32/32 source, 32/32 compiled, 0/32 naive**:
> [original-order rerun](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37746035726),
> [per-episode Python/NumPy/Torch reseeded rerun](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37746063527).
> Seed 10014's initial **observation** SHA matched across those two
> instrumented reruns and 8 standalone repeats, but the original 31/32
> batch did not log its exact initial-state fingerprint. Version lists
> of the core simulator/PyTorch dependencies appeared identical across
> initial and repeated runs. Root cause remains **unproven**: this may
> be unrecorded full physical state, simulator numerical effects, or
> runtime details. Do not call seed 10014 a reproducible failure or
> quote 31/32 as a stable deterministic rate. Both 31/32 and 32/32 are
> genuine observed batches.

# Prospective disjoint 32-seed frozen PPO controller-swap holdout — final results

**Canonical successful CI:** https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37716840505

**Pre-registration (published before the run):**
[FROZEN_PPO_32_SEED_HOLDOUT_PRE_REG_2026_10_08.md](FROZEN_PPO_32_SEED_HOLDOUT_PRE_REG_2026_10_08.md)

**Exact public test source:**
https://github.com/lindicaphxag-tech/ManiSkill/blob/validation/frozen-ppo-ee-controller-swap-holdout-20261008/research/frozen_ppo_ee_swap.py

## Design and model provenance

- External MIT PPO checkpoint (ActionShift publication):
  `kattri15/actionshift-baselines/ppo/pick_cube_final_ckpt.pt`
- SHA-256 `3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8`.
- **Frozen neural actor**, no training or fine-tuning.
- Official ManiSkill Panda / PickCube-v1, `obs_mode=state`,
  PhysX CPU, 50-step maximum.
- Three separately stepping *real simulator* environments, each with its
  own source state observations: source `pd_ee_delta_pose`, destination
  `pd_ee_pose` with semantic transform, and destination `pd_ee_pose`
  with raw native-action copy.
- **All 32 exact preselected unseen seeds, 10001–10032, were run**;
  no seed omitted. Initial observations source-vs-target have
  `initial_obs_maxdiff=0.0` for every episode.
- The earlier 4 development seeds `42,270,429,2026` are **not part** of
  these results and were not included in the denominator.

## Frozen, unconditional results

| Controller arm | Success / 32 | Fraction |
|---|---:|---:|
| Source `pd_ee_delta_pose` | **32/32** | 100% |
| Compiled `pd_ee_pose` | **31/32** | 96.875% |
| Naive raw action into `pd_ee_pose` | **0/32** | 0% |

Paired `compiled - naive`: **31/32 episodes** (+96.875 percentage points).
Paired `compiled - source`: **-1/32 episode** (-3.125 percentage points).

**One genuine migration failure retained:** seed `10014`. The source PPO
succeeded at step 31; the compiled destination did **not** reach success
before the fixed 50-step horizon; the naive target also failed. No
post-hoc seed filtering, threshold change, extra training, or dropped
run was applied. Other 31 episodes succeeded under compiled target at
the same step as the source controller in the public log.

Source-vs-compiled discordant pairs: 1 source-only success, 0
compiled-only successes.
Compiled-vs-naive discordant pairs: 31 compiled-only successes, 0
naive-only successes.

The canonical run retains a machine-readable
`frozen_ppo_controller_swap.json` artifact and 32
`FROZEN_PPO_SWAP_EPISODE` log entries.

## What this validates / scientific caveat

This is now a **real frozen trained policy, closed-loop
own-observation evaluation**, no longer a scripted-action toy example.
It shows that using the correct physical target action chart can
substantially outperform sending raw trained-policy outputs into an
incompatible controller; the underlying action-chart principle is
**already known in prior research**, so we do NOT claim a broad
first-in-literature novelty.

**The one seed-10014 failure falsifies any claim that a correct
instantaneous action transformation universally preserves task success.**
Potential contributors include physically different controller
integration/IK, floating-point perturbation amplified by feedback and
contact, and late-horizon nonlinear dynamics. These are hypotheses
until directly tested; it cannot be attributed to hidden controller
memory or action saturation on present evidence.

Generalization still needs: a different task/policy, a held-out controller
family, explicit memory-state transfer, long-term closed-loop robustness,
nonrepresentability diagnostics, independently run reproduction, and
an upstream maintainer review/merge. This is not hardware-safety evidence,
not a formal guarantee, and not a top-conference paper acceptance.


## Replication warning added after independent diagnostic replay

**Important newly observed negative result about reproducibility:**
a separate full source/compiled/naive reenactment of *integer seed 10014*
on a fresh CI runner **did not reproduce the initial failure**.

- Original preregistered 32-trial workflow:
  https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37716840505
  — for integer seed 10014, source succeeded at 31 steps and compiled
  failed by the 50-step horizon.
- Later independent per-step diagnostic:
  https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37717458927
  — for **the same integer seed 10014**, source succeeded at 19 steps and
  compiled succeeded at 25 steps. Initial *within-run* source/compiled
  observations still matched to machine precision.

**Correction:** the phrase "seed 10014 is a reproducible migration failure"
is not supported. The initial 31/32 vs 32/32 vs 0/32 counts are true
for their *exact public CI trial* and must remain as originally observed,
but integer seeds alone did not yet certify identical scene initialization
across separate workflow runs. The simulator may have other uncontrolled
randomization/runtime variability, which requires diagnosis.

The original experiment was **paired within run**, but it should not be
called a fully reproducible *scene-level seeded holdout* until a scene state
fingerprint and randomization reproducibility are demonstrated.

A repeated-initialization audit (same integer seed repeated four times
with hashed first observations and outcomes) is now in a separate
validation branch, not altering the original frozen result:
https://github.com/lindicaphxag-tech/ManiSkill/tree/validation/frozen-ppo-seed10014-repeatability-20261008

No change to the original outcomes, outcome denominator, seed set or
success counting was made to manufacture a stronger result.

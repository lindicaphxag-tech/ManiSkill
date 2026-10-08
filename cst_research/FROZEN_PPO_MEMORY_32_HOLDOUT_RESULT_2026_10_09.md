# Controller-owned target memory + bounded feasibility transport — 32-seed result

**Canonical public run:** https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37808039983

**Frozen prospective protocol committed before launching this run:**
[FROZEN_PPO_MEMORY_FALLBACK_32_HOLDOUT_PREREG_2026_10_09.md](FROZEN_PPO_MEMORY_FALLBACK_32_HOLDOUT_PREREG_2026_10_09.md)

**Executable source at validation ref:**
https://github.com/lindicaphxag-tech/ManiSkill/blob/validation/frozen-ppo-memory-projected-holdout-20261009/research/frozen_ppo_target_memory.py

## Setup

- 32 full episodes, fixed seeds 20001–20032, no omitted episode.
- Source: third-party published ActionShift PPO weights,
  `kattri15/actionshift-baselines/ppo/pick_cube_final_ckpt.pt`,
  SHA256 `3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8`.
  Frozen actor, no training/fine-tuning. Credit the original authors.
- Genuine ManiSkill Panda/PickCube-v1 physical simulation on PhysX CPU.
- Source controller: achieved-relative `pd_ee_delta_pose`.
- Target controller: **stateful**
  `pd_ee_target_delta_pose`, whose actions are relative to previous
  controller target memory and whose observations include extra 7D
  `target_pose` not present in the pretrained PPO's 42D input.
- Target observation projection verifies the live `target_pose` values
  and removes *only* that controller memory field before evaluating the
  frozen actor. Target-memory values remain available to the execution
  adapter, but not passed through the policy's incompatible input ABI.
- Four independently stepping environments per trial: source, exact
  live memory or refuse, live-memory-plus-bounded-projection, and naive
  raw native action. Matched initial 42D projected observations
  (all differences = 0.0).
- Per-episode 50-step cap, official task-success signal.

## Unconditional results

| Arm | Succeeded / 32 | Fraction |
|---|---:|---:|
| Source achieved-delta PPO | **31/32** | 96.875% |
| Exact target-memory transform, refuse nonrepresentable actions | **5/32** | 15.625% |
| Target-memory transform + explicit bounded non-exact projection | **32/32** | 100% |
| Target-delta controller, no conversion | **3/32** | 9.375% |

- Paired bounded-minus-exact = **+27/32** (+84.375 pp); all 27
  exact-migration refusals resulted in success with the projected action
  variant in THIS run. This is a single-task empirical observation, not a
  guarantee of projection benefit at every step.
- Paired bounded-minus-naive = **+29/32** (+90.625 pp).
- Paired bounded-minus-source = **+1/32** (+3.125 pp); the source
  failure occurred at **seed 20016**, where the projected target
  succeeded. This single discordant trial does not warrant claiming
  improved source-policy competence: stochastic/numerical sensitivity
  has been observed on another seed (10014).
- **27/32** target episodes required a feasibility correction;
  **30** total non-exact projected steps. Required normalized action
  amplitude among projected steps ranged **1.0374–1.6309**.
- No projection is described as mathematically exact. For positions,
  componentwise [-1,1] clipping implements Euclidean projection onto
  a box. For rotations, norm scaling projects onto the unit ball.
  This is a **simple optimization baseline**, not a novel advanced
  controller method on its own.
- All 32 executed and CI succeeded. Raw per-episode records remain
  in the `FROZEN_TARGET_MEMORY_EPISODE` CI log and workflow artifact.

## Important scientific limitation

The label “32 seeds” denotes 32 chosen calls to environment reset.
**Repeated CI executions have not yet established deterministic
per-seed outcomes**. An earlier source/compiled action-chart study gave
a seed-10014 compiled failure in one batch but success on the same
nominal seed in an isolated diagnostic run. We therefore report this
32-seed result as **one full experimental batch**, not a seed-deterministic
success guarantee. A fresh CI replication with the exact same evaluator
Git blob was triggered separately:
https://github.com/lindicaphxag-tech/ManiSkill/tree/validation/frozen-ppo-memory-projected-replication-20261009
and its results must be reported even if they disagree.

This does not establish cross-policy/cross-task gains, real hardware safety,
true probabilistic confidence under all sources of stochasticity, an
algorithmic novelty claim for clipping, or external upstream adoption.

## Research advancement criteria

1. At least one independent repeated batch + diagnose stochastic
   variation. Preserve differing outcomes without data replacement.
2. Compare with **naive clipping of unconverted policy output** and
   simpler achievable-pose baselines to isolate value of state transfer;
   no performance credit for mere action-range bounding.
3. Test a different pretrained policy and a *different task/controller
   family*. One Panda/PickCube configuration is not broad transfer.
4. Introduce controlled controller-state corruption/delay experiments
   and evaluate refusal versus harmful acceptance, not only success.
5. Explore genuinely new **feasibility-aware controller-memory program
   compilation** (precise state contract, constraints, automatic
   well-typed actions and certified/explained approximate execution)
   beyond established action chart transforms and ordinary clipping.
6. Independent maintenance/reproduction and public acceptance of a
   **matching** mechanism are still unachieved.

Adjacent examples that narrow broad novelty claims:
- ActionShift: https://github.com/Archerkattri/actionshift
- TAM (CoRL 2026): https://dongwon-son.github.io/tam-project-page/
- Tune to Learn: https://arxiv.org/abs/2604.02523


## Fresh CI replication, not a new independent holdout

A second GitHub Actions workflow executed the **identical Python source
blob** `c1b1b2dcd39e549a91f99540ba9cd05bc7bae51e`
against **the same predefined 32 seeds**:
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37809034284

Original:
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37808039983

All **128 per-seed binary method outcomes** (32 seeds × four methods)
were identical across both runs. Both summaries are exactly:
- source 31/32, exact/refuse 5/32,
  target-memory bounded projection 32/32, naive 3/32;
- refusals in 27/32, 30 projected actions;
- source-alone unsuccessful seed **20016**;
- no seed had a materially changed maximum required native amplitude
  (tolerance 1e-4 in our comparison).

This is a useful **repeatability check** under matched environment/setup,
not 64 independent holdout seeds. Do not double the sample size or report
a tighter independent-trial confidence interval. It does not resolve
different earlier seed-10014 behavior across modified diagnostic and
batch-run protocols; that issue remains separately recorded.

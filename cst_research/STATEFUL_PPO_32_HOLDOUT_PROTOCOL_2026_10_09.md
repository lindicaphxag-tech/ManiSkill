# Prospective stateful frozen-PPO migration holdout — 2026-10-09

Written before any 32-seed target-memory feasibility holdout outcome.

## Research question

How often does converting a competent fixed PPO's
`pd_ee_delta_pose` source actions into ManiSkill
`pd_ee_target_delta_pose` require an action **outside the target
controller's representable native bounds**? If such a mismatch occurs,
does an explicitly **non-exact** action-feasible projection sustain
task success better than a strict refuse-on-unrepresentable contract?

This is an action+observation ABI and controller-history integration,
not a claim of discovering generic delta/absolute conversion.

## Fixed prospective sample

Seeds **20001 through 20032 inclusive**, selected before running.
No replacement or exclusion of failures. These are disjoint from
earlier development seeds [42,270,429,2026] and earlier
delta->absolute holdout [10001..10032].

Original third-party frozen PPO:
`kattri15/actionshift-baselines/ppo/pick_cube_final_ckpt.pt`;
SHA256
`3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8`.
No model training or adaptation of weights.

Four **separately simulated** paired arms, each with own observations:
- `source`: original `pd_ee_delta_pose` controller.
- `memory`: exact runtime previous-target conversion, refuse if
  native target action amplitude >1+1e-5.
- `projected`: same runtime conversion with **bounded closest
  native input projection** (box for xyz, unit ball for rotation);
  every projected step is labeled `NOT_EXACT`.
- `naive`: direct-copy native source action into target-delta controller.

Projection cannot be called exact, safe, or optimal in task space,
and has no claimed general guarantee of parity. The target's
7D controller target_pose is explicitly removed *only from the PPO
observation*, not from the runtime converter's memory; verify the
removed bytes equal actual controller memory on each call.

Official ManiSkill PickCube-v1 Panda, PhysX CPU, 50 actions maximum
per episode per arm. All arms reset to the same seed, compare projected
initial `obs_mode=state` equality (tolerance 5e-4). Incompatible
initial observations are experimental invalidity, not failure.

## Prespecified reporting

- All 32 source/strict/projected/naive success counts.
- All strict-refused episode counts and exact first refusal step.
- Number of projection steps, maximum required preprojection action
  amplitude, and how many projected successes involved an actually
  clipped command.
- Paired discordant episodes projected-vs-strict and
  projected-vs-naive, no selective exclusion.
- Explicit every-seed outcome, including negative outcomes, 50-step
  censored incomplete episodes, and any controller exception.
- If no run finishes or a code bug prevents it, say *inconclusive*.
- 32 seeds are an author-run single-policy single-task **pilot**,
  not independent replication, formal safety, or L8/L9 recognition.

## Grounded initial four-seed pilot (excluded from 32 holdout)

Source 4/4, strict 2/4 (two feasibility refusals at normalized
amplitudes 1.42 and 1.62), bounded projection 4/4 with one
non-exact projected step in each of the two strict-refused
episodes, naive 1/4.

Canonical evidence:
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37717601656

No further parameter tuning is allowed after observing the new
holdout without labeling it post-hoc exploratory.

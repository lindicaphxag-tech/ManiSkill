# FROZEN PPO desired-target controller: first disjoint 32-seed pilot protocol

**Registered before running** the 32-seed four-arm experiment.
The following outcomes are deliberately *not* yet known.

## Data selection / leakage prevention

Holdout seeds: all integers **20001..20032** inclusive, in ascending
order. Do not replace, drop, filter or tune any of these after seeing the
outcomes. This does **not** overlap:
- development seeds 42,270,429,2026;
- initial delta->absolute pilot seeds 10001..10032.

Task PickCube-v1/Panda/PhysX CPU, 50 control steps max.
Frozen third-party ActionShift PPO checkpoint
`kattri15/actionshift-baselines/ppo/pick_cube_final_ckpt.pt`,
SHA256
`3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8`.
No training or online policy parameter updates.

## Four matched-arm interventions

Each arm creates its own simulator, is reset with the same nominal seed,
and runs identical frozen policy weights on its **own** observations.

1. **Source:** `pd_ee_delta_pose` trained policy interface.
2. **Exact/refuse:** `pd_ee_target_delta_pose` with runtime
   `_target_pose` observation, inverse source delta chart and strict
   rejection if a target-relative action requires native magnitude >1+1e-5.
3. **Bounded approximation:** identical target controller and live
   state-dependent inverse, but uses positional box projection and
   SO(3)-delta native rotation-ball projection when required target delta
   is outside the target action limits. This intervention MUST report
   every non-exact action, required amplitude and step.
4. **Direct copy:** target-delta controller receives original native
   action without execution-memory compensation.

OBS ABI: source 42-D, target 49-D with 7-D previous target pose.
The trained policy receives projected 42-D source-compatible features
(qpos/qvel followed by task extras). The 7-D memory is verified against
the *live* target controller's `get_state()['target_pose']`, retained
for executable action conversion, and NOT fed into a retrained policy.

Check and report initial observation equality after projection. On any
mismatch >5e-4, mark execution INVALID, not counted as failure/success.

## Endpoints

Primary: for all **32** held-out seed/episode pairs, show unconditional
success count per arm, exact/refuse episode count, projected approximation
episode count and total projected steps, and all seed-level outcomes.

Secondary: paired success discordant counts exact vs naive, projected vs
naive, projected vs source. Report total projection amplitudes and
step index distribution; distinguish inability to express the desired
one-step target from the actual physical task success.

**No post-hoc claim of a universal guarantee.** Approximation violates
instantaneous exactness; a successful projection does not make it an
equivalence certificate. The threshold and geometry follow the source
controller input contract, not a fitted hyperparameter.

## Reproducibility caveat

A separate repeated-reset diagnostic checks whether identical nominal
seed reproduces identical simulator initial state across repeated runs.
Until that check is resolved, 32 distinct integer seeds must be described
as **32 nominally seeded cases matched within-run**, not proven independent
identical-across-run scenes. Every paired comparison also checks initial
projected observations.

## L8/9 research gate

This is still a one-task/one-policy/one-robot pilot; stronger research
requires a nontrivial safe residual-state transport algorithm, other
families/tasks, previously unseen controller parameters and independent
maintainer or external replication. Existing action adapters, saturations
and clipping are prior art. The potential innovation is *a sound
run-time authorization and certified local approximation scope grounded
in live controller goal memory*, not the clipping primitive itself.

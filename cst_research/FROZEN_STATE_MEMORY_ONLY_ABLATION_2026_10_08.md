# Prospective memory-only ablation — frozen PPO on ManiSkill Panda

Pre-registered 2026-10-08 **before** any results of this test.
We already observed 4 development seeds and the 32-seed feasible-set
holdout [20001..20032]. Do not reuse either cohort for the primary result.

## Exact fixed independent cohort

Seeds `30001, 30002, ..., 30032` inclusive, same PickCube-v1 task,
Panda, PhysX CPU, 50-step maximum and exact immutable ActionShift PPO
checkpoint SHA256
`3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8`.
No fine-tuning, retraining, new policy checkpoint or choice of new
seeds based on observed outcomes.

All arms must check matching first-step projected **42D task/policy
observation ABI**, preserving controller-owned 7D target pose separately.
Every arm selects the PPO action from its own current environment state.

## Five arms (only paired memory access is main comparison)

A. Source `pd_ee_delta_pose` PPO.
B. Target `pd_ee_target_delta_pose` with **live previous-target
   memory**, source-action→target-delta composition and feasible-set
   clipping/projection (non-exact actions explicitly counted).
C. Target `pd_ee_target_delta_pose` with **NO previous-target memory
   read**, instead replacing it by target's current achieved EE pose;
   apply the **same exact math, rotation conventions and same** 
   feasible-set clipping/projection as B.
D. Target with **exact-only** stateful conversion, refusing any
   nonrepresentable native action.
E. Target receiving direct raw PPO actions, no conversion.

Compared with prior 32-seed run: only new B↔C memory-only ablation is
new. Other arms provide context and need all 32 raw outcomes.

## Analysis frozen before observing data

- Primary: paired task success_count B vs C, fraction over **all 32**,
  the discordant pair identities and failure examples.
- Report B vs A and C vs A separately to track policy competence.
- Secondary: source/target task steps, per-arm number of projected
  actions, their required normalized amplitudes, per-seed refusals,
  and exact first-step observation ABI identity.
- No cherry-picked subset on source successes. If C matches B, the
  added live memory has **no measured task-success advantage** in this
  fixed setting and that is the conclusion.
- This is a second **exploratory, test-set reuse-aware** holdout within
  one task/policy. It is not independent third-party validation.
- Memory-aware projection and bounded projection may be standard
  mechanisms. This empirical test alone is not proof of new theory.

## Failure disclosure

A controller error, mismatch, missing memory, ABI mismatch or
unsupported mode must be recorded as invalid execution, not silently
counted as task failure. Any data repair changes the protocol and
requires new predeclared seeds.

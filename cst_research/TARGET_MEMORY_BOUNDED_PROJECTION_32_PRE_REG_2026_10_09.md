# CST stateful target-memory / feasible-action experiment — prospective pilot

**Created before launching the 32-seed validation.** Do not merge results with
the development seeds 42, 270, 429, 2026 or the earlier ordinary delta-to-
absolute controller-swap holdout 10001–10032.

## A priori experiment

- Task: official PickCube-v1 Panda / ManiSkill v3 / PhysX CPU; one public
  frozen third-party ActionShift PPO checkpoint
  `kattri15/actionshift-baselines/ppo/pick_cube_final_ckpt.pt`,
  SHA256 `3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8`.
- **New exact requested seeds:** every integer **20001 through 20032**
  inclusive, without substitution; max 50 steps per episode, no training.
- Four separate environments per seed, initialized with the same requested
  seed and verifying projected source-policy 42D observation compatibility:
  1. Source PPO + achieved-relative `pd_ee_delta_pose`.
  2. Target with previous-target-memory adapter and **strict refusal**
     whenever the action cannot be represented in `pd_ee_target_delta_pose`.
  3. Identical memory-aware target adapter but with **bounded approximate
     projection** of infeasible normalized translation into the unit box
     and rotation vector into the unit ball. Log each approximate step;
     never call its physical execution exactly equivalent.
  4. Naive raw PPO output copied into the target-delta controller.
- All arms infer on their **own** 42D policy-compatible observations. The
  extra 7D target-controller memory is kept outside the policy input,
  only used by the adapter; compare initial policy observations and
  invalidate unmatched cases.
- Record initial 42D observation fingerprint per seed, each arm's success,
  actual step count, strict refusals, approximate action events, requested
  native amplitude and failure conditions.
- The original 4-development-seed pilot produced source 4/4, strict
  2/4, bounded approximate 4/4, naive 1/4. This influenced selecting
  bounded approximation, so the 32 new seeds are a **prospective
  validation pilot**, not an unbiased selection of that algorithm
  among multiple alternatives.

## Frozen analysis rules

Primary: unconditional 32-seed per-arm success counts, paired difference
(projected minus strict), and number of episodes invoking non-exact
projection. Strict-refused episodes are failures to complete the task,
**not** incorrect controller outcomes; report refusal counts separately.
Also report the naive arm even if it succeeds.

Secondary: magnitudes of demanded amplitudes (including >1),
per-seed results, number of approximation events, and episode steps
conditional on task success. A seed with invalid initial observation
comparison or execution errors is **invalid** and explicitly reported,
not silently excluded or counted as 0%.

**Caution on reproducibility:** an earlier separate 10014 diagnostic
re-execution changed task outcomes despite the same requested integer
seed. A dedicated initial state / execution-order fingerprint audit is
under way. Until it resolves, do NOT describe these seeds as
cross-run identical physical initial states solely because integers
match. Interpret results as one reproducible *run artifact* with
actual scene fingerprints, not a demonstrated exactly replayable
sequence across processes.

## Novelty boundary

Nearest-neighbor bounded action projection, generic frozen-policy
retargeting and rejecting infeasible actions are not novel by
themselves. The research hypothesis requires explicit **controller-
owned previous goal memory**, runtime observation-ABI projection,
an executable feasibility/refusal contract, and empirical
non-exact fallback transparency. Only stronger cross-task and
cross-controller evidence and third-party review can support a major
publication claim.

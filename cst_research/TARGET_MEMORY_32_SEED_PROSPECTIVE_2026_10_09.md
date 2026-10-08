# CST target-memory + bounded feasibility: prospective 32-seed pilot

Protocol committed **before running** the dedicated 32-seed experiment.
Previous developmental outcomes for seeds 42,270,429,2026 are known:
source 4/4, strict memory 2/4 (two valid refusals), bounded-memory 4/4
(two documented approximate steps), naive 1/4.
Those four development seeds must **never be included** in these numbers.

## Prespecified seeds and intervention

**All 32 integer seeds 20001 through 20032**, fixed in numeric order.
One public externally trained PPO checkpoint:
`kattri15/actionshift-baselines/ppo/pick_cube_final_ckpt.pt`
SHA256 `3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8`.
Weights never trained/fine-tuned/modified. Official ManiSkill Panda
PickCube-v1, `obs_mode=state`, PhysX CPU. Max 50 steps, every run logged.
Independent closed-loop inference on each environment's OWN observation,
explicitly projecting target's 49D state (42D trained-policy ABI plus 7D
controller-owned target-pose memory) into the 42D original policy ABI,
without throwing away task state.

Four simultaneously run, equally initialized controllers:

1. **Source**: learned PPO on its original `pd_ee_delta_pose`.
2. **Strict**: `pd_ee_target_delta_pose`, runtime previous-goal read,
   exact inverse command only if representable; otherwise STOP/REFUSE.
3. **Bounded approximation**: same runtime goal memory and inverse;
   if unrepresentable, project normalized position onto [-1,1]^3 and
   orientation vector onto Euclidean unit ball; log every non-exact
   execution, required amplitude and seed. No silent success certificate.
4. **Naive**: raw frozen PPO commands on `pd_ee_target_delta_pose`
   with no goal-memory translation.

For every seed: assert initial source and target observation equivalence
after *validated* removal of the controller 7D target pose; if not,
declare invalid, never score as task failure. All completed success flags
come from the actual ManiSkill PickCube task oracle.

## Fixed reporting metrics

- Four unconditional success fractions out of all **32** scheduled seeds,
  with per-seed success/failure/invalid status.
- Paired bounded-minus-strict, bounded-minus-naive, bounded-minus-source
  success differences, including discordant successes and failures.
- Strict refusal count; exact episode/step/cause and original normalized
  required-action amplitude. The strict refused episode is NOT success.
- Number of bounded, non-exact projected actions and fraction of episodes
  relying on them. Any bounded success with projection is NOT an
  exact-trace preservation certificate.
- Missing/aborted CI: INVALID, do not turn into 0 task successes.
- Record first-completion step and censor failures at 50.
- All results remain published even if source transfer fails.

**Do not include previously observed 4 development seeds.**
No hyperparameter choices based on unseen pilot labels; the projection
operation is the same previously tested implementation.

This is still a single-policy single-task CPU pilot with known action
interfaces and not independent replication, automatic contract inference
or robotic safety. Background work on adapting frozen policies to
different action interfaces including ActionShift must be acknowledged.

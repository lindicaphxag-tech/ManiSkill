# Prospective 48-seed frozen-PPO target-memory feasibility pilot

Created **before** observing outcomes for the new seed set. This is a
single-task development holdout, not independent peer-review confirmation.

## Fixed design

- Public frozen third-party PPO checkpoint: `kattri15/actionshift-baselines`,
  `ppo/pick_cube_final_ckpt.pt`, SHA256
  `3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8`.
- No policy training, fine-tuning, value-function adaptation or changed
  checkpoint. True ManiSkill 3 PickCube-v1, Panda, PhysX CPU.
- The 48 *new* seeds are **20001 through 20048 inclusive**. Neither the
  prior four development seeds nor the delta-to-absolute pilot seeds
  10001..10032 may enter this denominator.
- Max 50 steps/episode, every seed included with original outcome.
- Same-policy inference on the environment's own observation, projecting
  the target controller's 49D proprioception back to the *exact* trained
  42D policy ABI by validated removal of the 7D goal-memory field;
  the seven hidden goal-memory dimensions remain readable only by
  runtime controller interface, not injected as PPO inputs.
- For each seed create four independent, identically seeded environments:
  1. Source: achieved-relative `pd_ee_delta_pose`.
  2. Strict: target-relative `pd_ee_target_delta_pose`, reads runtime
     `_target_pose`, decodes source physical EE desired pose, inverts into
     target-native action; refuses if required normalized amplitude > 1
     (beyond 1e-5 tolerance).
  3. Feasibility-limited: same memory-aware mapping but when the exact
     target is out of native representable bounds, apply **an explicitly
     NON-EXACT** command projected to axiswise position bounds and an
     orientation unit ball. Report every such intervention. No claim of
     exact trajectory equivalence after projection.
  4. Direct-copy: target-relative controller directly receives original
     pretrained policy action after observation projection.

## Frozen reporting / outcome ledger

For all 48 seeds, log source/strict/projected/direct-copy success_once,
elapsed steps, any strict refusal reason and first time, every projected
action's original maximum normalized amplitude. Verify initial projected
observations match source (<5e-4) or mark experiment invalid.

Report unconditional success fractions in all four arms and paired
discordant outcomes. Source incompetence and approximate-path failures
must be retained. Main comparison:
`projected vs strict`, with source and naive reference.

**Important scientific honesty**:
- 4-seed initial trial (4/4 projected, 2/4 strict, 1/4 naive) was used
  to choose the specific bounded-projection method, so it is development
  evidence. This 48-seed run is a new pilot holdout.
- Projection onto native action limits is a standard/simple baseline,
  not a novel optimization algorithm. The research novelty hypothesis
  concerns the controller-owned goal-state transport, observation-ABI
  reconciliation, and explicit executability/refusal boundary.
- The reference checkpoint is external intellectual property; cite
  ActionShift. No hardware, no universal robotics safety, and no
  cross-task transfer are evaluated here.
- Do not add/remove seeds after seeing outcomes. A separate lockbox
  replication or broader controller/task testing is mandatory before
  strong paper claims.

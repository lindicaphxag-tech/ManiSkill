# PushCube frozen PPO stateful controller transport — preregistered second-task pilot

Filed before any PushCube 32-seed target-memory results are observed.

## Prediction and task separation

**Do not train a new policy.** Instead use the *different* public,
task-specific PushCube-v1 PPO checkpoint released by ActionShift, checksum
`a4a02198b309e73cb877959079023d967d5f63ec78380de9703a10c9efafc0cf`,
file `ppo/push_cube_final_ckpt.pt`. This checkpoint is *independent third-party
work*, not a novel policy by this project.

The previous frozen-policy stateful transport test used PickCube-v1
and the separate checksum beginning `3e6c95d6`. Here evaluate the
different PushCube-v1 manipulation task, robot still Panda, control
still ManiSkill PhysX CPU. This tests task/general-policy portability,
**not** robot/controller-family portability.

## Prospective cohort

Fixed ordered 32 seeds: **30001,30002,...,30032**, not used in prior runs.
Four modes for each same initial task seed, each with frozen PPO inference
on its own current *compatible* observation:
1. Source: `pd_ee_delta_pose`, achieved-relative.
2. Exact live goal-memory translation into `pd_ee_target_delta_pose`
   with refusal when target next action is out of representable bounds.
3. Feasibility-bounded nonexact one-step native delta projection using
   the same controller-owned previous target state, record every time it
   clips/limits an action.
4. Raw native action into `pd_ee_target_delta_pose` after required
   policy-observation adaptation, deliberately ignores target history.

Policy observation ABI may differ between PickCube and PushCube:
derive original input width from checkpoint-compatible source env,
validate destination width is exactly original + 7; verify controller
target memory equals the observed 7D slice at the exact agent
qpos+qvel offset, remove *only that slice*, retain task extra state.
No generic blindly truncating 7 last dimensions.

MAX_STEPS=50 (task may require longer horizon; capture and report shortfall
rather than changing a measured denominator). Report unconditional success
counts and actual episode length, exact-refusal count, projected steps,
max required action amplitude, all failed and invalid states, and full
weights/checkpoint identity. If source is not competent on >half episodes,
the experiment is a checkpoint-horizon mismatch and does not support
a cross-task success claim.

This is a 32-seed exploratory pilot, not a statistical safety proof,
formal bisimulation, hardware, independent adoption, or an original claim
to the known concept of action saturation. The *new* scientific hypothesis
is executable state/observation transport with explicit feasibility
boundary between controllers while reusing a frozen learned policy.

Controls fixed before outcome inspection; no cherry-picked seed changes,
fine-tuning, per-seed controller gains, or post-hoc horizon extension.

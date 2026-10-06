# LeRobot #3312 ACT Relative-Action Upstream Candidate

External issue: https://github.com/huggingface/lerobot/issues/3312

Maintainer `pkooij` explicitly replied that relative actions were implemented
for pi0/pi05 and invited an ACT integration PR.

## Current-main audit

Current LeRobot already contains the hard part of the fix:

- `RelativeActionsProcessorStep` can hold an anchor while a policy queue is in flight;
- `bind_relative_anchor(policy, preprocessor)` binds that hold to
  `policy.count_queued_actions`;
- production rollout/eval paths call the binder.

The remaining ACT-specific gap is narrower:

- `ACTConfig` does not expose relative-action settings;
- `make_act_pre_post_processors` only builds the default normalize /
  unnormalize pipeline.

## Candidate upstream change

Exactly two production files plus one focused regression:

1. `configuration_act.py`
   - add `use_relative_actions=False`;
   - `relative_exclude_joints=["gripper"]`;
   - `action_feature_names=None`.

2. `processor_act.py`
   - default path remains unchanged when disabled;
   - enabled path uses:
     `raw -> relative -> normalize -> ACT -> unnormalize -> absolute`;
   - reuses the existing shared `RelativeActionsProcessorStep`,
     `AbsoluteActionsProcessorStep`, and queue-anchor binding.

3. focused test
   - default ACT processor layout unchanged;
   - training conversion happens before normalization;
   - gripper remains absolute;
   - a real ACTPolicy action queue holds the original chunk anchor while queued
     actions drain and re-anchors only after the queue becomes empty.

No new queue state machine is introduced. This is deliberately an ACT wiring PR
around existing LeRobot infrastructure.

## Status boundary

This candidate is being validated against a pinned current LeRobot commit from a
separate public CI because the user's GitHub installation currently has no
LeRobot fork. It is not an upstream PR or adoption until a fork exists and the
patch is submitted/accepted.

# Suggested upstream PR

**Title**

`feat(act): support relative actions through shared processor pipeline`

**Body**

## Summary

Add opt-in relative-action support to ACT by reusing LeRobot's existing
`RelativeActionsProcessorStep` / `AbsoluteActionsProcessorStep` pair.

This addresses the ACT gap discussed in #3312. The issue notes that relative
actions are currently available for Pi0/Pi0.5 and explicitly welcomes an ACT
integration.

## Scope

The change is intentionally small:

- add the standard relative-action fields to `ACTConfig`;
- when `use_relative_actions=True`, place the existing relative step before
  normalization and the paired absolute step after unnormalization;
- add a CPU regression covering processor order, excluded gripper semantics,
  and exact relative→absolute round trip.

The default ACT processor path is unchanged when
`use_relative_actions=False`.

## Semantics

The pipeline is:

```text
absolute dataset action
  -> relative to observation.state
  -> normalize
  -> ACT
  -> unnormalize
  -> absolute using the cached generation-time state
```

No new relative-action math is introduced.

The shared relative processor already implements action-chunk anchor lifetime.
Production eval/rollout code calls `bind_relative_anchor(policy, preprocessor)`,
so one predicted ACT chunk keeps the state anchor that generated it until the
queue drains rather than re-anchoring later actions to newer observations.

## Excluded joints

`relative_exclude_joints` and `action_feature_names` use the same mechanism
as Pi0. The generic `make_policy` path already populates
`action_feature_names` from dataset metadata.

## Validation

Targeted validation is frozen against LeRobot commit:

`d40e8709cffb93644db66e30604ef50fdec003cb`

The handoff CI performs:

```bash
git apply --check lerobot_act_relative_actions.patch
git apply lerobot_act_relative_actions.patch
git diff --check
python -m pytest -q tests/processor/test_act_processor.py --tb=short
```

No model weights, rollout engine, queue implementation, or shared relative
processor are changed.

Fixes / advances #3312.

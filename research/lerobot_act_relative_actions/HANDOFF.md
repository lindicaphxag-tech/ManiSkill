# LeRobot ACT relative-action support — upstream handoff

Target issue: huggingface/lerobot#3312

Pinned source used for validation:

- repository: huggingface/lerobot
- commit: `d40e8709cffb93644db66e30604ef50fdec003cb`
- files changed by the proposed patch:
  - `src/lerobot/policies/act/configuration_act.py`
  - `src/lerobot/policies/act/processor_act.py`
  - `tests/processor/test_act_processor.py`

## Why this patch is deliberately small

Current LeRobot already owns the semantics we need:

- `RelativeActionsProcessorStep`: absolute -> state-relative action conversion;
- `AbsoluteActionsProcessorStep`: inverse conversion at inference;
- chunk-anchor lifetime support through the existing relative-action processor;
- relative-action dataset-stat plumbing in `lerobot_train.py`;
- dataset action-name population in the generic policy factory.

ACT currently bypasses this stack by calling only
`make_default_pre_post_processors`.

The proposed change therefore does **not** introduce a new action convention.
It only opts ACT into the existing LeRobot convention:

```text
training:
absolute action -> relative-to-current-state -> normalize -> ACT

inference:
ACT -> unnormalize -> add captured chunk anchor -> absolute action
```

Default ACT behavior is byte-for-byte structurally unchanged when
`use_relative_actions=False`.

## Review boundary

The patch intentionally does not:

- add delta/sequential-difference semantics;
- change ACT architecture or loss;
- change existing absolute-action checkpoints;
- invent a second anchor implementation;
- modify generic relative-action processors.

## Proposed upstream title

`feat(act): support state-relative action chunks`

## Acceptance tests

1. existing ACT processor tests remain green;
2. relative mode converts arm dimensions before normalization;
3. excluded gripper dimensions remain absolute;
4. postprocessing reconstructs the original absolute action;
5. default mode contains no relative/absolute conversion steps.

External adoption credit remains zero until this is actually submitted and
retained by huggingface/lerobot.

# LeRobot upstream PR #3312 — ready-to-submit body

**Compare (manual upstream PR):**
https://github.com/huggingface/lerobot/compare/main...lindicaphxag-tech:lerobot:fix/act-relative-action-support-final-pr?expand=1

**Suggested title:** feat(act): support relative actions

## Summary
LeRobot issue #3312 requests ACT relative actions. Maintainer `pkooij`
confirmed support was available only for pi0/pi05 and invited an ACT PR.

- Adds opt-in `ACTConfig.use_relative_actions`, with explicit runtime
  action dimension names and excluded-joint configuration.
- Places shared relative-action processing before normalization, and
  absolute reconstruction after denormalization.
- Reuses the common per-chunk anchor lifecycle: queued ACT actions
  retain the state at which their chunk was produced rather than
  accidentally reanchoring to a later observation.
- Preserves absolute treatment of excluded dimensions such as grippers.
- Adds ACT-focused tests and documentation.

By default `use_relative_actions=False`, preserving the existing ACT
processor behavior.

## Validation
- **8 passed, 5 skipped** in focused ACT tests on the exact final
  submitted file contents:
  https://github.com/lindicaphxag-tech/lerobot/actions/runs/37688063579
- ruff, ruff-format, typos, pyupgrade, prettier, bandit and mypy all pass.
- This is processor/anchor correctness evidence, not an end-to-end
  hardware rollout or learned policy success-rate comparison.

## Community review requirement
Before requesting maintainer attention, perform one genuine code review of
another contributor's open PR, as required by LeRobot's community policy.
The previously audited candidate was
https://github.com/huggingface/lerobot/pull/4871
but **a review has not been submitted** through the connector.

## Significant AI-assistance disclosure
Significant AI assistance was used to inspect the existing processor stack,
draft implementation/tests and audit edge cases. The code and tests were
reviewed and validated against current LeRobot source, focused tests,
formatting, static analysis and security checks.

Closes #3312.

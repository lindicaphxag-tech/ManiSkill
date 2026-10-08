# robomimic upstream PR #270 — ready-to-submit body

**Compare (manual upstream PR):**
https://github.com/ARISE-Initiative/robomimic/compare/master...lindicaphxag-tech:robomimic:fix/add-delta-actions-converter-pr?expand=1

**Suggested title:** Add absolute-to-delta robosuite OSC action conversion

## Summary
Implements the inverse operation requested in #270, where maintainer
`amandlek` said the feature would be welcome.

- Adds a controller-semantic `RobomimicDeltaActionConverter`, mirroring
  the existing delta-to-absolute script.
- Restores each recorded simulator state; computes the relative OSC goal in
  the controller's reference frame; recovers the correct orientation through
  `R_delta = R_goal @ R_achieved.T`; inverts native action scaling.
- Preserves gripper/base remainder, exposes saturation when the absolute goal
  cannot be represented by the configured delta-action limits, and explicitly
  rejects unsupported hidden goal-update state.
- Wires `--add_delta_actions` into `convert_robosuite.py` and fixes
  `action_dict` to label source absolute and generated delta fields correctly.

## Validation
- Focused lightweight tests: **4 passed** covering scaling, SO(3),
  clipping and a noncommuting orientation case.
- Real Panda/Lift robosuite OSC goal comparison using
  robosuite 1.5.2/MuJoCo 3.3.0: **passed**.
- Separate public validation experiment (not included in the small PR):
  https://github.com/lindicaphxag-tech/robomimic/actions/runs/37706956215
  – **8/8 passed** on real OSC objects, synthetic HDF5
  `convert_demo`, controller-state interventions and matched-MJCF
  closed-loop numerical comparisons.
- The HDF5 integration test uses a programmatically generated demo
  and isolates heavy metadata initialization; it is **not** a proof that
  all external robomimic datasets or the complete CLI work unchanged.

## Scope / limitations
Supports fixed-impedance OSC pose actions, with strict refusal for
unsupported previous-target dependence. It does not promise all
controller pairs can be converted exactly, and it does not assert
universal success-rate preservation.

## AI assistance
Significant AI assistance was used to analyze controller semantics and
draft parts of the patch/tests; the resulting code was checked against
actual robosuite source and public CI. Maintainer feedback is welcome.

Closes #270.

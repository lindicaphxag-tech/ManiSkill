# CST Claim–Evidence Matrix

Frozen purpose: separate controller-semantic claims from task / plant claims.

| ID | Claim | Status | Public evidence / promotion rule |
|---|---|---|---|
| C1 | ManiSkill `pd_joint_delta_pos -> pd_joint_pos` has a reproducible controller-semantic defect on the upstream base used by the patch. | **supported** | Clean branch regression is base-fail / fix-pass in fork CI. The upstream patch branch contains only production code + focused regression after removing the temporary workflow. |
| C2 | CST's PD-joint Trace IR matches ManiSkill `PDJointPosController` command semantics. | **supported** | Pinned host-parity job covers absolute, current-delta, target-delta, interpolation on/off, and normalized clipping. |
| C3 | CST is not specific to ManiSkill's controller implementation. | **supported at host-semantic level** | Independent pinned robosuite `JointPositionController` parity covers delta/absolute goal semantics and real qpos clipping. |
| C4 | Endpoint-goal equality is weaker than full controller-command trace equality. | **supported** | Deterministic GOAL_ONLY construction with a non-zero substep drive-target mismatch. |
| C5 | For affine controller regions, one analytic morphism can certify the entire source action box. | **supported** | Global morphism verifies semantic-map / offset identities and exact affine target-box bounds; randomized samples are secondary checks. |
| C6 | Controller state can be required for a correct transport. | **supported in modeled family** | Current-relative and target-relative delta modes compile through distinct measured-state / hidden-reference channels. |
| C7 | Piecewise controller boundaries can be compiled rather than hidden by one affine approximation. | **supported for coordinate clipping** | Robosuite qpos clipping is represented as an exact piecewise-affine partition and matches the host across 2000 random action/state samples including saturation. |
| C8 | CST can emit constructive witnesses when an exact semantic morphism does not exist or is non-unique. | **pending latest CI** | New witness code returns a source direction outside the target image plus source/target nullspace witnesses. Promote only after the branch workflow passes. |
| C9 | CST-preserving conversion preserves full physical robot trajectories or task success. | **unproven** | Requires exact simulator-state source/target replay on public demonstrations. Controller-command equivalence alone is insufficient. |
| C10 | CST handles arbitrary nonlinear IK/task-space controllers exactly. | **unproven** | Needs branch-aware / region-aware nonlinear certificates; current affine and piecewise-affine results do not imply this. |
| C11 | A maintainer has retained CST or the #429 semantic fix upstream. | **false currently** | External PR creation is blocked by the current GitHub App permission. Promotion requires upstream review/merge or independent maintained use. |
| C12 | CST is a cheaper or universally better action representation. | **not claimed** | CST decides semantic transportability; it does not claim one action representation is globally superior. |

## Non-negotiable promotion rules

- C1 becomes external adoption only after the production patch is accepted or
  positively reviewed upstream; fork CI is not adoption.
- C3 is a second implementation family, not a second task-success result.
- C8 requires machine-checked witnesses: substituting the returned vectors must
  numerically reproduce image-exclusion or nullspace properties.
- C9 requires public task-level replay with frozen source trajectories,
  controller configs, seeds / simulator-state protocol, and explicit
  success/failure accounting.
- A negative result remains evidence. No tolerance, controller semantics, or
  evaluation subset may be changed after outcome inspection without a version
  change.

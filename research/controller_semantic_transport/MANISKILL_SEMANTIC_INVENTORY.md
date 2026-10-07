# ManiSkill controller semantic inventory — CST v0

This inventory is conservative: implementation inheritance is not treated as semantic substitutability.

| Controller | Physical goal space | Update mode | Hidden state | Frame / parameterization | Exact CST family? |
| --- | --- | --- | --- | --- | --- |
| PDJointPosController (absolute) | joint position | absolute | none | joint coordinates / qpos | yes |
| PDJointPosController (delta, use_target=false) | joint position | delta-current | current_qpos | joint coordinates / qpos | yes, stateful |
| PDJointPosController (delta, use_target=true) | joint position | delta-target | target_qpos | joint coordinates / qpos | yes, stateful |
| PDJointVelController | joint velocity | absolute | none | joint coordinates / qvel | no; approximate/dynamics contract required |
| PDEEPosController | Cartesian position | absolute or delta | current_pose or target_pose for delta | configured root/body frame / xyz | no direct joint-family exact authority |
| PDEEPoseController | Cartesian pose | absolute or delta | current_pose or target_pose for delta | configured root/body frame / xyz Euler | no direct joint-family exact authority |

## Important inheritance trap

PDEEPosController inherits from PDJointPosController in ManiSkill for implementation reuse. PDEEPoseController in turn inherits from PDEEPosController.

Therefore a Python check such as isinstance(controller, PDJointPosController) is not a valid semantic classifier. CST checks the most-specific controller type first and the exact joint-position chart adapter rejects subclasses by default.

This is an example of the general CST thesis: software type compatibility and tensor-shape compatibility do not imply control-semantic compatibility.

## Promotion boundary

This inventory is source-level semantic analysis, not evidence that all listed approximate conversions fail in practice. Exact/approximate labels grant or withhold proof authority; task-level behavior must still be measured under public replay protocols.

from __future__ import annotations

import numpy as np

from mani_skill.agents.controllers import (
    PDEEPosController,
    PDEEPoseController,
    PDJointPosController,
    PDJointVelController,
)

from .core import ControllerState, JointPositionChart


def chart_from_maniskill_joint_position_controller(
    controller: PDJointPosController,
) -> JointPositionChart:
    """Compile a ManiSkill PDJointPosController into a CST native-action chart."""
    if type(controller) is not PDJointPosController:
        raise TypeError(
            "exact joint-position CST adapter requires a concrete "
            "PDJointPosController; EE/IK and mimic subclasses have different "
            "physical semantics and are intentionally rejected"
        )

    if controller.config.use_delta:
        mode = "delta_target" if controller.config.use_target else "delta_current"
    else:
        mode = "absolute"

    if controller.config.normalize_action:
        lower = controller.action_space_low.detach().cpu().numpy()
        upper = controller.action_space_high.detach().cpu().numpy()
    else:
        lower = np.asarray(controller.single_action_space.low, dtype=float)
        upper = np.asarray(controller.single_action_space.high, dtype=float)

    return JointPositionChart(
        mode=mode,
        lower=np.asarray(lower, dtype=float),
        upper=np.asarray(upper, dtype=float),
        normalized=bool(controller.config.normalize_action),
    )


def state_from_maniskill_joint_position_controller(
    controller: PDJointPosController,
    *,
    env_index: int = 0,
) -> ControllerState:
    """Extract the hidden state needed to interpret one native controller action."""
    if type(controller) is not PDJointPosController:
        raise TypeError(
            "exact joint-position CST state extraction requires a concrete "
            "PDJointPosController"
        )
    current = controller.qpos.detach().cpu().numpy()[env_index].copy()
    target = None
    if controller.config.use_target:
        target = controller._target_qpos.detach().cpu().numpy()[env_index].copy()
    return ControllerState(current_qpos=current, target_qpos=target)


def semantic_type_from_maniskill_controller(controller):
    """Infer a conservative CST semantic type from a ManiSkill controller.

    Most-specific subclasses are checked first because ManiSkill's Cartesian
    EE controllers inherit from PDJointPosController for implementation reuse.
    Python inheritance therefore does not imply semantic substitutability.
    """
    from .semantic_types import (
        ControllerSemanticType,
        joint_position_semantic_type,
    )

    interpolation = (
        "linear" if bool(getattr(controller.config, "interpolate", False)) else "none"
    )

    if isinstance(controller, PDEEPoseController):
        hidden = (
            frozenset({"target_pose"})
            if controller.config.use_target
            else frozenset({"current_pose"})
        )
        return ControllerSemanticType(
            goal_space="cartesian_pose",
            update_mode=(
                "delta_target"
                if controller.config.use_delta and controller.config.use_target
                else "delta_current"
                if controller.config.use_delta
                else "absolute"
            ),
            frame=str(controller.config.frame),
            parameterization="xyz_euler",
            hidden_state=hidden if controller.config.use_delta else frozenset(),
            interpolation=interpolation,
            actuator_semantics="ik_to_joint_pd",
        )

    if isinstance(controller, PDEEPosController):
        hidden = (
            frozenset({"target_pose"})
            if controller.config.use_target
            else frozenset({"current_pose"})
        )
        return ControllerSemanticType(
            goal_space="cartesian_position",
            update_mode=(
                "delta_target"
                if controller.config.use_delta and controller.config.use_target
                else "delta_current"
                if controller.config.use_delta
                else "absolute"
            ),
            frame=str(controller.config.frame),
            parameterization="xyz",
            hidden_state=hidden if controller.config.use_delta else frozenset(),
            interpolation=interpolation,
            actuator_semantics="ik_to_joint_pd",
        )

    if type(controller) is PDJointPosController:
        mode = (
            "delta_target"
            if controller.config.use_delta and controller.config.use_target
            else "delta_current"
            if controller.config.use_delta
            else "absolute"
        )
        return joint_position_semantic_type(
            update_mode=mode,
            normalized=bool(controller.config.normalize_action),
            interpolation=interpolation,
            actuator_semantics="pd_joint_position",
        )

    if isinstance(controller, PDJointVelController):
        return ControllerSemanticType(
            goal_space="joint_velocity",
            update_mode="absolute",
            frame="joint_coordinates",
            parameterization="qvel",
            hidden_state=frozenset(),
            interpolation="none",
            actuator_semantics="pd_joint_velocity",
        )

    raise TypeError(
        f"no conservative CST semantic type registered for {type(controller).__name__}"
    )

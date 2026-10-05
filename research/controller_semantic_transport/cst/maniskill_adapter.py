from __future__ import annotations

import numpy as np

from mani_skill.agents.controllers import PDJointPosController

from .core import ControllerState, JointPositionChart


def chart_from_maniskill_joint_position_controller(
    controller: PDJointPosController,
) -> JointPositionChart:
    """Compile a ManiSkill PDJointPosController into a CST native-action chart."""
    if not isinstance(controller, PDJointPosController):
        raise TypeError("controller must be a ManiSkill PDJointPosController")

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
    if not isinstance(controller, PDJointPosController):
        raise TypeError("controller must be a ManiSkill PDJointPosController")
    current = controller.qpos.detach().cpu().numpy()[env_index].copy()
    target = None
    if controller.config.use_target:
        target = controller._target_qpos.detach().cpu().numpy()[env_index].copy()
    return ControllerState(current_qpos=current, target_qpos=target)

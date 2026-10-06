"""Utilities to convert actions between different control modes. Note that this code is specifically designed for the Franka Panda robot arm, it is not guaranteed to work for other robots."""
from typing import Union

import numpy as np
import sapien
import torch
from tqdm.auto import tqdm

from mani_skill.agents.controllers import (
    PDEEPosController,
    PDEEPoseController,
    PDJointPosController,
    PDJointVelController,
)
from mani_skill.agents.controllers.base_controller import CombinedController
from mani_skill.envs.sapien_env import BaseEnv
from mani_skill.utils import common, gym_utils
from mani_skill.utils.geometry import rotation_conversions
from mani_skill.utils.structs.link import Link
from mani_skill.utils.structs.pose import Pose


def qpos_to_pd_joint_delta_pos(controller: PDJointPosController, qpos):
    assert type(controller) == PDJointPosController
    assert controller.config.use_delta
    assert controller.config.normalize_action
    delta_qpos = qpos - controller.qpos.cpu().numpy()[0]
    low, high = controller.config.lower, controller.config.upper
    return gym_utils.inv_scale_action(delta_qpos, low, high)


def qpos_to_pd_joint_target_delta_pos(controller: PDJointPosController, qpos):
    assert type(controller) == PDJointPosController
    assert controller.config.use_delta
    assert controller.config.use_target
    assert controller.config.normalize_action
    delta_qpos = qpos - controller._target_qpos.cpu().numpy()[0]
    low, high = controller.config.lower, controller.config.upper
    return gym_utils.inv_scale_action(delta_qpos, low, high)


def qpos_to_pd_joint_vel(controller: PDJointVelController, qpos):
    assert type(controller) == PDJointVelController
    assert controller.config.normalize_action
    delta_qpos = qpos - controller.qpos.cpu().numpy()[0]
    qvel = delta_qpos * controller._control_freq
    low, high = controller.config.lower, controller.config.upper
    return gym_utils.inv_scale_action(qvel, low, high)


def euler_xyz_from_quaternion(quat: np.ndarray) -> np.ndarray:
    """Convert a quaternion to the XYZ Euler convention used by PDEEPoseController."""
    quat = torch.as_tensor(quat)
    matrix = rotation_conversions.quaternion_to_matrix(quat)
    return rotation_conversions.matrix_to_euler_angles(matrix, "XYZ").cpu().numpy()


def inverse_delta_to_pd_ee_euler(quat: np.ndarray) -> np.ndarray:
    """Convert the converter's inverse relative quaternion to desired XYZ Euler."""
    quat = torch.as_tensor(quat)
    desired_delta = rotation_conversions.quaternion_invert(quat)
    return euler_xyz_from_quaternion(desired_delta.numpy())


def _pd_ee_rotation_gains(controller: PDEEPoseController) -> torch.Tensor:
    """Probe the controller's actual normalized rotation mapping."""
    if not isinstance(controller, PDEEPoseController):
        raise TypeError("rotation conversion requires PDEEPoseController")

    dtype = controller.action_space_low.dtype
    device = controller.action_space_low.device
    probe = torch.zeros((3, 6), dtype=dtype, device=device)
    probe[:, 3:] = torch.eye(3, dtype=dtype, device=device)
    scaled_rotation = controller._clip_and_scale_action(probe)[:, 3:]

    gains = torch.diagonal(scaled_rotation)
    off_diagonal = scaled_rotation - torch.diag(gains)
    if not torch.allclose(
        off_diagonal,
        torch.zeros_like(off_diagonal),
        atol=1e-7,
        rtol=0.0,
    ):
        raise RuntimeError("PDEEPoseController rotation mapping is not axis-separable")
    if torch.any(torch.abs(gains) <= torch.finfo(dtype).eps):
        raise RuntimeError("PDEEPoseController rotation mapping has zero gain")
    return gains


def _normalized_pd_ee_rotation_action(
    controller: PDEEPoseController, desired_euler: np.ndarray
) -> np.ndarray:
    """Invert the controller mapping when the target is directly reachable."""
    gains = _pd_ee_rotation_gains(controller)
    desired = torch.as_tensor(
        desired_euler, dtype=gains.dtype, device=gains.device
    )
    return (desired / gains).cpu().numpy()


def _bounded_pd_ee_rotation_action(
    controller: PDEEPoseController,
    desired_quaternion: np.ndarray,
    *,
    iterations: int = 64,
) -> np.ndarray:
    """Compile a desired rotation into the controller's bounded action ball.

    Reachable targets use the exact analytic inverse. Out-of-bound targets solve
    a three-dimensional constrained problem against the controller forward
    XYZ-Euler semantics: minimize SO(3) discrepancy subject to norm(a) <= 1.

    The chordal objective 3 - trace(R_a^T R_desired) is monotone in geodesic
    angle on SO(3), and projected Adam is deterministic for this fixed problem.
    """
    gains = _pd_ee_rotation_gains(controller)
    dtype = gains.dtype
    device = gains.device

    desired_q = torch.as_tensor(
        desired_quaternion, dtype=dtype, device=device
    )
    desired_q = desired_q / torch.linalg.norm(desired_q)
    desired_matrix = rotation_conversions.quaternion_to_matrix(desired_q)
    desired_euler = rotation_conversions.matrix_to_euler_angles(
        desired_matrix, "XYZ"
    )
    exact = desired_euler / gains

    exact_norm = torch.linalg.norm(exact)
    if exact_norm <= 1.0 + 1e-7:
        return exact.cpu().numpy()

    action = (exact / exact_norm).detach().clone().requires_grad_(True)
    optimizer = torch.optim.Adam([action], lr=0.08)

    best_action = action.detach().clone()
    best_loss = torch.tensor(float("inf"), dtype=dtype, device=device)

    for _ in range(iterations):
        optimizer.zero_grad()
        realized_matrix = rotation_conversions.euler_angles_to_matrix(
            action * gains, "XYZ"
        )
        loss = 3.0 - torch.trace(
            realized_matrix.transpose(-1, -2) @ desired_matrix
        )
        loss.backward()
        optimizer.step()

        with torch.no_grad():
            norm = torch.linalg.norm(action)
            if norm > 1.0:
                action.mul_(1.0 / norm)

            realized_matrix = rotation_conversions.euler_angles_to_matrix(
                action * gains, "XYZ"
            )
            candidate_loss = 3.0 - torch.trace(
                realized_matrix.transpose(-1, -2) @ desired_matrix
            )
            if candidate_loss < best_loss:
                best_loss = candidate_loss
                best_action = action.detach().clone()

    return best_action.cpu().numpy()


def delta_pose_to_pd_ee_delta(
    controller: Union[PDEEPoseController, PDEEPosController],
    delta_pose: sapien.Pose,
    pos_only=False,
):
    """
    Given a delta pose, convert it to a PDEEPose/PDEEPos Controller action
    """
    # TODO (stao): update this code to be parallelized / use GPU
    assert isinstance(controller, PDEEPosController)
    assert controller.config.use_delta
    assert controller.config.normalize_action
    low, high = controller.action_space_low, controller.action_space_high
    if pos_only:
        return gym_utils.inv_scale_action(
            delta_pose.p, low.cpu().numpy(), high.cpu().numpy()
        )
    position_action = gym_utils.inv_scale_action(
        delta_pose.p,
        low[:3].cpu().numpy(),
        high[:3].cpu().numpy(),
    )
    desired_quaternion = rotation_conversions.quaternion_invert(
        torch.as_tensor(
            delta_pose.q,
            dtype=controller.action_space_low.dtype,
            device=controller.action_space_low.device,
        )
    )
    rotation_action = _bounded_pd_ee_rotation_action(
        controller,
        desired_quaternion.cpu().numpy(),
    )
    return np.r_[position_action, rotation_action]


def from_pd_joint_pos_to_ee(
    output_mode: str,
    ori_actions,
    ori_env: BaseEnv,
    env: BaseEnv,
    render=False,
    pbar=None,
    verbose=False,
):
    n = len(ori_actions)
    if pbar is not None:
        pbar.reset(total=n)

    ori_controller: CombinedController = ori_env.unwrapped.agent.controller
    controller: CombinedController = env.unwrapped.agent.controller
    assert (
        "arm" in ori_controller.controllers
    ), "Could not find the controller for the robot arm. This controller conversion tool requires there to be a key called 'arm' in the controller"
    ori_arm_controller: PDJointPosController = ori_controller.controllers["arm"]
    arm_controller: PDEEPoseController = controller.controllers["arm"]
    assert isinstance(arm_controller, PDEEPoseController) or isinstance(
        arm_controller, PDEEPosController
    ), "the arm controller must inherit PDEEPoseController or PDEEPosController"
    assert arm_controller.config.frame in [
        "root_translation:root_aligned_body_rotation",
        "root_translation",
    ], "Currently only support the 'root_translation:root_aligned_body_rotation' ee control frame for delta pose control and 'root_translation' ee control frame for delta pos control"
    target_controller_is_delta = arm_controller.config.use_delta

    ee_link: Link = arm_controller.ee_link
    pos_only = arm_controller.config.frame == "root_translation"
    use_target = arm_controller.config.use_target == True
    pin_model = ori_controller.articulation.create_pinocchio_model()
    info = {}

    for t in range(n):
        if pbar is not None:
            pbar.update()

        ori_action = common.to_tensor(ori_actions[t], device=env.unwrapped.device)
        ori_action_dict = common.to_tensor(
            ori_controller.to_action_dict(ori_action), device=env.unwrapped.device
        )
        output_action_dict = common.to_tensor(
            ori_action_dict.copy(), device=env.unwrapped.device
        )  # do not in-place modify
        ori_env.step(ori_action)

        # NOTE (stao): for high success rate of pd joint pos to pd ee delta pos/pose control, we need to use the current target qpos of the original
        # environment controller to compute the target ee pose to try and reach. this is because if we attempt to reach the original envs ee link pose
        # we may fall short and fail.
        full_qpos = ori_controller.articulation.get_qpos()
        full_qpos[
            :, ori_arm_controller.active_joint_indices
        ] = ori_arm_controller._target_qpos
        pin_model.compute_forward_kinematics(full_qpos.cpu().numpy()[0])
        target_ee_pose_pin = Pose.create(
            ori_controller.articulation.pose.sp
            * pin_model.get_link_pose(arm_controller.ee_link.index)
        )

        flag = True
        for _ in range(4):
            if target_controller_is_delta:
                delta_q = [1, 0, 0, 0]
                if "root_translation" in arm_controller.config.frame:
                    if use_target:
                        delta_position = (
                            target_ee_pose_pin.p
                            - arm_controller._target_pose.p
                            - arm_controller.articulation.pose.p
                        )
                    else:
                        delta_position = target_ee_pose_pin.p - ee_link.pose.p
                if "root_aligned_body_rotation" in arm_controller.config.frame:
                    if use_target:
                        delta_q = (
                            arm_controller._target_pose.sp * target_ee_pose_pin.sp.inv()
                        ).q
                    else:
                        delta_q = (ee_link.pose.sp * target_ee_pose_pin.sp.inv()).q

                delta_pose = sapien.Pose(delta_position.cpu().numpy()[0], delta_q)

                arm_action = delta_pose_to_pd_ee_delta(
                    arm_controller, delta_pose, pos_only=pos_only
                )
                if (np.abs(arm_action[:3])).max() > 1:  # position clipping
                    if verbose:
                        tqdm.write(f"Position action is clipped: {arm_action[:3]}")
                    arm_action[:3] = np.clip(arm_action[:3], -1, 1)
                    flag = False
                if not pos_only:
                    if np.linalg.norm(arm_action[3:]) > 1:  # rotation clipping
                        if verbose:
                            tqdm.write(f"Rotation action is clipped: {arm_action[3:]}")
                        arm_action[3:] = arm_action[3:] / np.linalg.norm(arm_action[3:])
                        flag = False
                output_action_dict["arm"] = common.to_tensor(
                    arm_action, device=env.unwrapped.device
                )
                output_action = controller.from_action_dict(output_action_dict)
            else:
                # NOTE (stao): We convert from quaternion to matrix to euler angles since this is how the default pd ee pose controller does it
                # As far as I know this is not notably any slower than a batched version of transforms3d euler2quat.
                output_action_dict["arm"] = torch.cat(
                    [
                        common.to_tensor(
                            target_ee_pose_pin.p[0], device=env.unwrapped.device
                        ),
                        common.to_tensor(
                            rotation_conversions.matrix_to_euler_angles(
                                rotation_conversions.quaternion_to_matrix(
                                    target_ee_pose_pin.q[0]
                                ),
                                "XYZ",
                            ),
                            device=env.unwrapped.device,
                        ),
                    ]
                )
                output_action_dict["arm"][:3] -= arm_controller.articulation.pose.p[0]
                output_action = controller.from_action_dict(output_action_dict)

            _, _, _, _, info = env.step(output_action)
            if render:
                env.render_human()

            if flag:
                break
    return info


def from_pd_joint_pos(
    output_mode,
    ori_actions,
    ori_env: BaseEnv,
    env: BaseEnv,
    render=False,
    pbar=None,
    verbose=False,
):
    if "ee" in output_mode:
        return from_pd_joint_pos_to_ee(**locals())

    n = len(ori_actions)
    if pbar is not None:
        pbar.reset(total=n)

    ori_controller: CombinedController = ori_env.unwrapped.agent.controller
    controller: CombinedController = env.unwrapped.agent.controller

    info = {}

    for t in range(n):
        if pbar is not None:
            pbar.update()

        ori_action = ori_actions[t]
        ori_action_dict = ori_controller.to_action_dict(ori_action)
        output_action_dict = ori_action_dict.copy()  # do not in-place modify

        ori_env.step(ori_action)
        flag = True

        for _ in range(2):
            if output_mode == "pd_joint_delta_pos":
                arm_action = qpos_to_pd_joint_delta_pos(
                    controller.controllers["arm"], ori_action_dict["arm"]
                )
            elif output_mode == "pd_joint_target_delta_pos":
                arm_action = qpos_to_pd_joint_target_delta_pos(
                    controller.controllers["arm"], ori_action_dict["arm"]
                )
            elif output_mode == "pd_joint_vel":
                arm_action = qpos_to_pd_joint_vel(
                    controller.controllers["arm"], ori_action_dict["arm"]
                )
            else:
                raise NotImplementedError(
                    f"Does not support converting pd_joint_pos to {output_mode}"
                )

            # Assume normalized action
            if np.max(np.abs(arm_action)) > 1 + 1e-3:
                if verbose:
                    tqdm.write(f"Arm action is clipped: {arm_action}")
                flag = False
            arm_action = np.clip(arm_action, -1, 1)
            output_action_dict["arm"] = arm_action

            output_action = controller.from_action_dict(
                common.to_tensor(output_action_dict, device=env.unwrapped.device)
            )
            _, _, _, _, info = env.step(output_action)
            if render:
                env.render_human()

            if flag:
                break

    return info


def from_pd_joint_delta_pos(
    output_mode,
    ori_actions,
    ori_env: BaseEnv,
    env: BaseEnv,
    render=False,
    pbar=None,
    verbose=False,
):
    n = len(ori_actions)
    if pbar is not None:
        pbar.reset(total=n)

    ori_controller: CombinedController = ori_env.unwrapped.agent.controller
    controller: CombinedController = env.unwrapped.agent.controller
    ori_arm_controller: PDJointPosController = ori_controller.controllers["arm"]

    assert output_mode == "pd_joint_pos", output_mode
    assert ori_arm_controller.config.normalize_action
    low, high = ori_arm_controller.config.lower, ori_arm_controller.config.upper

    info = {}

    for t in range(n):
        if pbar is not None:
            pbar.update()

        ori_action = ori_actions[t]
        ori_action_dict = ori_controller.to_action_dict(ori_action)
        output_action_dict = ori_action_dict.copy()  # do not in-place modify

        prev_arm_qpos = ori_arm_controller.qpos
        delta_qpos = gym_utils.clip_and_scale_action(ori_action_dict["arm"], low, high)
        arm_action = prev_arm_qpos + delta_qpos

        ori_env.step(ori_action)

        output_action_dict["arm"] = arm_action
        output_action = controller.from_action_dict(
            common.to_tensor(output_action_dict, device=env.unwrapped.device)
        )
        _, _, _, _, info = env.step(output_action)

        if render:
            env.render_human()

    return info

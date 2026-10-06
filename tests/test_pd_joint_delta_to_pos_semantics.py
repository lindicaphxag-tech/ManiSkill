from types import SimpleNamespace

import numpy as np
import torch

from mani_skill.agents.controllers import PDJointPosController
from mani_skill.trajectory.utils.actions.conversion import from_pd_joint_delta_pos
from mani_skill.utils import gym_utils


class _Combined:
    def __init__(self, arm):
        self.controllers = {"arm": arm}

    def to_action_dict(self, action):
        # Match production CombinedController.to_action_dict: HDF5 trajectory
        # rows remain NumPy arrays here.
        return {"arm": np.asarray(action, dtype=np.float64).copy()}

    def from_action_dict(self, action_dict):
        return torch.as_tensor(action_dict["arm"], dtype=torch.float64)


class _Env:
    def __init__(self, arm):
        self.unwrapped = SimpleNamespace(
            agent=SimpleNamespace(controller=_Combined(arm)),
            device=torch.device("cpu"),
        )
        self.last_action = None

    def step(self, action):
        self.last_action = np.asarray(action, dtype=np.float64)
        return None, 0.0, False, False, {"success": True}


def _source_arm(monkeypatch):
    arm = object.__new__(PDJointPosController)
    source_low = np.array([-0.1, -0.2], dtype=np.float64)
    source_high = np.array([0.1, 0.2], dtype=np.float64)
    arm.config = SimpleNamespace(
        use_delta=True,
        normalize_action=True,
        lower=source_low,
        upper=source_high,
    )
    # Physical delta-q action box saved by BaseController before normalization.
    arm.action_space_low = torch.tensor(source_low, dtype=torch.float64)
    arm.action_space_high = torch.tensor(source_high, dtype=torch.float64)
    qpos = torch.tensor([[0.2, -0.3]], dtype=torch.float64)

    original_qpos = PDJointPosController.qpos

    def fake_qpos(self):
        if self is arm:
            return qpos
        return original_qpos.fget(self)

    monkeypatch.setattr(PDJointPosController, "qpos", property(fake_qpos))
    return arm


def _target_arm():
    arm = object.__new__(PDJointPosController)
    arm.config = SimpleNamespace(use_delta=False, normalize_action=True)
    # Deliberately asymmetric absolute target chart. A physical qpos cannot be
    # passed through as a native normalized action without changing semantics.
    arm.action_space_low = torch.tensor([-2.0, -1.0], dtype=torch.float64)
    arm.action_space_high = torch.tensor([2.0, 3.0], dtype=torch.float64)
    return arm


def test_joint_delta_to_joint_pos_reencodes_physical_goal_in_target_chart(monkeypatch):
    source = _source_arm(monkeypatch)
    target = _target_arm()
    source_env = _Env(source)
    target_env = _Env(target)

    source_native = np.array([[0.5, -0.5]], dtype=np.float64)
    from_pd_joint_delta_pos(
        output_mode="pd_joint_pos",
        ori_actions=source_native,
        ori_env=source_env,
        env=target_env,
    )

    # Source native [0.5,-0.5] maps through physical bounds
    # [-0.1,+0.1] x [-0.2,+0.2] to delta-q [0.05,-0.10].
    # Starting at [0.2,-0.3], the controller-independent target is
    # therefore [0.25,-0.40].
    desired_qpos = np.array([0.25, -0.40], dtype=np.float64)
    expected_target_native = gym_utils.inv_scale_action(
        desired_qpos,
        target.action_space_low.numpy(),
        target.action_space_high.numpy(),
    )

    np.testing.assert_allclose(target_env.last_action, expected_target_native, atol=1e-12)

    reconstructed = gym_utils.clip_and_scale_action(
        torch.as_tensor(target_env.last_action, dtype=torch.float64),
        target.action_space_low,
        target.action_space_high,
    ).numpy()
    np.testing.assert_allclose(reconstructed, desired_qpos, atol=1e-12)


def test_source_native_action_is_clipped_before_physical_delta_decode(monkeypatch):
    source = _source_arm(monkeypatch)
    target = _target_arm()
    source_env = _Env(source)
    target_env = _Env(target)

    from_pd_joint_delta_pos(
        output_mode="pd_joint_pos",
        ori_actions=np.array([[3.0, -2.0]], dtype=np.float64),
        ori_env=source_env,
        env=target_env,
    )

    desired_qpos = np.array([0.3, -0.5], dtype=np.float64)
    reconstructed = gym_utils.clip_and_scale_action(
        torch.as_tensor(target_env.last_action, dtype=torch.float64),
        target.action_space_low,
        target.action_space_high,
    ).numpy()
    np.testing.assert_allclose(reconstructed, desired_qpos, atol=1e-12)

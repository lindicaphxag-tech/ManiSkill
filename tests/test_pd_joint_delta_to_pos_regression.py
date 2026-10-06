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
        return {"arm": np.asarray(action).copy()}

    def from_action_dict(self, action_dict):
        return torch.as_tensor(action_dict["arm"])


class _Env:
    def __init__(self, controller):
        self.unwrapped = SimpleNamespace(
            agent=SimpleNamespace(controller=controller),
            device=torch.device("cpu"),
        )
        self.last_action = None

    def step(self, action):
        self.last_action = np.asarray(action)
        return None, 0.0, False, False, {"success": True}


def _source_arm(monkeypatch, *, qpos):
    arm = object.__new__(PDJointPosController)
    arm.config = SimpleNamespace(use_delta=True, normalize_action=True)
    arm.action_space_low = torch.tensor([-0.1, -0.2], dtype=torch.float64)
    arm.action_space_high = torch.tensor([0.1, 0.2], dtype=torch.float64)

    original_qpos = PDJointPosController.qpos

    def fake_qpos(self):
        if self is arm:
            return torch.tensor([qpos], dtype=torch.float64)
        return original_qpos.fget(self)

    monkeypatch.setattr(PDJointPosController, "qpos", property(fake_qpos))
    return arm


def _target_arm(*, normalize_action):
    arm = object.__new__(PDJointPosController)
    arm.config = SimpleNamespace(
        use_delta=False,
        normalize_action=normalize_action,
    )
    if normalize_action:
        arm.action_space_low = torch.tensor([-2.0, -1.0], dtype=torch.float64)
        arm.action_space_high = torch.tensor([2.0, 3.0], dtype=torch.float64)
    return arm


def test_delta_to_absolute_uses_physical_target_for_unnormalized_controller(monkeypatch):
    source_arm = _source_arm(monkeypatch, qpos=[0.2, -0.3])
    target_arm = _target_arm(normalize_action=False)
    source_env = _Env(_Combined(source_arm))
    target_env = _Env(_Combined(target_arm))

    from_pd_joint_delta_pos(
        output_mode="pd_joint_pos",
        ori_actions=np.array([[0.5, -0.5]], dtype=np.float64),
        ori_env=source_env,
        env=target_env,
    )

    # [0.5, -0.5] under source limits [-0.1, 0.1] x [-0.2, 0.2]
    # means physical delta-q [0.05, -0.1].
    np.testing.assert_allclose(target_env.last_action, [0.25, -0.4], atol=1e-12)


def test_delta_to_absolute_reencodes_for_normalized_target_controller(monkeypatch):
    source_arm = _source_arm(monkeypatch, qpos=[0.2, -0.3])
    target_arm = _target_arm(normalize_action=True)
    source_env = _Env(_Combined(source_arm))
    target_env = _Env(_Combined(target_arm))

    from_pd_joint_delta_pos(
        output_mode="pd_joint_pos",
        ori_actions=np.array([[0.5, -0.5]], dtype=np.float64),
        ori_env=source_env,
        env=target_env,
    )

    expected_qpos = np.array([0.25, -0.4])
    decoded_target = gym_utils.clip_and_scale_action(
        torch.as_tensor(target_env.last_action, dtype=torch.float64),
        target_arm.action_space_low,
        target_arm.action_space_high,
    ).numpy()
    np.testing.assert_allclose(decoded_target, expected_qpos, atol=1e-12)

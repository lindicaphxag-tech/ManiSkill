from types import SimpleNamespace

import numpy as np
import torch

from mani_skill.agents.controllers import PDJointPosController
from mani_skill.trajectory.utils.actions.conversion import (
    from_pd_joint_delta_pos,
    normalized_pd_joint_action_to_physical,
    qpos_to_pd_joint_pos,
)


class _Combined:
    def __init__(self, arm):
        self.controllers = {"arm": arm}

    def to_action_dict(self, action):
        return {"arm": np.asarray(action, dtype=np.float64).copy()}

    def from_action_dict(self, action_dict):
        return torch.as_tensor(action_dict["arm"], dtype=torch.float64)


class _Env:
    def __init__(self, controller):
        self.unwrapped = SimpleNamespace(
            agent=SimpleNamespace(controller=controller),
            device=torch.device("cpu"),
        )
        self.last_action = None

    def step(self, action):
        self.last_action = np.asarray(action, dtype=np.float64)
        return None, 0.0, False, False, {"success": True}


def test_joint_delta_decoder_accepts_numpy_trajectory_action():
    source = object.__new__(PDJointPosController)
    source.config = SimpleNamespace(use_delta=True, normalize_action=True)
    source.action_space_low = torch.tensor([-0.1, -0.2], dtype=torch.float64)
    source.action_space_high = torch.tensor([0.1, 0.2], dtype=torch.float64)

    physical = normalized_pd_joint_action_to_physical(
        source, np.array([0.5, -0.5], dtype=np.float64)
    )

    np.testing.assert_allclose(physical, [0.05, -0.1], atol=1e-12)


def test_physical_qpos_is_encoded_for_normalized_target_controller():
    target = object.__new__(PDJointPosController)
    target.config = SimpleNamespace(use_delta=False, normalize_action=True)
    target.action_space_low = torch.tensor([-2.0, -1.0], dtype=torch.float64)
    target.action_space_high = torch.tensor([2.0, 3.0], dtype=torch.float64)

    native = qpos_to_pd_joint_pos(target, np.array([0.5, 2.0]))

    np.testing.assert_allclose(native, [0.25, 0.5], atol=1e-12)


def test_joint_delta_to_joint_pos_preserves_physical_target(monkeypatch):
    source_arm = object.__new__(PDJointPosController)
    source_arm.config = SimpleNamespace(
        use_delta=True,
        normalize_action=True,
    )
    source_arm.action_space_low = torch.tensor([-0.1, -0.1], dtype=torch.float64)
    source_arm.action_space_high = torch.tensor([0.1, 0.1], dtype=torch.float64)

    target_arm = object.__new__(PDJointPosController)
    target_arm.config = SimpleNamespace(
        use_delta=False,
        normalize_action=False,
    )

    qpos_by_id = {id(source_arm): torch.tensor([[0.2, -0.3]], dtype=torch.float64)}
    original_qpos = PDJointPosController.qpos

    def fake_qpos(self):
        if id(self) in qpos_by_id:
            return qpos_by_id[id(self)]
        return original_qpos.fget(self)

    monkeypatch.setattr(PDJointPosController, "qpos", property(fake_qpos))

    source_env = _Env(_Combined(source_arm))
    target_env = _Env(_Combined(target_arm))

    from_pd_joint_delta_pos(
        output_mode="pd_joint_pos",
        ori_actions=np.array([[0.5, -0.5]], dtype=np.float64),
        ori_env=source_env,
        env=target_env,
    )

    # +/-0.1 delta range turns [0.5, -0.5] into [0.05, -0.05].
    # Starting at [0.2, -0.3] therefore commands [0.25, -0.35].
    np.testing.assert_allclose(target_env.last_action, [0.25, -0.35], atol=1e-12)

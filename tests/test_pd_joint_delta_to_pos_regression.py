"""Regression for NumPy replay actions through the Panda joint-delta converter."""

from types import SimpleNamespace

import numpy as np
import torch

from mani_skill.agents.controllers import PDJointPosController
from mani_skill.trajectory.utils.actions.conversion import from_pd_joint_delta_pos


class CombinedController:
    def __init__(self, arm):
        self.controllers = {"arm": arm}

    def to_action_dict(self, action):
        return {"arm": np.asarray(action).copy()}

    def from_action_dict(self, actions):
        return torch.as_tensor(actions["arm"])


class ReplayEnv:
    def __init__(self, controller):
        self.unwrapped = SimpleNamespace(
            agent=SimpleNamespace(controller=controller),
            device=torch.device("cpu"),
        )
        self.latest_action = None

    def step(self, action):
        self.latest_action = np.asarray(action, dtype=float)
        return None, 0.0, False, False, {"success": True}


def test_pd_joint_delta_pos_numpy_replay_has_correct_physical_target(monkeypatch):
    source = object.__new__(PDJointPosController)
    source.config = SimpleNamespace(
        use_delta=True,
        normalize_action=True,
        lower=-0.1,
        upper=0.1,
    )
    # The source qpos has a batch dimension but HDF5 action rows do not.
    qpos = torch.tensor([[0.2, -0.3]], dtype=torch.float64)
    original = PDJointPosController.qpos
    monkeypatch.setattr(
        PDJointPosController,
        "qpos",
        property(lambda self: qpos if self is source else original.fget(self)),
    )

    target = object.__new__(PDJointPosController)
    source_env = ReplayEnv(CombinedController(source))
    target_env = ReplayEnv(CombinedController(target))

    from_pd_joint_delta_pos(
        output_mode="pd_joint_pos",
        ori_actions=np.array([[0.5, -0.5]], dtype=np.float64),
        ori_env=source_env,
        env=target_env,
    )
    # [-1, 1] normalized source action maps to +/-0.1-radian physical delta.
    np.testing.assert_allclose(target_env.latest_action, [0.25, -0.35])

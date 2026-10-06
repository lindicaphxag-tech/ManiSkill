from types import SimpleNamespace

import numpy as np
import torch

from mani_skill.agents.controllers import PDJointPosController
from mani_skill.trajectory.utils.actions.conversion import from_pd_joint_delta_pos


class _Combined:
    def __init__(self, arm):
        self.controllers = {"arm": arm}

    def to_action_dict(self, action):
        return {"arm": action.clone() if isinstance(action, torch.Tensor) else np.asarray(action).copy()}

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
        self.last_action = np.asarray(action, dtype=np.float64).reshape(-1)
        return None, 0.0, False, False, {"success": True}


def _source_controller(monkeypatch, qpos):
    source = object.__new__(PDJointPosController)
    source.config = SimpleNamespace(
        use_delta=True,
        normalize_action=True,
        lower=-0.1,
        upper=0.1,
    )
    source.action_space_low = torch.tensor([-0.1, -0.1], dtype=torch.float64)
    source.action_space_high = torch.tensor([0.1, 0.1], dtype=torch.float64)

    original_qpos = PDJointPosController.qpos

    def fake_qpos(self):
        if self is source:
            return torch.tensor([qpos], dtype=torch.float64)
        return original_qpos.fget(self)

    monkeypatch.setattr(PDJointPosController, "qpos", property(fake_qpos))
    return source


def test_delta_trajectory_numpy_action_converts_to_physical_absolute_target(monkeypatch):
    source = _source_controller(monkeypatch, [0.2, -0.3])

    target = object.__new__(PDJointPosController)
    target.config = SimpleNamespace(use_delta=False, normalize_action=False)

    source_env = _Env(_Combined(source))
    target_env = _Env(_Combined(target))

    # Recorded trajectory rows are NumPy arrays. The source normalized deltas
    # [0.5, -0.5] under +/-0.1 physical limits mean [0.05, -0.05].
    from_pd_joint_delta_pos(
        output_mode="pd_joint_pos",
        ori_actions=np.array([[0.5, -0.5]], dtype=np.float64),
        ori_env=source_env,
        env=target_env,
    )

    np.testing.assert_allclose(target_env.last_action, [0.25, -0.35], atol=1e-12)


def test_physical_target_is_reencoded_for_normalized_absolute_controller(monkeypatch):
    source = _source_controller(monkeypatch, [0.2, -0.3])

    target = object.__new__(PDJointPosController)
    target.config = SimpleNamespace(use_delta=False, normalize_action=True)
    target.action_space_low = torch.tensor([-2.0, -2.0], dtype=torch.float64)
    target.action_space_high = torch.tensor([2.0, 2.0], dtype=torch.float64)

    source_env = _Env(_Combined(source))
    target_env = _Env(_Combined(target))

    # Use a Tensor source row here so this test isolates target-chart encoding
    # instead of the separate NumPy/torch boundary regression above.
    from_pd_joint_delta_pos(
        output_mode="pd_joint_pos",
        ori_actions=torch.tensor([[0.5, -0.5]], dtype=torch.float64),
        ori_env=source_env,
        env=target_env,
    )

    # Desired physical qpos is [0.25, -0.35]. Under target bounds [-2, 2],
    # the target controller-native normalized action is [0.125, -0.175].
    np.testing.assert_allclose(target_env.last_action, [0.125, -0.175], atol=1e-12)

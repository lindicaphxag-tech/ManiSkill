from types import SimpleNamespace

import numpy as np
import torch

from mani_skill.agents.controllers import PDJointPosController
from mani_skill.trajectory.utils.actions.conversion import from_pd_joint_delta_pos


def _arm_controller(*, use_delta, normalize_action, low, high, qpos):
    controller = object.__new__(PDJointPosController)
    controller.config = SimpleNamespace(
        use_delta=use_delta,
        normalize_action=normalize_action,
        lower=low,
        upper=high,
    )
    controller.action_space_low = torch.as_tensor(low, dtype=torch.float64)
    controller.action_space_high = torch.as_tensor(high, dtype=torch.float64)
    controller._test_qpos = torch.as_tensor([qpos], dtype=torch.float64)
    # PDJointPosController.qpos is a property backed by articulation.  Override
    # it at the class level only for this minimal conversion harness.
    return controller


class _ArmProxy:
    """Expose PDJointPosController identity while supplying a fixed qpos."""

    def __init__(self, controller, qpos):
        self._controller = controller
        self.config = controller.config
        self.action_space_low = controller.action_space_low
        self.action_space_high = controller.action_space_high
        self._qpos = torch.as_tensor([qpos], dtype=torch.float64)

    @property
    def qpos(self):
        return self._qpos


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


def test_joint_delta_to_joint_pos_uses_controller_semantics_end_to_end(monkeypatch):
    # Keep the production PDJointPosController type check while replacing only
    # its qpos property with a deterministic tensor for this CPU-only harness.
    source_arm = object.__new__(PDJointPosController)
    source_arm.config = SimpleNamespace(
        use_delta=True,
        normalize_action=True,
        lower=-0.1,
        upper=0.1,
    )
    source_arm.action_space_low = torch.tensor([-0.1, -0.1], dtype=torch.float64)
    source_arm.action_space_high = torch.tensor([0.1, 0.1], dtype=torch.float64)

    target_arm = object.__new__(PDJointPosController)
    target_arm.config = SimpleNamespace(
        use_delta=False,
        normalize_action=False,
        lower=None,
        upper=None,
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

    # Source normalized deltas [0.5, -0.5] under +/-0.1 physical limits mean
    # delta-q [0.05, -0.05].  Starting from [0.2, -0.3], the exact absolute
    # target is therefore [0.25, -0.35].
    np.testing.assert_allclose(
        target_env.last_action,
        [0.25, -0.35],
        atol=1e-12,
    )



def test_joint_delta_to_normalized_joint_pos_encodes_target_native_action(monkeypatch):
    source_arm = object.__new__(PDJointPosController)
    source_arm.config = SimpleNamespace(
        use_delta=True,
        normalize_action=True,
        lower=-0.1,
        upper=0.1,
    )
    source_arm.action_space_low = torch.tensor([-0.1, -0.1], dtype=torch.float64)
    source_arm.action_space_high = torch.tensor([0.1, 0.1], dtype=torch.float64)

    target_arm = object.__new__(PDJointPosController)
    target_arm.config = SimpleNamespace(
        use_delta=False,
        normalize_action=True,
        lower=None,
        upper=None,
    )
    target_arm.action_space_low = torch.tensor([-2.0, -2.0], dtype=torch.float64)
    target_arm.action_space_high = torch.tensor([2.0, 2.0], dtype=torch.float64)

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

    # Desired physical target remains [0.25, -0.35]. Under target physical
    # range [-2, 2], the native normalized action must be [0.125, -0.175].
    np.testing.assert_allclose(
        target_env.last_action,
        [0.125, -0.175],
        atol=1e-12,
    )
    reconstructed = 0.5 * (
        target_arm.action_space_high.numpy() + target_arm.action_space_low.numpy()
    ) + 0.5 * (
        target_arm.action_space_high.numpy() - target_arm.action_space_low.numpy()
    ) * target_env.last_action
    np.testing.assert_allclose(reconstructed, [0.25, -0.35], atol=1e-12)

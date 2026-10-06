from types import SimpleNamespace

import numpy as np
import pytest
import torch
from gymnasium import spaces

from mani_skill.agents.controllers import PDJointPosController

from trace_semantics import joint_position_trace_ir


class _PDJointHarness(PDJointPosController):
    @property
    def qpos(self):
        return self._harness_qpos

    def set_drive_targets(self, targets):
        self._captured_targets.append(targets.detach().cpu().numpy().copy())


def _make_controller(
    *,
    mode,
    physical_low,
    physical_high,
    qpos,
    target_qpos,
    sim_steps,
    interpolate,
    normalized=True,
):
    low = np.asarray(physical_low, dtype=np.float64)
    high = np.asarray(physical_high, dtype=np.float64)
    ctrl = object.__new__(_PDJointHarness)
    ctrl.scene = SimpleNamespace(num_envs=1)
    ctrl.config = SimpleNamespace(
        use_delta=(mode != "absolute"),
        use_target=(mode == "delta_target"),
        interpolate=interpolate,
        normalize_action=normalized,
    )
    ctrl._normalize_action = normalized
    ctrl._sim_steps = sim_steps
    ctrl._harness_qpos = torch.tensor([qpos], dtype=torch.float64)
    ctrl._target_qpos = torch.tensor([target_qpos], dtype=torch.float64)
    ctrl._start_qpos = ctrl._harness_qpos.clone()
    ctrl._captured_targets = []

    if normalized:
        ctrl.action_space_low = torch.tensor(low, dtype=torch.float64)
        ctrl.action_space_high = torch.tensor(high, dtype=torch.float64)
        ctrl.action_space = spaces.Box(
            -1.0, 1.0, shape=(len(low),), dtype=np.float64
        )
    else:
        ctrl.action_space = spaces.Box(low, high, dtype=np.float64)
    return ctrl


def _actual_trace(ctrl, native_action):
    action = torch.tensor([native_action], dtype=torch.float64)
    ctrl.set_action(action)
    if ctrl.config.interpolate:
        for _ in range(ctrl._sim_steps):
            ctrl.before_simulation_step()
    else:
        # Host sends the held target at set_action(). Semantically that same
        # drive target remains active over each simulation substep.
        assert len(ctrl._captured_targets) == 1
        held = ctrl._captured_targets[0]
        ctrl._captured_targets = [held.copy() for _ in range(ctrl._sim_steps)]
    return np.concatenate([x[0] for x in ctrl._captured_targets], axis=0)


@pytest.mark.parametrize(
    "mode,interpolate,native_action,qpos,target_qpos",
    [
        ("absolute", False, [0.1, -0.2], [0.4, -0.3], [0.0, 0.0]),
        ("absolute", True, [0.1, -0.2], [0.4, -0.3], [0.0, 0.0]),
        ("delta_current", False, [0.5, -0.25], [0.4, -0.3], [0.0, 0.0]),
        ("delta_current", True, [0.5, -0.25], [0.4, -0.3], [0.0, 0.0]),
        ("delta_target", False, [0.5, -0.25], [0.4, -0.3], [0.7, -0.8]),
        ("delta_target", True, [0.5, -0.25], [0.4, -0.3], [0.7, -0.8]),
    ],
)
def test_trace_ir_matches_host_pd_joint_position_controller(
    mode, interpolate, native_action, qpos, target_qpos
):
    physical_low = np.array([-0.2, -0.4])
    physical_high = np.array([0.2, 0.4])
    sim_steps = 4
    ctrl = _make_controller(
        mode=mode,
        physical_low=physical_low,
        physical_high=physical_high,
        qpos=qpos,
        target_qpos=target_qpos,
        sim_steps=sim_steps,
        interpolate=interpolate,
        normalized=True,
    )
    ir = joint_position_trace_ir(
        mode=mode,
        physical_low=physical_low,
        physical_high=physical_high,
        sim_steps=sim_steps,
        interpolate=interpolate,
        normalized=True,
    )

    host_trace = _actual_trace(ctrl, native_action)
    ir_trace, ir_goal, ir_next = ir.evaluate(
        np.asarray(native_action, dtype=float),
        np.asarray(qpos, dtype=float),
        np.asarray(target_qpos, dtype=float),
    )

    np.testing.assert_allclose(host_trace, ir_trace, atol=1e-12)
    np.testing.assert_allclose(
        ctrl._target_qpos.detach().cpu().numpy()[0], ir_goal, atol=1e-12
    )
    np.testing.assert_allclose(
        ctrl._target_qpos.detach().cpu().numpy()[0], ir_next, atol=1e-12
    )


def test_host_parity_includes_runtime_clipping_of_normalized_action():
    ctrl = _make_controller(
        mode="delta_current",
        physical_low=[-0.2],
        physical_high=[0.2],
        qpos=[0.4],
        target_qpos=[0.0],
        sim_steps=2,
        interpolate=True,
        normalized=True,
    )
    ir = joint_position_trace_ir(
        mode="delta_current",
        physical_low=np.array([-0.2]),
        physical_high=np.array([0.2]),
        sim_steps=2,
        interpolate=True,
        normalized=True,
    )

    # Host clips 3.0 to +1 before scaling. The IR's declared native domain is
    # [-1, 1]; parity is therefore checked against the clipped native command,
    # and out-of-domain inputs remain a caller-side contract violation.
    host_trace = _actual_trace(ctrl, [3.0])
    ir_trace, _, _ = ir.evaluate(
        np.array([1.0]), np.array([0.4]), np.array([0.0])
    )
    np.testing.assert_allclose(host_trace, ir_trace, atol=1e-12)

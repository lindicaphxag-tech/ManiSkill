import numpy as np

from robosuite.controllers.parts.generic.joint_pos import JointPositionController

from contextual_trace_morphism import (
    compile_contextual_trace_morphism,
    shared_current_qpos_binding,
)
from robosuite_joint_semantics import (
    certify_robosuite_delta_affine_region,
    robosuite_joint_position_ir,
)


def _host_controller(
    *,
    input_type,
    current_qpos,
    input_min=-1.0,
    input_max=1.0,
    output_min=-0.05,
    output_max=0.05,
    qpos_limits=None,
):
    current = np.asarray(current_qpos, dtype=float)
    d = current.shape[0]
    ctrl = object.__new__(JointPositionController)
    ctrl.input_type = input_type
    ctrl.impedance_mode = "fixed"
    ctrl.qpos_index = np.arange(d)
    ctrl.joint_pos = current.copy()
    ctrl.position_limits = (
        None if qpos_limits is None else np.asarray(qpos_limits, dtype=float)
    )
    ctrl.input_min = np.broadcast_to(np.asarray(input_min, dtype=float), (d,)).copy()
    ctrl.input_max = np.broadcast_to(np.asarray(input_max, dtype=float), (d,)).copy()
    ctrl.output_min = np.broadcast_to(np.asarray(output_min, dtype=float), (d,)).copy()
    ctrl.output_max = np.broadcast_to(np.asarray(output_max, dtype=float), (d,)).copy()
    ctrl.action_scale = None
    ctrl.action_input_transform = None
    ctrl.action_output_transform = None
    ctrl.goal_qpos = None
    ctrl.interpolator = None
    ctrl.update = lambda *args, **kwargs: None
    return ctrl


def test_delta_ir_matches_robosuite_set_goal_on_random_unclipped_actions():
    rng = np.random.default_rng(2701)
    ir = robosuite_joint_position_ir(input_type="delta", d=3)
    for _ in range(500):
        x = rng.uniform(-0.5, 0.5, size=3)
        u = rng.uniform(-1.0, 1.0, size=3)
        ctrl = _host_controller(input_type="delta", current_qpos=x)
        ctrl.set_goal(u)
        _, goal, _ = ir.evaluate(u, x, np.zeros(3))
        np.testing.assert_allclose(ctrl.goal_qpos, goal, atol=1e-12)


def test_absolute_ir_matches_robosuite_direct_goal_semantics():
    rng = np.random.default_rng(2702)
    ir = robosuite_joint_position_ir(
        input_type="absolute",
        d=3,
        native_absolute_low=-np.ones(3),
        native_absolute_high=np.ones(3),
    )
    for _ in range(200):
        x = rng.uniform(-0.5, 0.5, size=3)
        u = rng.uniform(-1.0, 1.0, size=3)
        ctrl = _host_controller(input_type="absolute", current_qpos=x)
        ctrl.set_goal(u)
        _, goal, _ = ir.evaluate(u, x, np.zeros(3))
        np.testing.assert_allclose(ctrl.goal_qpos, goal, atol=1e-12)


def test_qpos_boundary_is_real_piecewise_host_semantics():
    limits = np.array([[-1.0], [1.0]])
    ctrl = _host_controller(
        input_type="delta",
        current_qpos=np.array([0.99]),
        qpos_limits=limits,
    )
    ctrl.set_goal(np.array([1.0]))
    np.testing.assert_allclose(ctrl.goal_qpos, [1.0], atol=1e-12)

    ir = robosuite_joint_position_ir(input_type="delta", d=1)
    _, affine_goal, _ = ir.evaluate(
        np.array([1.0]), np.array([0.99]), np.zeros(1)
    )
    np.testing.assert_allclose(affine_goal, [1.04], atol=1e-12)

    region = certify_robosuite_delta_affine_region(
        d=1,
        state_low=np.array([0.96]),
        state_high=np.array([1.0]),
        qpos_limits=limits,
    )
    assert not region.clip_inactive


def test_compiled_cst_matches_both_robosuite_controller_modes():
    rng = np.random.default_rng(2703)
    source_region = certify_robosuite_delta_affine_region(
        d=2,
        state_low=np.array([-0.5, -0.5]),
        state_high=np.array([0.5, 0.5]),
        qpos_limits=np.array([[-1.0, -1.0], [1.0, 1.0]]),
    )
    target_ir = robosuite_joint_position_ir(
        input_type="absolute",
        d=2,
        native_absolute_low=np.array([-1.0, -1.0]),
        native_absolute_high=np.array([1.0, 1.0]),
    )
    binding = shared_current_qpos_binding(2)
    cert = compile_contextual_trace_morphism(
        source=source_region.ir,
        target=target_ir,
        source_binding=binding,
        target_binding=binding,
        context_low=np.array([-0.5, -0.5]),
        context_high=np.array([0.5, 0.5]),
    )
    assert cert.bounded_on_region

    for _ in range(500):
        x = rng.uniform(-0.5, 0.5, size=2)
        u_delta = rng.uniform(-1.0, 1.0, size=2)

        source_host = _host_controller(
            input_type="delta",
            current_qpos=x,
            qpos_limits=np.array([[-1.0, -1.0], [1.0, 1.0]]),
        )
        source_host.set_goal(u_delta)

        u_absolute = cert.transport(u_delta, x)
        target_host = _host_controller(
            input_type="absolute",
            current_qpos=x,
        )
        target_host.set_goal(u_absolute)

        np.testing.assert_allclose(
            target_host.goal_qpos, source_host.goal_qpos, atol=1e-12
        )

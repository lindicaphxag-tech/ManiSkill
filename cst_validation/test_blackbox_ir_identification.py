import numpy as np

from blackbox_ir_identification import identify_affine_trace_ir
from trace_semantics import joint_position_trace_ir


class _IROracle:
    def __init__(self, ir):
        self.ir = ir
        self.action_dim = ir.action_dim
        self.state_dim = ir.state_dim
        self.hidden_dim = ir.hidden_dim
        self.trace_steps = ir.trace_steps
        self.native_low = ir.native_low
        self.native_high = ir.native_high

    def query(self, action, state, hidden):
        return self.ir.evaluate(action, state, hidden)


def test_identifies_delta_target_controller_without_hand_written_formula():
    truth = joint_position_trace_ir(
        mode="delta_target",
        physical_low=np.array([-0.2, -0.1]),
        physical_high=np.array([0.2, 0.1]),
        sim_steps=4,
        interpolate=True,
    )
    cert = identify_affine_trace_ir(
        _IROracle(truth),
        state_center=np.array([0.2, -0.1]),
        state_radius=np.array([0.5, 0.5]),
        hidden_center=np.array([0.1, 0.3]),
        hidden_radius=np.array([0.5, 0.5]),
        validation_samples=100,
    )
    assert cert.accepted
    assert cert.ir is not None
    np.testing.assert_allclose(cert.ir.T_u, truth.T_u, atol=1e-10)
    np.testing.assert_allclose(cert.ir.T_x, truth.T_x, atol=1e-10)
    np.testing.assert_allclose(cert.ir.T_z, truth.T_z, atol=1e-10)
    np.testing.assert_allclose(cert.ir.H_u, truth.H_u, atol=1e-10)
    np.testing.assert_allclose(cert.ir.H_z, truth.H_z, atol=1e-10)
    assert cert.fit_query_count == 1 + 6


def test_identified_ir_can_drive_exact_cross_controller_transport():
    source = joint_position_trace_ir(
        mode="delta_current",
        physical_low=np.array([-0.2]),
        physical_high=np.array([0.2]),
        sim_steps=3,
        interpolate=True,
    )
    cert = identify_affine_trace_ir(
        _IROracle(source),
        state_center=np.array([0.0]),
        state_radius=np.array([0.8]),
        hidden_center=np.array([0.0]),
        hidden_radius=np.array([0.8]),
        validation_samples=50,
    )
    assert cert.accepted
    u = np.array([0.4])
    x = np.array([0.25])
    z = np.array([-0.2])
    expected = source.evaluate(u, x, z)
    actual = cert.ir.evaluate(u, x, z)
    for lhs, rhs in zip(actual, expected, strict=True):
        np.testing.assert_allclose(lhs, rhs, atol=1e-10)


class _ClippedOracle:
    action_dim = 1
    state_dim = 1
    hidden_dim = 1
    trace_steps = 1
    native_low = np.array([-1.0])
    native_high = np.array([1.0])

    def query(self, action, state, hidden):
        # Saturation makes one global affine model invalid over the declared box.
        goal = np.clip(state + action, -0.25, 0.25)
        trace = goal.copy()
        next_hidden = hidden + 0.1 * goal
        return trace, goal, next_hidden


def test_rejects_piecewise_controller_instead_of_fitting_false_global_affine_ir():
    cert = identify_affine_trace_ir(
        _ClippedOracle(),
        state_center=np.array([0.0]),
        state_radius=np.array([0.8]),
        hidden_center=np.array([0.0]),
        hidden_radius=np.array([0.5]),
        validation_samples=200,
        validation_seed=7,
    )
    assert not cert.accepted
    assert cert.ir is None
    assert cert.max_goal_relative_residual > 0.05
    assert "piecewise" in cert.reason


class _QuadraticHiddenOracle:
    action_dim = 1
    state_dim = 1
    hidden_dim = 1
    trace_steps = 1
    native_low = np.array([-1.0])
    native_high = np.array([1.0])

    def query(self, action, state, hidden):
        goal = action + state
        trace = goal.copy()
        next_hidden = hidden + action**2
        return trace, goal, next_hidden


def test_rejects_hidden_state_nonlinearity_even_when_goal_is_affine():
    cert = identify_affine_trace_ir(
        _QuadraticHiddenOracle(),
        state_center=np.array([0.0]),
        state_radius=np.array([1.0]),
        hidden_center=np.array([0.0]),
        hidden_radius=np.array([1.0]),
        validation_samples=100,
    )
    assert not cert.accepted
    assert cert.ir is None
    assert cert.max_trace_relative_residual < 1e-10
    assert cert.max_goal_relative_residual < 1e-10
    assert cert.max_hidden_relative_residual > 1e-3

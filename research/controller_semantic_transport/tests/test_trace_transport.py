import numpy as np

from cst.trace_transport import solve_counterfactual_trace_transport


def test_affine_target_oracle_recovers_cross_family_action():
    A = np.array([[1.0, 0.2],[0.5, -0.3],[0.1, 0.8],[1.2, 0.4],[-0.2, 0.7],[0.3, -0.6]])
    b = np.array([0.2, -0.1, 0.3, 0.0, 0.5, -0.2])
    true_action = np.array([0.35, -0.25])
    source_trace = (A @ true_action + b).reshape(3, 2)

    cert = solve_counterfactual_trace_transport(
        source_trace=source_trace,
        target_oracle=lambda u: (A @ u + b).reshape(3, 2),
        initial_action=np.zeros(2),
        action_low=-np.ones(2),
        action_high=np.ones(2),
        max_relative_residual=1e-6,
        min_improvement_ratio=0.9,
    )

    assert cert.accepted, cert.reason
    np.testing.assert_allclose(cert.action, true_action, atol=1e-4)
    assert cert.relative_residual < 1e-6


def test_unrepresentable_trace_fails_closed_at_action_box():
    source_trace = np.array([[5.0], [5.0]])
    cert = solve_counterfactual_trace_transport(
        source_trace=source_trace,
        target_oracle=lambda u: np.array([[u[0]], [u[0]]]),
        initial_action=np.array([0.0]),
        action_low=np.array([-1.0]),
        action_high=np.array([1.0]),
        max_relative_residual=0.05,
        min_saturation_margin=0.01,
    )
    assert not cert.accepted
    assert cert.relative_residual > 0.05


def test_ill_conditioned_target_mapping_is_not_granted_authority():
    eps = 1e-10
    source_trace = np.array([0.4, 0.4])
    def oracle(u):
        total = u[0] + u[1]
        return np.array([total, total + eps * u[1]])

    cert = solve_counterfactual_trace_transport(
        source_trace=source_trace,
        target_oracle=oracle,
        initial_action=np.zeros(2),
        action_low=-np.ones(2),
        action_high=np.ones(2),
        max_relative_residual=1e-5,
        max_jacobian_condition=1e5,
    )
    assert not cert.accepted
    assert cert.jacobian_condition > 1e5
    assert "ill-conditioned" in cert.reason


def test_exact_initial_match_does_not_require_fake_improvement():
    source_trace = np.array([0.2, -0.1])
    initial = np.array([0.2, -0.1])
    cert = solve_counterfactual_trace_transport(
        source_trace=source_trace,
        target_oracle=lambda u: u.copy(),
        initial_action=initial,
        action_low=-np.ones(2),
        action_high=np.ones(2),
        max_relative_residual=1e-9,
    )
    assert cert.accepted
    assert cert.residual_norm < 1e-12

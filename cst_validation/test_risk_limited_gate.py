import numpy as np

from cst_validation.closed_loop_transport import (
    LinearClosedLoopModel,
    synthesize_closed_loop_transport,
)
from cst_validation.risk_limited_gate import (
    calibrate_split_conformal_residual,
    certify_risk_limited_dominance,
)


def _observed(model, states, actions, residual_fn=None):
    out = []
    for x, u in zip(states, actions):
        y = model.A @ x + model.B @ u
        if residual_fn is not None:
            y = y + residual_fn(x, u)
        out.append(y)
    return np.stack(out)


def test_split_conformal_uses_finite_sample_order_statistic():
    model = LinearClosedLoopModel(A=np.array([[0.0]]), B=np.array([[0.0]]))
    states = np.arange(1.0, 20.0)[:, None]
    actions = np.zeros_like(states)
    # Residual scores are exactly 1,2,...,19.
    observed = states.copy()
    bound = calibrate_split_conformal_residual(
        model, states, actions, observed, alpha=0.10
    )
    # ceil((19 + 1) * .9) = 18.
    assert bound.order_statistic_rank == 18
    assert bound.residual_quantile == 18.0
    assert bound.finite


def test_too_few_samples_fail_closed_instead_of_weakening_risk():
    model = LinearClosedLoopModel(A=np.array([[1.0]]), B=np.array([[1.0]]))
    states = np.array([[-1.0], [-0.5], [0.5], [1.0]])
    actions = np.zeros_like(states)
    observed = _observed(model, states, actions)
    bound = calibrate_split_conformal_residual(
        model, states, actions, observed, alpha=0.05
    )
    # ceil(5 * .95) = 5 > n=4, so there is no finite bound at this risk.
    assert not bound.finite
    assert np.isinf(bound.residual_quantile)


def test_clear_transport_advantage_is_accepted_at_declared_familywise_coverage():
    source = LinearClosedLoopModel(A=np.array([[0.8]]), B=np.array([[1.0]]))
    target = LinearClosedLoopModel(A=np.array([[0.2]]), B=np.array([[2.0]]))
    transport = synthesize_closed_loop_transport(source, target)

    states = np.linspace(-1.0, 1.0, 49)[:, None]
    actions = np.linspace(1.0, -1.0, 49)[:, None]
    src = calibrate_split_conformal_residual(
        source, states, actions, _observed(source, states, actions), alpha=0.04
    )
    tgt = calibrate_split_conformal_residual(
        target, states, actions, _observed(target, states, actions), alpha=0.04
    )

    cert = certify_risk_limited_dominance(
        source,
        target,
        transport,
        state=np.array([0.6]),
        source_action=np.array([0.4]),
        source_residual=src,
        target_residual=tgt,
        required_coverage=0.88,
    )
    assert cert.use_transport
    assert cert.familywise_coverage_lower_bound == 0.88
    assert cert.transport_upper_bound < cert.fallback_lower_bound


def test_union_bound_refuses_when_requested_coverage_is_stronger_than_calibration():
    source = LinearClosedLoopModel(A=np.array([[0.8]]), B=np.array([[1.0]]))
    target = LinearClosedLoopModel(A=np.array([[0.2]]), B=np.array([[2.0]]))
    transport = synthesize_closed_loop_transport(source, target)

    states = np.linspace(-1.0, 1.0, 49)[:, None]
    actions = np.linspace(1.0, -1.0, 49)[:, None]
    src = calibrate_split_conformal_residual(
        source, states, actions, _observed(source, states, actions), alpha=0.04
    )
    tgt = calibrate_split_conformal_residual(
        target, states, actions, _observed(target, states, actions), alpha=0.04
    )

    cert = certify_risk_limited_dominance(
        source,
        target,
        transport,
        state=np.array([0.6]),
        source_action=np.array([0.4]),
        source_residual=src,
        target_residual=tgt,
        required_coverage=0.95,
    )
    assert not cert.use_transport
    assert "coverage" in cert.reason


def test_nonlinear_residual_uncertainty_can_make_nominal_advantage_unsafe_to_claim():
    source = LinearClosedLoopModel(A=np.array([[0.8]]), B=np.array([[1.0]]))
    target = LinearClosedLoopModel(A=np.array([[0.75]]), B=np.array([[1.05]]))
    transport = synthesize_closed_loop_transport(source, target)

    states = np.linspace(-1.0, 1.0, 99)[:, None]
    actions = np.linspace(1.0, -1.0, 99)[:, None]
    residual = lambda x, u: np.array([0.03 * (x[0] ** 2 + u[0] ** 2)])
    src = calibrate_split_conformal_residual(
        source,
        states,
        actions,
        _observed(source, states, actions, residual),
        alpha=0.03,
    )
    tgt = calibrate_split_conformal_residual(
        target,
        states,
        actions,
        _observed(target, states, actions, lambda x, u: -residual(x, u)),
        alpha=0.03,
    )

    cert = certify_risk_limited_dominance(
        source,
        target,
        transport,
        state=np.array([0.5]),
        source_action=np.array([0.4]),
        source_residual=src,
        target_residual=tgt,
        required_coverage=0.90,
    )
    assert not cert.use_transport
    assert cert.certified_margin <= 0.0


def test_query_outside_calibration_box_is_refused_even_with_small_residuals():
    source = LinearClosedLoopModel(A=np.array([[0.8]]), B=np.array([[1.0]]))
    target = LinearClosedLoopModel(A=np.array([[0.2]]), B=np.array([[2.0]]))
    transport = synthesize_closed_loop_transport(source, target)

    states = np.linspace(-0.5, 0.5, 49)[:, None]
    actions = np.linspace(-0.5, 0.5, 49)[:, None]
    src = calibrate_split_conformal_residual(
        source, states, actions, _observed(source, states, actions), alpha=0.04
    )
    tgt = calibrate_split_conformal_residual(
        target, states, actions, _observed(target, states, actions), alpha=0.04
    )

    cert = certify_risk_limited_dominance(
        source,
        target,
        transport,
        state=np.array([0.9]),
        source_action=np.array([0.2]),
        source_residual=src,
        target_residual=tgt,
        required_coverage=0.88,
    )
    assert not cert.use_transport
    assert not cert.inside_calibration_domain

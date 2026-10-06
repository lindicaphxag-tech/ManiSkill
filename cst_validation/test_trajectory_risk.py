import numpy as np

from cst_validation.closed_loop_transport import (
    LinearClosedLoopModel,
    synthesize_closed_loop_transport,
)
from cst_validation.trajectory_risk import (
    calibrate_episode_max_residual,
    certify_episode_risk_dominance,
    combine_episode_event_families,
)


def test_episode_calibration_uses_max_per_episode_not_pooled_steps():
    episodes = [
        np.array([0.1, 0.2, 0.3]),
        np.array([0.05, 0.4]),
        np.array([0.2, 0.25, 0.35, 0.45]),
        np.array([0.1, 0.15]),
        np.array([0.5]),
        np.array([0.12, 0.18]),
        np.array([0.22, 0.28]),
        np.array([0.32, 0.38]),
        np.array([0.42, 0.48]),
    ]
    bound = calibrate_episode_max_residual(episodes, alpha=0.2)
    # n=9 -> ceil(10*.8)=8; episode maxima sorted:
    # .18,.28,.3,.38,.4,.45,.48,.5 => rank 8 = .5 (plus one duplicate ordering)
    maxima = sorted(float(np.max(x)) for x in episodes)
    assert bound.order_statistic_rank == 8
    assert bound.max_residual_quantile == maxima[7]
    assert bound.min_events_per_episode == 1
    assert bound.max_events_per_episode == 4


def test_too_few_episodes_refuses_high_confidence():
    episodes = [np.array([0.01, 0.02]) for _ in range(9)]
    bound = calibrate_episode_max_residual(episodes, alpha=0.05)
    # ceil(10*.95)=10 > 9.
    assert not bound.finite
    assert np.isinf(bound.max_residual_quantile)


def test_combined_event_family_covers_source_adapt_and_fallback_events():
    source = np.array([0.01, 0.02])
    adapted = np.array([0.03, 0.04])
    fallback = np.array([0.05, 0.06])
    combined = combine_episode_event_families(source, adapted, fallback)
    np.testing.assert_allclose(combined, [0.01, 0.02, 0.03, 0.04, 0.05, 0.06])


def test_episode_risk_gate_accepts_only_when_separation_survives_episode_radius():
    source = LinearClosedLoopModel(A=np.array([[0.8]]), B=np.array([[1.0]]))
    target = LinearClosedLoopModel(A=np.array([[0.2]]), B=np.array([[2.0]]))
    transport = synthesize_closed_loop_transport(source, target)

    # 24 exchangeable calibration episodes, each score <= .01.
    episodes = [
        np.array([0.001 + 0.0002 * ((i + j) % 10) for j in range(12)])
        for i in range(24)
    ]
    bound = calibrate_episode_max_residual(episodes, alpha=0.08)
    assert bound.finite

    cert = certify_episode_risk_dominance(
        source,
        target,
        transport,
        state=np.array([0.6]),
        source_action=np.array([0.4]),
        episode_residual=bound,
        required_episode_coverage=0.92,
    )
    assert cert.use_transport
    assert cert.transport_upper_bound < cert.fallback_lower_bound
    assert cert.episode_coverage_lower_bound == 0.92


def test_large_episode_max_residual_can_refuse_nominally_better_adapter():
    source = LinearClosedLoopModel(A=np.array([[0.8]]), B=np.array([[1.0]]))
    target = LinearClosedLoopModel(A=np.array([[0.75]]), B=np.array([[1.05]]))
    transport = synthesize_closed_loop_transport(source, target)

    episodes = [
        np.array([0.02, 0.03, 0.04 + 0.001 * (i % 4)])
        for i in range(24)
    ]
    bound = calibrate_episode_max_residual(episodes, alpha=0.08)

    cert = certify_episode_risk_dominance(
        source,
        target,
        transport,
        state=np.array([0.5]),
        source_action=np.array([0.4]),
        episode_residual=bound,
        required_episode_coverage=0.92,
    )
    assert not cert.use_transport
    assert cert.certified_margin <= 0.0


def test_episode_coverage_request_stronger_than_calibration_fails_closed():
    source = LinearClosedLoopModel(A=np.array([[0.8]]), B=np.array([[1.0]]))
    target = LinearClosedLoopModel(A=np.array([[0.2]]), B=np.array([[2.0]]))
    transport = synthesize_closed_loop_transport(source, target)

    episodes = [np.array([0.001, 0.002]) for _ in range(24)]
    bound = calibrate_episode_max_residual(episodes, alpha=0.08)

    cert = certify_episode_risk_dominance(
        source,
        target,
        transport,
        state=np.array([0.6]),
        source_action=np.array([0.4]),
        episode_residual=bound,
        required_episode_coverage=0.99,
    )
    assert not cert.use_transport
    assert "coverage" in cert.reason

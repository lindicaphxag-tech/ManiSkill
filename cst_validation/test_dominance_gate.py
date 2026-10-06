import numpy as np

from closed_loop_transport import LinearClosedLoopModel, synthesize_closed_loop_transport
from dominance_gate import calibrate_quadratic_remainder, certify_calibrated_dominance


def _exact_calibration(model, states, actions):
    observed=np.stack([model.A@x+model.B@u for x,u in zip(states,actions)])
    return calibrate_quadratic_remainder(model,states,actions,observed)


def test_exact_models_enable_transport_when_fallback_is_strictly_worse():
    source=LinearClosedLoopModel(A=np.array([[0.8]]),B=np.array([[1.0]]))
    target=LinearClosedLoopModel(A=np.array([[0.5]]),B=np.array([[2.0]]))
    transport=synthesize_closed_loop_transport(source,target)
    states=np.array([[-1.0],[-0.5],[0.5],[1.0]])
    actions=np.array([[-1.0],[0.5],[-0.5],[1.0]])
    src_env=_exact_calibration(source,states,actions)
    tgt_env=_exact_calibration(target,states,actions)

    cert=certify_calibrated_dominance(
        source,target,transport,
        state=np.array([0.4]),source_action=np.array([0.3]),
        source_envelope=src_env,target_envelope=tgt_env,
    )
    assert cert.use_transport
    assert cert.transport_upper_bound < cert.fallback_lower_bound


def test_overlapping_calibrated_intervals_refuse_transport():
    source=LinearClosedLoopModel(A=np.array([[0.8]]),B=np.array([[1.0]]))
    target=LinearClosedLoopModel(A=np.array([[0.79]]),B=np.array([[1.01]]))
    transport=synthesize_closed_loop_transport(source,target)

    states=np.array([[-1.0],[-0.5],[0.5],[1.0]])
    actions=np.array([[-1.0],[0.5],[-0.5],[1.0]])
    # Inject a deterministic nonlinear residual large enough that the tiny
    # model-predicted advantage is not separable.
    src_obs=np.stack([source.A@x+source.B@u+np.array([0.02*(x[0]**2+u[0]**2)]) for x,u in zip(states,actions)])
    tgt_obs=np.stack([target.A@x+target.B@u-np.array([0.02*(x[0]**2+u[0]**2)]) for x,u in zip(states,actions)])
    src_env=calibrate_quadratic_remainder(source,states,actions,src_obs)
    tgt_env=calibrate_quadratic_remainder(target,states,actions,tgt_obs)

    cert=certify_calibrated_dominance(
        source,target,transport,
        state=np.array([0.4]),source_action=np.array([0.3]),
        source_envelope=src_env,target_envelope=tgt_env,
    )
    assert not cert.use_transport
    assert cert.certified_margin <= 0.0


def test_outside_calibration_box_fails_closed():
    source=LinearClosedLoopModel(A=np.array([[0.8]]),B=np.array([[1.0]]))
    target=LinearClosedLoopModel(A=np.array([[0.5]]),B=np.array([[2.0]]))
    transport=synthesize_closed_loop_transport(source,target)
    states=np.array([[-0.5],[0.5]])
    actions=np.array([[-0.5],[0.5]])
    src_env=_exact_calibration(source,states,actions)
    tgt_env=_exact_calibration(target,states,actions)

    cert=certify_calibrated_dominance(
        source,target,transport,
        state=np.array([0.8]),source_action=np.array([0.2]),
        source_envelope=src_env,target_envelope=tgt_env,
    )
    assert not cert.use_transport
    assert not cert.inside_calibration_domain
    assert "calibration domain" in cert.reason


def test_quadratic_envelope_recovers_known_remainder_coefficient():
    model=LinearClosedLoopModel(A=np.array([[0.7]]),B=np.array([[0.4]]))
    states=np.array([[-1.0],[-0.5],[0.5],[1.0]])
    actions=np.array([[0.5],[-1.0],[1.0],[-0.5]])
    coefficient=0.03
    observed=np.stack([
        model.A@x+model.B@u+np.array([coefficient*(x[0]**2+u[0]**2)])
        for x,u in zip(states,actions)
    ])
    env=calibrate_quadratic_remainder(model,states,actions,observed)
    np.testing.assert_allclose(env.coefficient,coefficient,rtol=1e-12,atol=1e-12)

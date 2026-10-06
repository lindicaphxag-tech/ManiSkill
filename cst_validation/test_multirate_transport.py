import numpy as np
import pytest

from closed_loop_transport import LinearClosedLoopModel
from multirate_transport import lift_zero_order_hold, synthesize_multirate_transport


def _exact_scalar_discretization(a: float, b: float, dt: float):
    A=np.array([[np.exp(-a*dt)]],dtype=float)
    B=np.array([[b/a*(1.0-np.exp(-a*dt))]],dtype=float)
    return LinearClosedLoopModel(A=A,B=B)


def test_zero_order_hold_lift_matches_repeated_micro_steps():
    model=LinearClosedLoopModel(A=np.array([[0.8]]),B=np.array([[0.3]]))
    lifted=lift_zero_order_hold(model,3)
    x0=np.array([0.4])
    u=np.array([0.2])

    x=x0.copy()
    for _ in range(3):
        x=model.A@x+model.B@u

    np.testing.assert_allclose(
        lifted.macro_model.A@x0+lifted.macro_model.B@u,
        x,
        atol=1e-12,
    )


def test_same_continuous_dynamics_at_20hz_and_100hz_become_identity_at_common_horizon():
    source=_exact_scalar_discretization(a=2.0,b=1.5,dt=0.05)
    target=_exact_scalar_discretization(a=2.0,b=1.5,dt=0.01)

    cert=synthesize_multirate_transport(
        source,target,
        source_control_period=0.05,target_control_period=0.01,
        source_hold_steps=1,target_hold_steps=5,
    )

    assert cert.transport.exact
    np.testing.assert_allclose(cert.transport.state_gain,[[0.0]],atol=1e-11)
    np.testing.assert_allclose(cert.transport.action_gain,[[1.0]],atol=1e-11)
    assert cert.source_macro_seconds==pytest.approx(0.05)
    assert cert.target_macro_seconds==pytest.approx(0.05)


def test_multirate_lift_synthesizes_gain_change_at_same_wall_clock_horizon():
    source=_exact_scalar_discretization(a=2.0,b=1.5,dt=0.05)
    target=_exact_scalar_discretization(a=2.0,b=0.75,dt=0.01)

    cert=synthesize_multirate_transport(
        source,target,
        source_control_period=0.05,target_control_period=0.01,
        source_hold_steps=2,target_hold_steps=10,
    )

    assert cert.transport.exact
    np.testing.assert_allclose(cert.transport.action_gain,[[2.0]],atol=1e-10)
    np.testing.assert_allclose(cert.transport.state_gain,[[0.0]],atol=1e-10)


def test_different_wall_clock_horizons_are_rejected():
    model=LinearClosedLoopModel(A=np.array([[0.9]]),B=np.array([[0.1]]))
    with pytest.raises(ValueError,match="different physical horizons"):
        synthesize_multirate_transport(
            model,model,
            source_control_period=0.05,target_control_period=0.01,
            source_hold_steps=1,target_hold_steps=4,
        )


def test_random_micro_models_match_direct_repetition_after_lifting():
    rng=np.random.default_rng(20261006)
    for _ in range(100):
        A=rng.normal(scale=0.15,size=(3,3))
        B=rng.normal(scale=0.2,size=(3,2))
        model=LinearClosedLoopModel(A=A,B=B)
        h=int(rng.integers(1,7))
        lifted=lift_zero_order_hold(model,h)
        x=rng.normal(size=3)
        x0=x.copy()
        u=rng.normal(size=2)
        for _ in range(h):
            x=A@x+B@u
        macro=lifted.macro_model.A@x0+lifted.macro_model.B@u
        np.testing.assert_allclose(macro,x,atol=1e-11,rtol=1e-11)

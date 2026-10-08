import numpy as np

from research.eprc.directional_jet import (
    evaluate_directional_jet_prediction,
    fit_centered_derivative_jet,
)


def test_smooth_cubic_response_is_recovered_and_predicts_finer_scale():
    j0=np.array([[1.0,0.2],[0.0,-0.5]])
    c=np.array([[0.8,-0.1],[0.3,0.4]])
    hc,hf,hr=0.5,0.25,0.125
    dc=j0+c*hc**2
    df=j0+c*hf**2
    dr=j0+c*hr**2

    out=evaluate_directional_jet_prediction(
        coarse_map=dc,fine_map=df,finer_map=dr,
        coarse_radius=hc,fine_radius=hf,finer_radius=hr,
    )
    assert np.allclose(out.linear_limit_map,j0)
    assert np.allclose(out.cubic_scale_coefficient,c)
    assert out.jet_prediction_error < 1e-12
    assert out.first_order_prediction_error > 0
    assert out.supports_model_order_upgrade


def test_linear_response_has_zero_cubic_coefficient():
    j=np.array([[1.0,2.0],[3.0,4.0]])
    j0,c=fit_centered_derivative_jet(
        j,j,coarse_radius=0.5,fine_radius=0.25
    )
    assert np.allclose(j0,j)
    assert np.allclose(c,0.0)


def test_non_smooth_scale_behavior_fails_model_order_upgrade():
    coarse=np.array([[1.0,0.0],[0.0,1.0]])
    fine=np.array([[2.0,0.0],[0.0,0.5]])
    # Deliberately violates the h^2 scale law inferred from coarse/fine.
    finer=np.array([[-1.0,0.0],[0.0,3.0]])

    out=evaluate_directional_jet_prediction(
        coarse_map=coarse,fine_map=fine,finer_map=finer,
        coarse_radius=0.5,fine_radius=0.25,finer_radius=0.125,
    )
    assert not out.supports_model_order_upgrade
    assert out.improvement_ratio > 0.5


def test_richer_model_is_not_authorized_by_tiny_absolute_gain_alone():
    coarse=np.array([[1.0]])
    fine=np.array([[1.000001]])
    finer=np.array([[1.000003]])
    out=evaluate_directional_jet_prediction(
        coarse_map=coarse,fine_map=fine,finer_map=finer,
        coarse_radius=0.5,fine_radius=0.25,finer_radius=0.125,
        required_improvement_ratio=0.5,
        max_relative_jet_error=1e-8,
    )
    assert not out.supports_model_order_upgrade

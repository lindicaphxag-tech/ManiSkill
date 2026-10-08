from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class DirectionalJetDiagnostic:
    linear_limit_map: np.ndarray
    cubic_scale_coefficient: np.ndarray
    predicted_finer_map: np.ndarray
    first_order_prediction_error: float
    jet_prediction_error: float
    improvement_ratio: float
    relative_jet_error: float
    supports_model_order_upgrade: bool


def fit_centered_derivative_jet(
    coarse_map: np.ndarray,
    fine_map: np.ndarray,
    *,
    coarse_radius: float,
    fine_radius: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Fit D(h) = J0 + C h^2 from two centered-derivative scales.

    For a smooth scalar/vector response along a fixed probe direction,

        D(h) = [f(+h)-f(-h)]/(2h)
             = J0 + (T/6) h^2 + O(h^4).

    C therefore represents T/6.  The routine works elementwise on a matrix of
    centered directional derivatives.
    """

    dc=np.asarray(coarse_map,dtype=float)
    df=np.asarray(fine_map,dtype=float)
    if dc.shape != df.shape:
        raise ValueError("coarse/fine map shapes differ")
    hc=float(coarse_radius)
    hf=float(fine_radius)
    if hc <= 0 or hf <= 0 or np.isclose(hc,hf):
        raise ValueError("probe radii must be positive and distinct")

    denom=hc*hc-hf*hf
    c=(dc-df)/denom
    j0=df-c*(hf*hf)
    return j0,c


def predict_centered_derivative(
    linear_limit_map: np.ndarray,
    cubic_scale_coefficient: np.ndarray,
    *,
    radius: float,
) -> np.ndarray:
    h=float(radius)
    if h < 0:
        raise ValueError("radius must be nonnegative")
    return (
        np.asarray(linear_limit_map,dtype=float)
        + np.asarray(cubic_scale_coefficient,dtype=float)*(h*h)
    )


def evaluate_directional_jet_prediction(
    *,
    coarse_map: np.ndarray,
    fine_map: np.ndarray,
    finer_map: np.ndarray,
    coarse_radius: float,
    fine_radius: float,
    finer_radius: float,
    required_improvement_ratio: float=0.5,
    max_relative_jet_error: float=0.25,
    atol: float=1e-12,
) -> DirectionalJetDiagnostic:
    """Out-of-fit scale prediction gate for a richer local response model.

    Coarse and fine maps fit the two-parameter odd local jet. The finer map is
    held out from fitting and acts as the model-order adjudication target.

    The richer model is authorized only if it both:
      1. cuts the first-order scale-prediction error by the frozen ratio; and
      2. has small error relative to the held-out finer map magnitude.
    """

    if not 0 <= required_improvement_ratio < 1:
        raise ValueError("required_improvement_ratio must lie in [0,1)")
    if max_relative_jet_error < 0:
        raise ValueError("max_relative_jet_error must be nonnegative")

    j0,c=fit_centered_derivative_jet(
        coarse_map,fine_map,
        coarse_radius=coarse_radius,
        fine_radius=fine_radius,
    )
    pred=predict_centered_derivative(j0,c,radius=finer_radius)
    actual=np.asarray(finer_map,dtype=float)
    fine=np.asarray(fine_map,dtype=float)
    if actual.shape != pred.shape:
        raise ValueError("finer map shape differs")

    first=float(np.linalg.norm(fine-actual,ord=2))
    jet=float(np.linalg.norm(pred-actual,ord=2))
    ratio=jet/max(first,atol)
    relative=jet/max(float(np.linalg.norm(actual,ord=2)),atol)
    supports=bool(
        ratio <= required_improvement_ratio
        and relative <= max_relative_jet_error
    )

    return DirectionalJetDiagnostic(
        linear_limit_map=j0,
        cubic_scale_coefficient=c,
        predicted_finer_map=pred,
        first_order_prediction_error=first,
        jet_prediction_error=jet,
        improvement_ratio=float(ratio),
        relative_jet_error=float(relative),
        supports_model_order_upgrade=supports,
    )

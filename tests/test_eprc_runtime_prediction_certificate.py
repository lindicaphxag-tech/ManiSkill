import numpy as np

from research.eprc.runtime_prediction_certificate import (
    RuntimePredictionCertificate,
    RuntimePredictionDecision,
    certify_runtime_prediction,
    verify_runtime_prediction_certificate,
)


def test_small_disturbance_is_certified_without_fresh_oracle():
    g = np.array([[2.0, 0.0], [0.0, 1.0]])
    xi = np.array([0.2, -0.1])

    cert = certify_runtime_prediction(
        g,
        xi,
        epsilon_g=0.05,
        certified_radius=0.5,
        residual_tolerance=0.02,
    )

    assert cert.decision is RuntimePredictionDecision.CERTIFIED_PREDICTION
    assert np.allclose(cert.predicted_correction, [0.4, -0.1])
    assert cert.worst_case_prediction_error <= 0.02
    assert verify_runtime_prediction_certificate(g, certificate=cert)


def test_high_model_uncertainty_stays_inconclusive():
    g = np.eye(2)
    cert = certify_runtime_prediction(
        g,
        np.array([0.4, 0.0]),
        epsilon_g=0.2,
        certified_radius=0.5,
        residual_tolerance=0.05,
    )

    assert cert.decision is RuntimePredictionDecision.INCONCLUSIVE
    assert cert.worst_case_prediction_error > cert.residual_tolerance
    assert verify_runtime_prediction_certificate(g, certificate=cert)


def test_request_outside_certified_radius_is_refused_before_execution():
    g = np.eye(2)
    cert = certify_runtime_prediction(
        g,
        np.array([0.6, 0.0]),
        epsilon_g=0.0,
        certified_radius=0.5,
        residual_tolerance=1.0,
    )

    assert cert.decision is RuntimePredictionDecision.REFUSE_OUTSIDE_CERTIFIED_REGION
    assert np.isinf(cert.worst_case_prediction_error)
    assert verify_runtime_prediction_certificate(g, certificate=cert)


def test_zero_uncertainty_certifies_any_in_radius_request_at_zero_tolerance():
    g = np.array([[1.0, 2.0]])
    cert = certify_runtime_prediction(
        g,
        np.array([0.1, -0.2]),
        epsilon_g=0.0,
        certified_radius=0.5,
        residual_tolerance=0.0,
    )

    assert cert.decision is RuntimePredictionDecision.CERTIFIED_PREDICTION
    assert cert.worst_case_prediction_error == 0.0


def test_forged_predicted_correction_is_rejected():
    g = np.eye(2)
    valid = certify_runtime_prediction(
        g,
        np.array([0.1, 0.0]),
        epsilon_g=0.1,
        certified_radius=0.5,
        residual_tolerance=0.02,
    )
    forged = RuntimePredictionCertificate(
        decision=valid.decision,
        support_delta=valid.support_delta,
        predicted_correction=valid.predicted_correction + np.array([1.0, 0.0]),
        support_norm=valid.support_norm,
        certified_radius=valid.certified_radius,
        epsilon_g=valid.epsilon_g,
        worst_case_prediction_error=valid.worst_case_prediction_error,
        residual_tolerance=valid.residual_tolerance,
        reason=valid.reason,
    )

    assert not verify_runtime_prediction_certificate(g, certificate=forged)

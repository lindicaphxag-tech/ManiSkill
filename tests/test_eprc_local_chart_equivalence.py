import numpy as np
import pytest

from research.eprc.local_chart_equivalence import (
    local_chart_certificate,
    nonlinear_reparameterized_jacobians,
    verify_local_diffeomorphism_invariance,
)
from research.eprc.contract_signature import semantically_lift_jacobian


def test_dec_is_invariant_under_nonlinear_local_action_diffeomorphism():
    j_phys = np.array([[1.0, 0.2], [0.3, 1.7], [0.0, 0.5]])
    a0 = np.array([0.4, -0.7, 0.2])
    beta = np.array([0.5, 1.1, 0.2])

    j_chart, lift, cert = nonlinear_reparameterized_jacobians(
        j_phys, a0, beta
    )
    assert cert.locally_invertible
    assert not np.allclose(j_chart, j_phys)
    assert np.allclose(semantically_lift_jacobian(j_chart, lift), j_phys)
    assert verify_local_diffeomorphism_invariance(j_phys, a0, beta)


def test_near_singular_chart_is_rejected_as_unstable_coordinate_change():
    j = np.diag([1.0, 1e-12, 2.0])
    cert = local_chart_certificate(j)
    assert not cert.locally_invertible
    assert cert.condition_number > 1e8


def test_non_square_mapping_is_not_an_action_coordinate_chart():
    with pytest.raises(ValueError, match="square"):
        local_chart_certificate(np.ones((3, 2)))

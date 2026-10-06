import numpy as np

from research.eprc.authority_loss import (
    SaturatingController,
    authority_aware_equivalence,
    authority_certificate,
    lifted_contract_under_controller,
)


def _controller():
    return SaturatingController(
        scale=np.array([1.0, 2.0, 0.5]),
        lower=np.array([-1.0, -1.0, -1.0]),
        upper=np.array([1.0, 1.0, 1.0]),
    )


def test_interior_chart_has_full_local_authority():
    c = _controller()
    cert = authority_certificate(c, np.array([0.2, 0.1, -0.4]))
    assert cert.admissible_for_exact_transport
    assert cert.local_rank == 3
    assert cert.lost_directions == 0


def test_saturation_creates_rank_loss_and_rejects_exact_equivalence():
    c = _controller()

    saturated_action = np.array([0.2, 0.8, -0.4])
    cert = authority_certificate(c, saturated_action)

    assert not cert.admissible_for_exact_transport
    assert cert.local_rank == 2
    assert cert.lost_directions == 1

    j_support = np.eye(3)
    ok, reason = authority_aware_equivalence(
        j_support,
        c,
        np.array([0.2, 0.1, -0.4]),
        j_support,
        c,
        saturated_action,
    )
    assert not ok
    assert "target controller has lost local physical authority" in reason


def test_same_raw_action_support_jacobian_can_have_different_physical_contract_after_saturation():
    c = _controller()
    j_support = np.array(
        [
            [1.0, 0.0],
            [0.0, 1.0],
            [0.4, 0.2],
        ]
    )

    phys_interior, sig_interior, cert_interior = lifted_contract_under_controller(
        j_support, c, np.array([0.2, 0.1, -0.4])
    )
    phys_sat, sig_sat, cert_sat = lifted_contract_under_controller(
        j_support, c, np.array([0.2, 0.8, -0.4])
    )

    assert cert_interior.local_rank == 3
    assert cert_sat.local_rank == 2
    assert not np.allclose(phys_interior, phys_sat)
    assert sig_interior.rank != sig_sat.rank


def test_equivalent_interior_reparameterizations_pass():
    a = SaturatingController(
        scale=np.array([1.0, 1.0]),
        lower=np.array([-10.0, -10.0]),
        upper=np.array([10.0, 10.0]),
    )
    b = SaturatingController(
        scale=np.array([2.0, 2.0]),
        lower=np.array([-10.0, -10.0]),
        upper=np.array([10.0, 10.0]),
    )

    j_a = np.array([[1.0, 0.2], [0.3, 0.7]])
    j_b = 0.5 * j_a

    ok, reason = authority_aware_equivalence(
        j_a,
        a,
        np.array([0.1, -0.2]),
        j_b,
        b,
        np.array([0.05, -0.1]),
    )
    assert ok
    assert reason == "locally equivalent and full-authority"

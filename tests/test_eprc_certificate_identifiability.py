import numpy as np

from research.eprc.certificate_directed_probing import ProbeInformation
from research.eprc.certificate_identifiability import (
    optimal_continuous_directional_probe,
    repeated_probe_count_for_directional_radius,
    repair_identifiability_budget,
)


def test_closed_form_probe_beats_random_unit_directions():
    rng = np.random.default_rng(7)
    V = np.array([[8.0, 1.2, 0.3], [1.2, 2.5, 0.4], [0.3, 0.4, 0.8]])
    info = ProbeInformation(V, beta=0.2)
    x = np.array([0.2, 1.0, -0.4])

    optimum = optimal_continuous_directional_probe(info, x)

    best_random_after = float("inf")
    for _ in range(10000):
        z = rng.normal(size=3)
        z /= np.linalg.norm(z)
        next_info = info.update(z)
        after = float(x @ np.linalg.solve(next_info.information, x))
        best_random_after = min(best_random_after, after)

    assert np.isclose(np.linalg.norm(optimum.probe), 1.0)
    assert optimum.variance_after <= best_random_after + 2e-4
    assert optimum.variance_reduction > 0


def test_repeated_probe_count_is_minimal_for_fixed_direction():
    info = ProbeInformation(np.eye(2), beta=0.2)
    x = np.array([1.0, 0.0])
    z = np.array([1.0, 0.0])

    # beta / sqrt(1 + k) <= 0.1 => k >= 3.
    k = repeated_probe_count_for_directional_radius(
        info, x, z, target_radius=0.1
    )
    assert k == 3


def test_single_probe_direction_can_be_insufficient_forever():
    info = ProbeInformation(np.eye(2), beta=0.2)
    x = np.array([1.0, 1.0])
    z = np.array([1.0, 0.0])

    # Repeating e1 cannot remove uncertainty in e2.
    k = repeated_probe_count_for_directional_radius(
        info, x, z, target_radius=0.05
    )
    assert k is None


def test_identifiability_budget_reports_policy_evaluation_cost():
    info = ProbeInformation(np.eye(2), beta=0.2)
    budget = repair_identifiability_budget(
        info,
        np.array([1.0, 0.0]),
        nominal_residual=0.0,
        residual_tolerance=0.1,
    )

    assert budget.repeated_probe_count_estimate == 3
    assert budget.symmetric_policy_evaluations_estimate == 6
    assert budget.information_only


def test_negative_nominal_slack_cannot_be_fixed_by_more_information_alone():
    info = ProbeInformation(np.eye(2), beta=0.2)
    budget = repair_identifiability_budget(
        info,
        np.array([1.0, 0.0]),
        nominal_residual=0.2,
        residual_tolerance=0.1,
    )

    assert budget.uncertainty_slack < 0
    assert budget.repeated_probe_count_estimate is None

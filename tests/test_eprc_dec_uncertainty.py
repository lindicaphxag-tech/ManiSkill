import numpy as np

from research.eprc.dec_uncertainty import (
    ComparisonDecision,
    compare_dec_with_uncertainty,
    estimate_dec_uncertainty,
)


def _replicates(base, seed, noise, n=12):
    rng = np.random.default_rng(seed)
    return np.stack([base + rng.normal(scale=noise, size=base.shape) for _ in range(n)])


def test_repeated_same_contract_can_be_certified_equivalent():
    base = np.array([[1.0, 0.2], [0.3, 0.8], [0.1, -0.1]])
    a = estimate_dec_uncertainty(_replicates(base, 1, 5e-4), max_q95_radius=0.02)
    b = estimate_dec_uncertainty(_replicates(base, 2, 5e-4), max_q95_radius=0.02)

    out = compare_dec_with_uncertainty(
        a, b, equivalence_tolerance=0.03, difference_tolerance=0.10
    )
    assert a.stable and b.stable
    assert out.decision is ComparisonDecision.EQUIVALENT


def test_physical_gain_change_is_certified_different():
    base = np.array([[1.0, 0.2], [0.3, 0.8], [0.1, -0.1]])
    a = estimate_dec_uncertainty(_replicates(base, 3, 5e-4), max_q95_radius=0.03)
    b = estimate_dec_uncertainty(_replicates(2.0 * base, 4, 5e-4), max_q95_radius=0.03)

    out = compare_dec_with_uncertainty(
        a, b, equivalence_tolerance=0.05, difference_tolerance=0.30
    )
    assert out.decision is ComparisonDecision.DIFFERENT
    assert out.lower_separation_bound >= 0.30


def test_high_probe_variance_forces_inconclusive_not_false_difference():
    base = np.array([[1.0, 0.2], [0.3, 0.8]])
    a = estimate_dec_uncertainty(_replicates(base, 5, 0.25), max_q95_radius=0.10)
    b = estimate_dec_uncertainty(_replicates(base, 6, 0.25), max_q95_radius=0.10)

    out = compare_dec_with_uncertainty(a, b)
    assert not a.stable or not b.stable
    assert out.decision is ComparisonDecision.INCONCLUSIVE


def test_too_few_replicates_never_certifies_contract():
    base = np.eye(2)
    a = estimate_dec_uncertainty(_replicates(base, 7, 1e-5, n=3), min_replicates=5)
    b = estimate_dec_uncertainty(_replicates(base, 8, 1e-5, n=3), min_replicates=5)
    out = compare_dec_with_uncertainty(a, b)
    assert not a.stable and not b.stable
    assert out.decision is ComparisonDecision.INCONCLUSIVE
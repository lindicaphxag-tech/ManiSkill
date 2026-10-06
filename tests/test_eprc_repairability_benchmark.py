from research.eprc.repairability_benchmark import (
    RepairabilityTrial,
    baseline_auc,
    paired_bootstrap_auc_delta,
    summarize_zero_threshold,
)


def _trials():
    # Frozen toy evidence: CRG sign exactly separates recoverable and failed
    # rollouts, while perturbation magnitude alone is intentionally ambiguous.
    return [
        RepairabilityTrial(0.6, True, 0.3, 0.8, 0.2),
        RepairabilityTrial(0.3, True, 0.8, 0.6, 0.4),
        RepairabilityTrial(0.1, True, 0.5, 0.4, 0.8),
        RepairabilityTrial(-0.1, False, 0.2, 0.7, 0.2),
        RepairabilityTrial(-0.4, False, 0.9, 0.5, 0.7),
        RepairabilityTrial(-0.8, False, 0.4, 0.2, 0.3),
    ]


def test_zero_threshold_is_not_tuned_from_outcomes():
    metrics = summarize_zero_threshold(_trials())
    assert metrics.coverage == 0.5
    assert metrics.false_accept_rate == 0.0
    assert metrics.accepted_success_rate == 1.0
    assert metrics.auc == 1.0


def test_benchmark_exposes_simple_baselines():
    scores = baseline_auc(_trials())
    assert scores["crg_margin"] == 1.0
    assert scores["negative_perturbation_norm"] < 1.0


def test_paired_bootstrap_runs_without_external_ml_dependencies():
    mean, lo, hi = paired_bootstrap_auc_delta(
        _trials(),
        baseline="negative_perturbation_norm",
        samples=200,
        seed=17,
    )
    assert mean > 0
    assert lo <= mean <= hi
